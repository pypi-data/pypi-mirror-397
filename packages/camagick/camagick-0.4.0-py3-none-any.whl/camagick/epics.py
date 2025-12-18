from camagick.reader import Receiver

from caproto.sync import client as ca_client
from caproto.asyncio.client import Context
from caproto import CaprotoTimeoutError
import numpy as np
import xarray as xr

import asyncio

import logging
logger = logging.getLogger(__name__)


def extract_data(response, pvName=None, others=None, auto_xarray=False):
    '''
    Extracts "useful" data out of a CAproto response telegram.
    '''
    pass


class EpicsReceiver(Receiver):
    ## Base class for all EPICS-based receivers -- essentially
    ## just manages the CAproto client context and data extraction
    async def init(self):
        await super().init()
        self.ctx = self.ctx = Context()
        self.data_pvs = await self.ctx.get_pvs(*[v for v in self._tokens])
        

    async def shutdown(self):
        await self.ctx.disconnect()


    def unpack(self, token, dataobj, context):
        
        auto_xarray=False
        others=context
        pvName=token
        response=dataobj

        if response is None:
            return None

        if others is None:
            others = {}

        # Channel types can be: CHAR, DOUBLE, FLOAT, STRING, ENUM, LONG, INT.
        # The intention is to get an automatic useful native Python data type,
        # scalar or array. This means different things for different data
        # types.
        # In addition, we implement some heuristics to decorate waveforms
        # (== arrays) if our obscure array markers are present (shape, dimensions,
        # axis scaling -- to be documented ;-) )

        if response.data_type in (ca_client.ChannelType.STRING,):
            return response.data[0].decode('utf-8')

        elif response.data_type in (ca_client.ChannelType.DOUBLE,
                                    ca_client.ChannelType.FLOAT,
                                    ca_client.ChannelType.LONG,
                                    ca_client.ChannelType.INT,
                                    ca_client.ChannelType.ENUM):

            if len(response.data) == 1:
                return response.data[0]

            if not pvName or not pvName.endswith("_SIGNAL"):
                return response.data

            # If we have an array and it ends on _SIGNAL, we also try to
            # load _OFFSET and _DELTA for intrinsic scaling information
            o_name = pvName.replace("_SIGNAL", "_OFFSET")
            d_name = pvName.replace("_SIGNAL", "_DELTA")

            if o_name in others:
                offs = extract_data(others.get(o_name, 0))
            else:
                offs = 0

            if d_name in others:
                dlta = extract_data(others.get(d_name, 1))
            else:
                dlta = 1

            try:
                axis = offs+np.array(range(len(response.data)))*dlta
            except TypeError as e:
                # This happens when not all the data (e.g. `dlta` or `offs`
                # has arrived yet.
                axis = np.array([np.nan] * len(response.data))

            if auto_xarray:
                return DataArray(data=response.data, dims=["x"], coords=[axis])
            else:
                return response.data

        elif response.data_type in (ca_client.ChannelType.CHAR,):
            # This is a string -- return as such (ACHTUNG, this will break
            # "everything is a numpy array" data philosophy -- but we _want_
            # this. There's no other way to discern a uint8 from a string
            # later on.
            p = response.data
            s = bytes(p).decode('utf-8')
            return s

        elif response.data_type in (ca_client.ChannelType.STRING,):
            # This is a string -- return as such (ACHTUNG, this will break
            # "everything is a numpy array" data philosophy -- but we _want_
            # this. There's no other way to discern a uint8 from a string
            # later on.
            #print('have', repsonse.data)
            return response.data


        # else: how to handle ENUM / CHAR?

        else:
            logger.warning ("Unhandled data type: %r" % (response.data_type,))
            return response.data[0]

    
class SubscriptionReceiver(EpicsReceiver):
    ## Async subscription-based implementation of "Receiver"
    async def init(self):
        await super().init()        
        self._ca_subscriptions = {}
        for d in self.data_pvs:
            logger.info(f'msg="Subscribing" pv="{d.name}"')
            self._ca_subscriptions[d.name] = d.subscribe()
            self._ca_subscriptions[d.name].add_callback(self._process_subscription)
        logger.debug(f'msg="CA client contex" ctx={self.ctx}')

    def _process_subscription(self, sub, data):
        self._process(sub.pv.name, data)


class PollingReceiver(EpicsReceiver):
    ## Polling-based receiver; essentially just installs a polling task
    ## with a (fairly slow) period and repeatedly tries to capture
    ## the PV values by calling .read().
    
    async def init(self):
        await super().init()
        poll_period = 0.2 # seconds
        self._poll_task = asyncio.create_task(self._poll(poll_period))

    async def _poll(self, poll_period):
        async def _read_and_process(pvobj, oldval):
            self._process(pvobj.name, (await pvobj.read()))
        self._old_data = None

        try:
            while True:
                data = await asyncio.gather(
                    asyncio.sleep(poll_period),
                    *[ _read_and_process(pv, None) for pv in self.data_pvs ],
                    return_exceptions = False
                )
                self._old_data = data
        except CaprotoTimeoutError as e:
            logger.warning(f'msg="CAproto timeout" detail="{e}"')
            pass
        except Exception as e:
            logger.error(f'msg="CA polling failed, detail follows" error={type(e)}')
            logger.error(e)
            logger.error(traceback.format_exc())
            raise
        finally:
            pass


    async def shutdown(self):
        try:
            self._poll_task.cancel()
            await self._poll_task
        except asyncio.CancelledError: pass
