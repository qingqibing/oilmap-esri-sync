#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file logical_or_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for logical_or of gridded data. 
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.operators.sum_reduce')

@util.coroutine
def sum(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in count operation. Received type: %s' % type(result))

    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (temp,reduction_metadata) = (yield)
        
        numpy.logical_or(temp,result, out=result)