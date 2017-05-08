#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file probability_reduce.py
@date 03/11/13
@description Reduce a map of values into a set of arrays by variable name and file/run number
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

logger = logging.getLogger('pystoch.map_reduce_ops.stats_reduce')

@util.coroutine
def stats_reduce(array_map, file_names):


    flist = []
    for fnum in xrange(file_names.shape[0]):
        fname = ''.join(file_names[fnum,:].tolist())
        fname = fname[:fname.index('\n')]
        flist.append(fname)


    #count = 0
    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (value_map,reduction_metadata) = (yield)
        
        fnum = flist.index(reduction_metadata[FILE_NAME])
        
        for name, value in value_map.iteritems():
            
            array_map[name][fnum] = value
            