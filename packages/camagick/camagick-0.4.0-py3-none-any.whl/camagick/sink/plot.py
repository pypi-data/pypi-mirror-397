from camagick.processor import ProcessorBase, SinkBase

import multiprocessing as mp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, RectangleSelector
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import LogNorm
import numpy as np

import traceback, os

from camagick.executor import QuitApplication

import time, math, logging, concurrent, asyncio, pickle, asteval

logger = logging.getLogger(__name__)


def resample_array(name, data, num_bins):
    if len(data) > num_bins:
        slices = np.linspace(0, data.shape[0], num_bins+1, True).astype(int)
        counts = np.diff(slices)
        mean = np.add.reduceat(data, slices[:-1]) / counts
        return mean
    else:
        return data

class MatplotlibDisplay:
    '''
    Stupidly simple class that uses Matplotlib to visualize numpy arrays.
    '''
    def __init__(self, rows=None, cols=None, flip_lr=True, transpose=False, sample_max=2056):
        self.flip_lr = flip_lr
        self.transpose = transpose
        self._rows = rows
        self._cols = cols
        self._sample_max = sample_max
        self.figure = plt.figure()
        self.bgcolor = (0.3, 0.3, 0.3)
        self.figure.patch.set_facecolor(self.bgcolor)

        self.panels = {}  # plots (lines/image) objects, per-tag
        self.axesobj = {} # actual axes objects _per_ _layout_
        self.axes = {}    # axes (subplot) references, organized per-tag
        self.markers = {} # marker objects (rect etc) to display, per-tag

        self.set_expected(1)
        

    def _default_rows_cols(self, num_panels, rows, cols):
        if rows is not None:
            self._rows = rows

        if cols is not None:
            self._cols = cols

        rows = self._rows if self._rows is not None else \
            int(math.ceil(math.sqrt(num_panels)))

        if rows == 0:
            logger.error(f'msg="ACHTUNG, no data"')
            rows += 1
        
        cols = self._cols if cols is not None else \
            int(math.ceil(num_panels/rows))

        return rows, cols


    def init_display(self, panel_name, pspec=None):
        '''
        Initializes display for a specific panel.
        Uses panel specification as in `pspec`, if not `None`.
        `num_total` is only used to determine a default subplot layout/configuration
        in the absence of a `pspec.sub` specification.
        '''

        num_total = self._expected_num_panels
        
        # default layout, if pspec doesn't exist
        rows, cols = self._default_rows_cols(num_total, None, None)

        # how many panels did we already place
        have = len(self.axes)

        #logger.info(f'geometry={rows}x{cols} displays={self.panelNames}')
        #self.axes = { k: self.figure.add_subplot(rows, cols, i+1) \
        #              for i,k in enumerate(self.panelNames) }

        if pspec is not None and pspec.subplot is not None:
            # Need to transform the subspec to the 3-digit-integer format,
            # because we want to use this as a key in .axesobj.
            if hasattr(pspec.subplot.sub, '__len__'):
                r, c, h = pspec.subplot.sub
                subspec = r*100+c*10+h
            else:
                subspec = pspec.subplot.sub
            subargs = pspec.subplot.kwargs
        else:
            subspec = rows*100 + cols*10 + have+1
            subargs = {}

        if subspec not in self.axesobj:
            ax = self.axesobj[subspec] = self.figure.add_subplot(subspec, **subargs)
            ax.set_facecolor(self.bgcolor)            
            logger.error(f'msg="Adding subplot" panel={panel_name} spec={subspec} sub={ax}')
        else:
            ax = self.axesobj[subspec]
            #ax.legend()

        if panel_name not in self.axes:
            logger.error(f'msg="Attibuting panel to subplot" panel={panel_name} sub={ax}')
            self.axes[panel_name] = ax

        self.markers[ax] = {}
        
            #RectangleSelector(
            #    ax, useblit=True,
            #    interactive=True,
            #    props={'fill': False},
            #    drag_from_anywhere=True,
            #    #ignore_event_outside=True
            #)
        #self.last_update = {k:time.time() for k in self.panelNames }


    def _plot_norm_2d(self, img):
        mi = img.min()
        ma = img.max()
        return mi, ma, LogNorm(vmin=mi if mi > 0 else 1e-5,
                               vmax=ma if ma > 0 and ma > mi else 1)
    
        
        
    def _plot_2d(self, name, data, *kw):
        ax = self.axes[name]
        ax.set_title(name)

        if self.flip_lr:
            img = data[:,::-1]
        else:
            img = data

        if self.transpose:
            img = np.transpose(img)
        
        self._2d_norm = self._plot_norm_2d(img)

        return ax.imshow(img, norm=self._2d_norm[2], *kw)


    def _plot_1d(self, name, data, *kw):        
        d = resample_array(name, data, self._sample_max)

        if len(data) != len(d):
            logger.info(f'tag={name} msg="Data was rebinned" '
                        f'full_shape={data.shape} '
                        f'bin_shape={d.shape}')        
        
        ax = self.axes[name]
        x = ax.plot(d,*kw)

        # Update legend to include all plots for this panel
        labels = [k for k,v in filter(lambda x: x[1] == ax, self.axes.items()) ]
        ax.legend(labels)

        return x


    def _update_1d(self, name, data, pspec=None, **kw):

        if (pspec is not None):
            axis = pspec.axes[0]
        else:
            axis = np.array(range(len(data)))
        
        if len(data) > self._sample_max:
            d = resample_array(name, data, self._sample_max)
        else:
            d = data

        x2 = resample_array(name, axis, self._sample_max)

        line = self.panels[name][0]
        line.set_xdata(x2)
        line.set_ydata(d)
        line.axes.relim()
        line.axes.autoscale_view()


    def _update_2d(self, name, data, pspec=None, **kw):
        if self.flip_lr:
            img = data[:,::-1]
        else:
            img = data

        if self.transpose:
            img = np.transpose(img)

        self.panels[name].set_data(img)

        if pspec.cursor is not None:
            for ci,cursor in enumerate(pspec.cursor):
                patch = self.markers[name].get(ci)                
                if len(cursor) > 2:
                    if patch is None:
                        patch = self.markers[name][ci] = \
                            Rectangle((cursor[0], cursor[1]), cursor[2], cursor[3],
                                      edgecolor='red', facecolor=(0.0, 0.0, 0.0, 0.0))
                        self.axes[name].add_patch(patch)
                    else:
                        patch.set(x=cursor[0], y=cursor[1], width=cursor[2], height=cursor[3])
                else:
                    if patch is None:
                        patch = self.markers[name][ci] = Circle((cursor[0], cursor[1]))
                    else:
                        patch.set(center=(cursor[0], cursor[1]))


        mi, ma, norm = self._plot_norm_2d(img)
        if mi < self._2d_norm[0] or ma > self._2d_norm[1]:
            logger.info(f'msg="Updating norm" tag="{name}" vmin="{mi}", vmax="{ma}"')
            self.panels[name].set_norm(norm)
            self._2d_norm = (mi, ma, norm)


    def _panel_for_data(self, name, data, pspec):
        '''
        Returns the panel for data set `name`
        '''
        dims = len(data.shape)
        plot_func = getattr(self, f"_plot_{dims}d")
        plot_kwargs = {
            1: {},
            2: {}
        }[dims]

        if data is None:
            data = np.ndarray([2]*dims)

        pan = self.panels.get(name)
        if pan is None:
            try:
                self.init_display(name, pspec)
                self.panels[name] = pan = plot_func(name, data, **plot_kwargs)
            except Exception as e:
                traceback.print_exc(e)
                raise

        return plt


    def set_expected(self, num_panels):
        self._expected_num_panels = num_panels
        

    def update(self, panel, data=None, pspec=None):
        
        if data is None:
            return
        
        try:
            dims = len(data.shape)
            ax = self._panel_for_data(panel, data, pspec)
        except KeyError:
            logging.error("%s: no such display panel" % panel)
            return

        getattr(self, f"_update_{dims}d")(panel, data, pspec)
        self.figure.canvas.draw_idle()


    def run(self):
        plt.show()


def _send(pipe, msg):
    try:
        pipe.send(msg)
    except Exception as e:
        logger.error(f'msg="Failed to send data to plotter" detail="{e}"')
        raise
        
        
class ProcessPlotter:

    def __init__(self, panels=None):
        self._panspec = panels if panels is not None else {}
        self.send_pipe, self.recv_pipe = mp.Pipe()
        self.plotter_process = mp.Process(
            target=self, args=(self.recv_pipe,), daemon=True
        )
        self.plotter_process.start()


    async def plot(self, data, context):
        '''
        Asynchronously sends data to the plotting (matplotlib) process.
        '''
        with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(pool, _send, self.send_pipe,
                                        {'data': data, 'ctx': context})
                await task
            except Exception as e:
                logger.error(f'msg="Plotter data feed" error="{e}"')
                raise

    
    def terminate(self):
        self.send_pipe.send(None)
        plt.close('all')

        
    def _eval_plotspec(self, ps, data, ctx):
        # Plotspec string: [pos, {kwargs}], xaxis, yaxis, cursorAt, cursorSize]
        from asteval import Interpreter
        inter = Interpreter()
        inter.symtable.update(ctx)
        from collections import namedtuple
        param_names = ['subplot', 'axes', 'cursor']
        PlotSpec = namedtuple('plotspec', param_names)
        have_args = inter(ps, raise_errors=True)
        if have_args is None:
            return None
        have = list(have_args)
        need =  [None]*(len(param_names)-len(have_args))

        interm = list(have_args) + need
        pspec = PlotSpec(*interm)

        # Complete missing parts.

        # Subplot must either be an integer 'xyz', a tuple (x,y,z),
        # or a tuple and a dictionary (subplot, {kwargs})
        if type(pspec.subplot) == int \
           or ((hasattr(pspec.subplot, "__len__") and len(pspec.subplot)) == 3) \
           or (pspec.subplot is None):
            pspec_subplot = namedtuple('PlotSpecSubplot', ['sub', 'kwargs'])(pspec.subplot, {})
        elif len(pspec.subplot) != 2:
            raise RuntimeError(f'Bad subplot spec \'{pspec.subplot}\'')
        else:
            if type(pspec.subplot[0]) == int:
                pspec_subplot = namedtuple('PlotSpecSubplot', ['sub', 'kwargs'])(pspec.subplot[0], pspec.subplot[1])
            else:
                pspec_subplot = namedtuple('PlotSpecSubplot', ['sub', 'kwargs'])(*pspec.subplot)


        is_standalone = lambda x: len(data.shape)==1 \
            and (x is not None) and \
            (hasattr(x, "__len__") and len(x)) != 1

        # Axes spec is one item per axis -- except if the dimension
        if is_standalone(pspec.axes):
            pspec_axes = (pspec.axes,)
        else:
            pspec_axes = pspec.axes
        # As a convenience, if the axis data is a (a,b) tuple, we
        # interpret it as a (delta, offset) specification and expand
        # to a linspace
        if pspec_axes is not None:
            pspec_axes = tuple([
                (np.linspace(start=p[0], stop=p[0]+p[1]*ds, num=ds) \
                 if p is not None and hasattr(p, "__len__") and len(p) == 2 \
                 else p) \
                for p,ds in zip(pspec_axes,data.shape)
            ])

        # Cursor is a tuple/list with item per dimension (or a single item
        # if the dimenson is 1).
        # Each item is, in turn, either a single- or a double-number.
        # Single-number is the position of the cursor (spanning from left
        # to right), double-number is position and size.
        if is_standalone(pspec.cursor):
            pspec_cursor = (pspec.cursor,)
        else:
            pspec_cursor = pspec.cursor
        if pspec_cursor is not None:
            pspec_cursor = tuple([
                    (p,0) if len(p)==0 else tuple([x for x in p]) \
                    for p in pspec_cursor
            ])

        return PlotSpec(pspec_subplot, pspec_axes, pspec_cursor)

    
    def callback(self):
        data = {}
        m0 = time.time()
        while self.pipe.poll():
            incoming = self.pipe.recv()
            if incoming is None or incoming['data'] is None:
                self.terminate()
                return False
            
            data = incoming['data']
            context = incoming['ctx'] or {}

        if len(data) > 0:
            self.display.set_expected(len(data))

        for dname,dvalues in data.items():
            try:
                pspec = self._panspec.get(dname, '')
                ps = self._eval_plotspec(pspec, dvalues, context)
                #logger.debug(f'tag={dname} subplot={ps.subplot} axes={ps.axes} cursor={ps.cursor}"')
            except Exception as e:
                logger.error(f'msg="Bad plot spec" tag=dname from=\'pspec\' reason="{e}"')
    
            
        #if (not self.display.is_initialized):            
        #    if len(data)>0:
        #        self.display.init_display(*[k for k in data.keys()])

        for name,val in data.items():
            self.display.update(name, val, ps)
            
        return True


    def __call__(self, pipe=None, period=0.03):
        self.pipe = pipe or self.recv_pipe
        self.display = MatplotlibDisplay(transpose=True, flip_lr=False)
        intr = int(period*1000)
        logger.info(f'msg="Matplotlib subprocess" refresh={intr}ms pid={os.getpid()}')
        timer = self.display.figure.canvas.new_timer(interval=intr)
        timer.add_callback(self.callback)
        timer.start()
        
        self.display.run()


class Processor(SinkBase):
    '''
    Plots data as lines (1D arrays) or images (2D arrays).
    '''
    
    def __init__(self, **spec):
        '''
        Args:
            **spec: Dictionary with data tags as keys, and plot spec
              strings as values. The plot spec strings are specified
              as a string `pos,spec,xaxis,yaxis`
              the following meaning:
        
              - pos: a subplot position spec compatible with the arguments
                passed to a call to `matplotlib.pyplot.subplot()`, i.e.
                "221" or "[2,2,1]".

              - spec: keyword arguments for subplot spec, to be passed
                to `matplotlib.pyplot.subplot()`, enclosed in `dict()`
                brackets `{}`, e.g.:  `{"polar":True}` or `{"sharex":False}`

              - xaxis: exxpression to calculate the X axis
                
        '''

        # Another tentative format: `"[sub[:x[:y]]][#fx[:fy][,tx[:ty]]"`
        self._panspec = spec


    async def startup(self):
        self.plotter = ProcessPlotter(self._panspec)


    async def shutdown(self):
        self.plotter.terminate()

    
    async def __call__(self, data=None, context=None):
        try:
            await self.plotter.plot(data, context)

            #return { k:data[k] for k in \
            #         filter(lambda x: x not in data, data.keys()) }
            
        except BrokenPipeError:
            logger.info(f'msg="Display closed by user"')
            raise QuitApplication(f'msg="Display closed by user"')
