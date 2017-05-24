#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file min_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for the minimum values of the array. 
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.min_reduce')

@util.coroutine
def min_reduce(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in min reduce. Received type: %s' % type(result))


    #count = 0
    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (temp,reduction_metadata) = (yield)
        
        numpy.minimum(temp, result, out=result)
        
        