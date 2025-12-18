from camagick.processor import ProcessorBase
import numpy as np
import logging
from asteval import Interpreter

logger = logging.getLogger(__name__)

def _parse_slice(s, inter=None):

    if inter is None:
        inter = Interpreter()
    
    parts = s.split(':')
    
    if len(parts)==1:
        return None if len(parts[0])==0 \
            else inter(parts[0], raise_errors=True)

    if len(parts) > 0:
        sparam = [int(inter(p, raise_errors=True) if p not in ("None", None) else None) \
                  if len(p)>0 else None for p in parts]
        return slice(*sparam)


class Processor(ProcessorBase):    
    '''
    Slices, a.k.a. selects, a subset of each dataset.
    '''

    def __init__(self, *rois):
        '''
        Iteratively selects regions of interests from data.

        Args:
            *rois: each unnamed parameter is either a `slice()` object (if used in API
              mode), a string of the format "start:stop:step" or "spec", or `None`.
              If it's a string, a slice object is constructed from the parsed string
              values using `asteval.Interpreter()` from the `lmfit` people -- meaning
              that you actually have access to a number of arithmetical operations
              and the context data as sy,bols. If it's `None`, it will be treated
              like `numpy`'s `None` or `newaxis`: a new axis is produced.
        
              As a convenience, if there's only one dimensional specification (i.e.
              one parameter), which is a string and which contains "," it treated
              as a complete specification of the form "dim,dim,dim".
        '''

        self._roi_spec = rois


    def _parse_roi(self, rois, ctx):

        # Splitting of single-parameter specification
        if len(rois)==1 and isinstance(rois[0], str):
            r = rois[0].split(',')
            rois = r

        # ROR params, one for each dimension.
        roi_params = []

        inter = Interpreter()
        inter.symtable.update(ctx)
        
        for r in rois:
            if isinstance(r, str):
                try:
                    o = inter(r, show_errors=False, raise_errors=True)
                    obj = int(o) if o not in (None,) else o
                except SyntaxError:
                    try:
                        obj = _parse_slice(r, inter)
                    except SyntaxError as e:
                        logger.error(f'msg="Error parsing ROI dimension" spec="{r}" '
                                     f'detail="{e}"')
                        raise
                roi_params.append(obj)
            elif hasattr(r, "__len__"):
                raise RuntimeError(f"Don't know how to deal with {r}")
            else:
                roi_params.append(r)

        return roi_params        
    
    async def __call__(self, data=None, context=None):
        ''' Executes the ROI selection. Context is ignored. '''
        try:
            roi_params = self._parse_roi(self._roi_spec, context or {})
            return {
                key:val[*roi_params] for key,val in data.items()
            }
        except Exception as e:
            logger.error(f"roi={self._roi_spec}")
            raise
