from camagick.processor import ProcessorBase

import logging

from asteval import Interpreter

class Processor(ProcessorBase):
    '''
    Executes arithmetic computations on the input data.
    '''    
    def __init__(self, expr):
        '''
        Args:
            expr: Python-esque expression to calculate. "{}" is being
              substituted for the input data, any other symbol for the
              corresponding context field. The expression is evaluated
              using lmfit's `asteval` module.
        '''
        self._expr = expr.format('__input_data__')
        self._intrp = Interpreter()
        
    
    async def startup(self):
        pass

    async def shutdown(self):
        pass
    
    async def __call__(self, data=None, context=None):
        intrp = self._intrp
        intrp.symtable.update(**context)
        ret = {}
        for k,v in data.items():
            intrp.symtable['__input_data__'] = v
            ret[k] = intrp(self._expr)
        return ret
