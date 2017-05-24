#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for the maximum values of the array. 
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.max_reduce')

@util.coroutine
def max_reduce(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in max reduce. Received type: %s' % type(result))


    # figure out why value to use to reset the temp array passed from the map function
    #try:
    #    reset_val = numpy.iinfo(result.dtype).min
    #except ValueError:
    #    reset_val = result.dtype.type('-inf')

    #count = 0
    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (temp,reduction_metadata) = (yield)
        
        numpy.maximum(temp, result, out=result)
