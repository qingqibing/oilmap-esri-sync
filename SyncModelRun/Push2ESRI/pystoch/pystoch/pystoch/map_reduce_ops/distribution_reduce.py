#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file distribution_reduce.py
@date 03/11/13
@description A module containing a coroutine reduce for the distribution of the array. 
'''
import numpy
import logging
from pystoch.datatypes import DT
from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.map_reduce_ops.distribution_reduce')

@util.coroutine
def distribution_reduce(result,bin_coefficient, nsims):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in distribution_reduce. Received type: %s' % type(result))

    dims = result.shape
    
    if not len(dims) == 3:
        raise PyStochOperatorError('invalid result argument in distribution_reduce operation. Expected array of rank 3, got rank %s' % len(dims))
    
    grid_dims = dims[1:3]
    nbins = dims[0]
    
    bin_index = numpy.zeros(grid_dims,dtype=DT.INT32)

    xi, yi = numpy.indices(grid_dims)

    try:
        #count = 0
        while True:
    
            # Take temp as input from an operation and sum it with the aggregated result array
            (temp,reduction_metadata) = (yield)
        
            numpy.floor_divide(numpy.sqrt(temp), bin_coefficient, out=bin_index)
            bin_index[bin_index >= nbins] = nbins - 1
            # Make sure the bin index value never causes an index error
                                
            result[bin_index, xi, yi] += 1
            
    except GeneratorExit:
        
        #print 'Calling cumsum!'
        # Offset by one because we want >= to the bin value
        result[1:,...] = result[:-1,...].cumsum(axis=0)

        # Need to use the ufunc interface to specify out!
        #result = nsims - result # effectively flip the direction of the cumsum
        numpy.add(nsims, -1 * result, out=result)
        result[0,...] = nsims
