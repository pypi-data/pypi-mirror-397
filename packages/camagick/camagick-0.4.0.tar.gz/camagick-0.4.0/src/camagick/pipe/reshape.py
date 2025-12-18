
from camagick.processor import ProcessorBase

from asteval import Interpreter

def populate_argparser(parser):
    pass

class Processor(ProcessorBase):
    '''
    Changes the array shape of the input data.
    '''
    
    def __init__(self, *dims, shape=None, **kw):
        '''
        Args:
            dims: List of shape specification, one per dimension. If the dimension
              specification are strings, they are parsed using `asteval.Interpreter`
              from the `lmfit` people, i.e. may contain a limited set of mathematical
              functions, constants, and data context tags as symbols.

            shape: Alternatively, if there are no dims, a shape can be supplied
              as a whole. As string, this is also parsed using `asteval.Interperter()`.
        
        '''
        super().__init__(**kw)
        if len(dims)==0:
            self.shape = shape
        else:
            self.shape = dims

    async def __call__(self, data=None, context=None):
        #shape = (context.get(f'{k}_shape', self.shape) for k in data) \
        #    if context is not None else self.shape

        if self.shape is None:
            raise RuntimeError(f'msg="{self.__class__.__name__} requires a shape '
                               f'for {k} got none"')
        
        
        inter = Interpreter()
        inter.symtable.update(context or {})
        
        if isinstance(self.shape, str):
            shape = inter(self.shape)
            if shape is None:
                raise RuntimeError(f'msg="Cannot parse shape" spec="{self.shape}"')
        else:
            shape = tuple([
                (inter(s, raise_errors=True) \
                 if isinstance(s, str) else s)  for s in self.shape
            ])
            for s1,s2 in zip(shape, self.shape):
                if s1 is None:
                    raise RuntimeError(f'msg="Don\'t understand shape" '
                                       f'spec="{self.shape}" '
                                       f'result="{shape}"')
        
        return { k:v.reshape(shape) for k,v in data.items() }
