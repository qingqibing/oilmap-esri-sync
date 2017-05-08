#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file run_stats_reduce.py
@date 03/11/13
@description A module containing a coroutine to produce per run statistics
'''
import numpy
import logging
from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import * 

logger = logging.getLogger('pystoch.map_reduce_ops.area_exceeding_by_threshold_stats_reduce')

@util.coroutine
def area_exceeding_by_threshold_stats_reduce(result, thresholds, file_names, scalar):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in "area exceeding by threshold stats reduce". Received type: %s' % type(result))

    if not hasattr(thresholds, '__iter__'):
        raise PyStochOperatorError('Invalid thresholds argument in "area exceeding by threshold stats reduce". Received type: %s' % type(thresholds))
    

    flist = []
    for fnum in xrange(file_names.shape[0]):
        fname = ''.join(file_names[fnum,:].tolist())
        fname = fname[:fname.index('\n')]
        flist.append(fname)


    #count = 0
    while True:
    
        # Take temp as input from an operation and sum it with the aggregated result array
        (map_array,reduction_metadata) = (yield)
        
        fnum = flist.index(reduction_metadata[FILE_NAME])
        
        #@todo replace with nditer
        for i in xrange(thresholds.shape[0]):
            area_oiled = scalar * numpy.sum(map_array >= thresholds[i])
        
            result[i,fnum] = area_oiled
        
        
        
        
        
        