#!/usr/bin/python3

import logging, time, math, random, asyncio

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast
from asteval import Interpreter

logger = logging.getLogger(__name__)

class Processor(SourceBase):
    '''
    Produces data from scratch by evaluating mathematical expressions.

    The eval expressions are parsed by the `asteval` module , providing
    a useful subset of the Python language focused on mathematical
    expresssions, mostly in the form of `numpy` functions and basic
    arithmetic operations (linspace, sin, ones, random, ...).

    This is a more powerful and easy-to-use data source than the
    "scratch" module, and actually in almost every way superior (except
    for the fact that `asteval` doesn't have a random number generator).
    But with great power comes great responsibility, as the underlying
    `asteval` module might allow for expressions that don't strictly
    result in array data -- which would break your CAspy flow.
    '''

    def __init__(self, **tags):
        '''
        Args:
            **tags: map of data name -> eval expression to generate
              data from.
        '''

        self._tags = tags
        self._inter = Interpreter()
        super().__init__()


    async def __call__(self, data=None, context=None):
        d = {}

        self._inter.symtable.update(context)

        for tag,code in self._tags.items():
            ev = self._inter(code)
            if ev is None:
                raise RuntimeError(f'msg="Asteval error" detail="{self._inter.error}" '
                                   f'tag="{tag}"')
                
            d[tag] = ev

        return d
