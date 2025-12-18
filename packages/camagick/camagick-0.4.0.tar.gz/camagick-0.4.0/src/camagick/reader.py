#!/usr/bin/python3

import asyncio, time, logging

import numpy as np

import copy, traceback

from xarray import DataArray
from functools import partial
from contextlib import suppress

logger = logging.getLogger(__name__)

class PvRetry(RuntimeError):
    '''
    Raised by GuidedPvReader when the PVs are not yet ready / guide does
    not yet signal readiness for signal readout.
    '''
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)


class DataInbox:
    ## Base class to manage various types of readout strategies.
    ## All have in common that data is (possibly) kept in a cache
    ## until a specific readout condition is met.
    ##
    ## Waiting is implemented by means of an async lock.
    
    def __init__(self, dwell=0.2):
        # This is where we cache the data.
        # We use full PV names as keys.
        # The payload ("data hold") is:
        # {
        #    'tag': short,
        #    'data': [list of datapoints],
        #    'ts': [timestamps]
        # }
        self._incoming_data = {}
        self._dwell_time = dwell


    def _have_complete_set(self):
        ## Checkes whether a complete data set (as expected) is available.
        have = [ k for k in self._incoming_data.keys() ]
        for x in self._expected:
            if x not in have:
                return False # don't have a full set, NO READOUT
        return True


    def _trim_backlog(self, num_max=1):
        ## Removes all but `num_max` data entries from every PV's backlog.
        ## This MUST BE CALLED if they don't reset the backlog altogether.
        for pvname,hold in self._incoming_data.items():
            if len(hold['data']) > num_max:
                del hold['data'][:num_max]
                del hold['ts'][:num_max]


    def _reset_backlog(self):
        self._incoming_data = {}


    async def create(self, expected):
        '''
        Called when within the designated asyncio loop.

        Expected to perform initialization steps that can only be
        performed from within the loop.

        Args:
            expected: List of expected full PV set. Used for various decision-making
              procedures (see also ._have_complete_set()).
        '''
        self._expected = expected


    def ingest(self, pvname, tag, response):
        '''
        Called when incoming data is arriving.

        Args:
            pvname: full PV name
            tag: short name (not used? may be "none"?)
            response: CAproto response object; contains `.data`
        '''
        hold = self._incoming_data.setdefault(
            pvname,
            {
                'tag': tag,
                'data': [],
                'ts': []
            }
        )
        hold['data'].append(response)
        hold['ts'].append(time.time())


    async def readout(self, timeout=None):
        '''
        Returns data, if this is the case according to readout policy.

        Might block until readout is due.
        '''
        if self._dwell_time > 0.0:
            await asyncio.sleep(self._dwell_time)

        # return only the last item of each key (not the whole incoming stack)
        return {
            k:{'data': v['data'][-1], 'ts': v['ts'][-1]} \
            for k,v in self._incoming_data.items()
        }


class ContinuousDataInbox(DataInbox):
    '''
    Continuous and uncoditional EPICS readout.
    No waiting for (new) data, no resetting of the readout
    buffer.
    '''
    def ingest(self, pvname, tag, response):
        super().ingest(pvname, tag, response)
        self._trim_backlog()
    

class LockingDataInbox(DataInbox):
    ## Base class that locks the ._readout_lock generally (at the
    ## beginning, and usually after readout), and only unlocks it
    ## when a new dataset is available.
    ## Essentially everything except ContinuousDataInbox depends
    ## on this.


    def _release_lock(self):
        with suppress(RuntimeError):
            self._readout_lock.release()


    async def _readout_lock_acquire(self, timeout=None):
        if timeout is None:
            await self._readout_lock.acquire()
        else:
            await asyncio.wait_for(self._readout_lock.acquire(), timeout)


    def can_readout(self):
        ## This is checked on every ingest. Default behavior for
        ## most modes is "yes, we can read out". But some specific
        ## modes -- i.e. "thorough" and possibly "guided" -- will
        ## overwrite this to implement a more sophisticated method.
        return True

    async def create(self, expected):
        self._readout_lock = asyncio.Lock()
        await super().create(expected)
        await self._readout_lock_acquire()

    def ingest(self, pvname, tag, response):
        super().ingest(pvname, tag, response)
        self._trim_backlog()
        if self.can_readout():
            self._release_lock()

    async def readout(self, timeout=None):
        await self._readout_lock_acquire(timeout)
        d = await super().readout()
        return d


class GuidedDataInbox(LockingDataInbox):

    def __init__(self, guide_dict, **kwargs):
        super().__init__(**kwargs)

        if guide_dict is None:
            guide_dict = {}
        
        # This is a dictionary guide-pv <-> test lambda
        self.guides = {}
        self.guides.update({
            k:v if hasattr(v, "__call__") else lambda k,x: x == v \
            for k,v in guide_dict.items()
        })

        # map EPICS name -> current True/False  evaluation of the guide signal.
        # Note that this is _not_ the guide trigger evaluation, i.e. the condition
        # of whether the waiting for this guide is finished and we're ready to
        # return data! For the latter to be fulfilled, the corresponding
        # guide_eval needs to be changing from 'False' to 'True'!
        self.guide_evals = { k:None for k in self.guides }


    async def create(self, expected):
        await super().create(expected)
        self.guide_trigger = {
            k:False for k in self.guides.keys()
        }


    def _guide_changed(self, pv_name, response):
        '''
        Called when a guide value changes. Checks if all guide conditions
        are met, and possibly calls the incoming hooks.
        '''

        d = response.data if len(response.data) > 1 else response.data[0]
        eval_result = self.guides[pv_name](pv_name,d)

        logger.info(f'msg="Guide update" pv={pv_name} value="{d}" type={type(d)}')

        if eval_result:
            if not self.guide_evals[pv_name]:
                # on eval switch False -> True: trigger!
                self.guide_trigger[pv_name] = True
        else:
            # eval False always kills the trigger
            self.guide_trigger[pv_name] = False
            
        self.guide_evals[pv_name] = eval_result


    def can_readout(self):

        # check whether we can do a data readout (all triggers must be True)
        guides_ok = all(self.guide_trigger.values())

        if not guides_ok:
            return False

        return True


    def _invalidate_guide(self):
        for k in self.guide_trigger:
            self.guide_trigger[k] = False


    def ingest(self, pvname, tag, response):
        if (pvname in self.guides):
            #logger.info(f'msg="Guide changed" name={pv_name} value={d} '
            #            f'condition_ok={eval_result} '
            #            f'activated_ok={self.guide_evals[pv_name]} '
            #            f'all_ok={guides_ok}')
            self._guide_changed(pvname, response)
        return super().ingest(pvname, tag, response)


    async def readout(self, timeout=None):
        data = await super().readout()
        self._invalidate_guide()
        not_guide = lambda x: x[0] not in self.guides
        return { k:v for k,v in filter(not_guide, data.items()) }


class SloppyDataInbox(LockingDataInbox):
    '''
    Unlocks the readout as soon as _any_ data is available.
    Don't reset the readout (meaning that subsequent ingest
    operations will eventually return a full set of data,
    but possibly from different points in time).
    '''
    pass

        
class HastyDataInbox(SloppyDataInbox):
    '''
    Same as SloppyDataInbox (i.e. returns data on _any_ ingest),
    but reset the backlog on retrieve. This means that there
    will almost never be a full dataset available (unless 'dwell'
    is sufficiently large).
    '''
    async def readout(self, timeout=None):
        d = await super().readout(timeout)
        self._reset_backlog()
        return d


class ThoroughDataInbox(SloppyDataInbox):
    '''
    Returns the data only when a full dataset is available.
    Resets the backlog afterwards, so that a _new_ full dataset
    is required for new readout.
    '''

    def can_readout(self):
        return self._have_complete_set()


class ClusteredDataInbox(DataInbox):
    # See also: https://web.stanford.edu/class/cs345a/slides/12-clustering.pdf
    pass


class Receiver:
    ## Used internally by SubscriptionReader / PollingReader to actually
    ## receive data (separation of reading mechanism and data retrieving
    ## policy -- this is the "mechanism" part.)
    ##
    ## Some readers will be subscription-based, others polling-based,
    ## and the protocols (EPICS vs Tango vs ???) will differ. The API
    ## must match all of them. Therefore the API is centered around
    ## initial connect/disconnect, regular health check, and channel
    ## subscription management. It's up to derrived classes to
    ## (re)implement whatever else functionality they need.

    def __init__(self, *tokens):
        self._tokens = tokens
        self._local_subscriptions = { t:[] for t in tokens }


    async def init(self):
        # Needs to be called exactly once before use, after init.
        pass

    
    async def shutdown(self):
        # Needs to be called exactly once, after last use, for cleanup.
        pass


    def unpack(self, token, dataobj, context):
        '''
        Expected to extract actual, useful data payload from `dataobj`.
        The underlying assumption is that the receiver class API usually
        deals with incoming "data objects" which are _different_ from the
        actual data payload, and need to be unpacked before they become
        useful.

        Since each Receiver class is mechanism-dependent, the unpack
        mechanism is also individual.

        Args:
          token: The token for this data package
          dataobj: The data object package
          context: Dicitonary {token:obj, ...} for other, possibly
            related data packages. The Receiver class does not manage
            data package collections (only access), so it does not
            have access to this information; this is why it must
            be specified as an extra parameter (if available).
        '''
        raise RuntimeError('not implemented')
        
    
    def subscribe(self, token, proc):
        '''
        Subscribes callable `proc` to receive data of `token`.

        Args:
          token: This is the string-like key of the data channel.
            (For EPICS, this is usually the full PV name.)
            Note that this _can_ but usually _isn't_, the CAmagick
            internal "tag" of the data. This is because the Receiver
            system is several layers below where "tag" is even
            introduced, and it's up to the upper layers to make the
            connection between a receiving channel token and a data
            "tag".

          proc: A callable with the signature `proc(token, dataobj)`,
            where `dataobj` contains the data object, possibly in an
            implementation-dependent form (e.g. a CAproto response
            object).
        '''
        token_list = self._local_subscriptions[token]
        if proc not in token_list:
            token_list.append(proc)


    def unsubscribe(self, token, proc):
        '''
        Unsubscribes `proc` from receiving news about data of "token".
        '''
        self._local_subscriptions[token].remove(proc)


    def _process(self, token, data):
        # This is for internal use (by derrived classes) only,
        # meant to distribute `data` to "token" callables.
        try:
            for proc in self._local_subscriptions[token]:
                proc(token, data)
        except Exception as e:
            logger.error(f'msg="Oops" reason="{e}"')
            logger.error(traceback.format_exc(e))
            raise
    

class AsyncReader:
    '''
    Observes a "guide" variable to determine when a specific EPICS PV signal is
    available, then collects the PV signal (which can come in a list of other PVs).    

    To get as efficient as possible, this implementation actually
    uses subscriptions to the guide variables, and reacts on
    those. Calling .value() will wait asynchronously for the guide
    conditions to be fulflled, and this will be fairly efficient.

    But the most efficient way will be to subscribe a data
    processing callback using .subscribe(), which will be called
    only when all guide conditions are fulfilled and all data
    is available.
    '''

    def __init__(self,
                 *pvs: list,
                 guide_dict: dict = None,
                 mode: str = '',
                 dwell: float = None,
                 receiver: type = None):
        '''
        Initialises the reader.

        Args:
        
            pvs: The PVs to read out. (If not specified here, they can
              be specified later -- FIXME: really?)
              All PVs to be monitored are being subscribed to, and the newest
              version of incoming data is stored without backlog (!), until
              the guide conditions are all met.
        
            guide_dict: A dicitonary of guide variable(s) as keys, and a
              corresponding value to use, OR a callable of the signature
              `proc(key, value)`.
              The "guide condition" is "activated" for each individual guide
              when the callable returns `True` for the first time; the "guide
              condition" is "met" when _all_ guides have been activated.
                      
              When the guide condition is met, the current values of the PVs
              specified in `pvs` are returned as readout, and a new readout
              is only possible after a new reactivation. Note that for a new
              reactivation, a *de*activation of the individuals is necessary
              first, and that a *de*activation is *not* done automatically.
              Rather, it is expected that the guides deactivate themselves
              by taking on a value that doesn't meet the activation condition.

              Thus, guides are required to "blink" at least once for every
              data readout.
        
            mode: Readout mode, one of "hasty", "sloppy", "continuous",
              "thorough", "guided" or "clustered". See documentation of
              `camagick.source.epics` for a detailed explantion on the
              readout mode.

            dwell: Time (in seconds) to wait after guide condition is met
              until data is collected. ACHTUNG: the wait is performed only
              for `.wait_for_data()`, not when using data callbacks!

            receiver: Receiver class to use for incoming data.
        '''

        self.pvs = [v for v in pvs]
        
        for v in (guide_dict if guide_dict is not None else {}):
            if v not in pvs:
                self.pvs.append(v)
                continue
            logger.warning(f'msg="PV explicitly requested as data _and_ guide will '
                           f'not be returned as data" name={v}')

        if receiver is not None:
            self.ReceiverClass = receiver
        else:
            from camagick.epics import SubscriptionReceiver, PollingReceiver
            self.ReceiverClass = SubscriptionReceiver


        if mode is None or len(mode) == 0:
            if guide_dict is None or len(guide_dict)==0:
                mode = 'sloppy'
            else:
                mode = 'guided'
            if dwell is None:
                dwell = 0.1
            logger.debug(f'msg="Readout mode autodetected"')
    
        logger.info(f'msg="Readout configuration" '
                    f'mode="{mode}" '
                    f'receiver={self.ReceiverClass} '
                    f'dwell={dwell}')

        # inbox needs to be initialized in a running asyncio loop.
        self.inbox = {
            'hasty':      partial(HastyDataInbox, dwell=dwell),
            'sloppy':     partial(SloppyDataInbox, dwell=dwell),
            'continuous': partial(ContinuousDataInbox, dwell=dwell),
            'thorough':   partial(ThoroughDataInbox, dwell=dwell),
            'guided':     partial(GuidedDataInbox, guide_dict=guide_dict, dwell=dwell),
            'clustered':  partial(ClusteredDataInbox, dwell=0.0)
        }[mode]()

        logger.info(f'msg="Have inbox" class="{self.inbox.__class__}"')

        self._ref_cnt = 0


    async def __aenter__(self):
        if self._ref_cnt == 0:
            await self.connect()
        self._ref_cnt += 1
        return self

    async def __aexit__(self, *a, **kw):
        if self._ref_cnt > 0:
            self._ref_cnt -= 1
        if self._ref_cnt == 0:
            await self.disconnect()

    async def connect(self):
        self._receiver = self.ReceiverClass(*self.pvs)
        await self._receiver.init()
        for pv in self.pvs:
            self._receiver.subscribe(pv, self._data_changed)
        await self.inbox.create(expected = [pv for pv in self.pvs])

    async def disconnect(self):
        await self._receiver.shutdown()
        del self._receiver

    def _data_changed(self, pvname, response):
        self.inbox.ingest(pvname, None, response)        

    
    async def _get_incoming(self):
        '''
        Returns the currently incoming data (from subscriptions).
        We're using this instead of directly reading out the `._incoming_data`
        dictionary because, optinally, we're doing some mangling
        in `.extract_data()` that may or may not interfere with
        the data keys.
        '''

        # need to work on a copy here because _incoming_data might change
        # while we're waiting for new incoming data.
        tmp = await self.inbox.readout()
        return {
            k:self._receiver.unpack(k, v['data'], context=tmp) \
            for k,v in tmp.items() \
            if (v is not None)
        }


    async def wait_for_incoming(self):
        '''
        Waits for incoming data. Returns only once per read-cycle
        (i.e. "marks" itself as called, so that repeated calls to
        this function sleep until new data is actually available,
        according to the ._readout_mode strategy).
        '''
        d = await self._get_incoming()
        return d


# Legacy name
GuidedAsyncReader = AsyncReader
