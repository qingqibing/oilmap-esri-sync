#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file sum_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for summing gridded data. 
'''
import numpy
import logging
#import numexpr
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.sum_reduce')

@util.coroutine
def sum_reduce(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in count operation. Received type: %s' % type(result))

    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (temp,reduction_metadata) = (yield)
        
        numpy.add(temp,result, out=result)
        #numexpr.evaluate('result + temp', out=result)
        
