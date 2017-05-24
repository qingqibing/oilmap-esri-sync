#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file probability_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce probability of a gridded result exceeding a specified value
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.probability_reduce')

@util.coroutine
def probability_reduce(result,exceeds_val):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in probability_reduce. Received type: %s' % type(result))


    #count = 0
    while True:
        logger.info('Deprecated!')
    
        (temp,reduction_metadata) = (yield)
        
        result[temp > exceeds_val] += 1
        
                