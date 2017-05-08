#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oil_volume.py
@date 03/11/13
@description A module containing a function for summing the oil volume in a grid cell
'''
import numpy
import logging

from pystoch import util
from pystoch.keywords import *
from pystoch.datatypes import DT

logger = logging.getLogger('pystoch.operators.oil_volume_distribution_op')


@util.coroutine
def oil_volume_distribution_op(result, bin_size):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in oil_volume operation. Received type: %s' % type(result))
    
    dims = result.shape
    
    if not len(dims) == 3:
        raise PyStochOperatorError('invalid result argument in oil_volume operation. Expected array of rank 3, got rank %s' % len(dims))
    
    grid_dims = dims[1:3]
    nbins = dims[0]
    
    oil_volume_array = numpy.zeros(grid_dims,dtype=DT.PRECISION)
    bin_index = numpy.zeros(grid_dims,dtype=DT.INT32)

    xi, yi = numpy.indices(grid_dims)


    try:

        while True:
            block, index_position, weight, metadata = (yield)
        
            weighted_oil_volume = block['mass']/block['density'] / weight # * metadata[TIME][DTIME]
        
            blen = index_position.shape[0]
            for i in xrange(blen):        
                oil_volume_array[tuple(index_position[i,:])] += weighted_oil_volume[i]
                                      
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep

                numpy.floor_divide(oil_volume_array, bin_size, out=bin_index)
                bin_index[bin_index >= nbins] = nbins - 1
                # Make sure the bin index value never causes an index error
                                
                result[bin_index, xi, yi] += 1
                                
                oil_volume_array[:] = 0.0
                   
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
    
        raise