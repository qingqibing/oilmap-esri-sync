#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file clean_array.py
@date 03/11/13
@description A module containing a coroutine whose sole purpose is to reset the array values
'''
import numpy
import logging
from pystoch.datatypes import DT
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.clean_array')

@util.coroutine
def clean_array():

    try:
        #count = 0
        while True:
            # Take temp as input from an operation and sum it with the aggregated result array
            (temp, reset_value) = (yield)
        
            if isinstance(temp, numpy.ndarray):
                temp[:] = reset_value
            elif isinstance(temp, dict) and isinstance(reset_value, dict):
                temp.update(reset_value)
            else:
                PyStochOperatorError("Received bad arguments to clean_array: temp - %s; reset_value - %s" % (temp, reset_value))
            
    except GeneratorExit:
        
        pass
        # do nothing to clean up at the end...
