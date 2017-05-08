#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file exceed_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for counting the number of times a grid cell exceeds a value. 
'''
import numpy
import logging
from pystoch.datatypes import DT
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.exceed_reduce')

@util.coroutine
def exceed_reduce(result,exceedance_value):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in exceed_reduce. Received type: %s' % type(result))

    try:
        #count = 0
        while True:
    
            # Take temp as input from an operation and sum it with the aggregated result array
            (temp,reduction_metadata) = (yield)
        
            result[temp > exceedance_value] +=1
            
            
    except GeneratorExit:
        
        pass
        # do nothing to clean up at the end...
