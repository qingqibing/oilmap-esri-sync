#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file uniform_oil_thickness_op.py
@date 03/11/13
@description A module containing a function for calculating the distribution of uniform the oil thickness in a grid cell
'''
import numpy
import logging

from pystoch import util
from pystoch.keywords import *

from pystoch.datatypes import DT

logger = logging.getLogger('pystoch.operators.uniform_oil_thickness_distribution_op')


@util.coroutine
def uniform_oil_thickness_distribution_op(result, cell_area, bin_size):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in uniform_oil_thickness_distribution_op operation. Received type: %s' % type(result))

    dims = result.shape
    
    if not len(dims) == 3:
        raise PyStochOperatorError('invalid result argument in uniform_oil_thickness_distribution_op operation. Expected array of rank 3, got rank %s' % len(dims))
    
    grid_dims = dims[1:3]
    nbins = dims[0]
    
    oil_thickness_array = numpy.zeros(grid_dims,dtype=DT.PRECISION)
    bin_index = numpy.zeros(grid_dims,dtype=DT.INT32)

    xi, yi = numpy.indices(grid_dims)


    try:
        
        while True:
            block, index_position, weight, metadata = (yield)
        
            #logger.info('block shape: %s' % list(block.shape))
            #logger.info('block: %s' % block)
            #logger.info('index_pos shape: %s' % list(index_position.shape))
            #logger.info('weight shape: %s' % list(weight.shape))
            #logger.info('weight: %s' % weight)

            # Calculate oil volume seconds!
            weighted_oil_volume = block['mass']/block['density'] / weight / cell_area
        
        
            blen = index_position.shape[0]
            for i in xrange(blen): 
            
                # Can't sum - need to take the max value over all time step...       
                oil_thickness_array[tuple(index_position[i,:])] += weighted_oil_volume[i]
                #print weighted_oil_volume[i]/cell_area
                   
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep
                
                # Take the square root of the thickness to make the distribution more uniform
                numpy.floor_divide(numpy.sqrt(oil_thickness_array), bin_size, out=bin_index)
                #if (numpy.max(bin_index) >= nbins):
                #    logger.warn('Expected maximum oil thickness exceeded!')
                bin_index[bin_index >= nbins] = nbins - 1
                # Make sure the bin index value never causes an index error
                                
                result[bin_index, xi, yi] += 1
                                
                oil_thickness_array[:] = 0.0
                
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        logger.info('cell_area:\n%s' % cell_area)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
    
        raise
