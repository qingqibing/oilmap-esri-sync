#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file thickest_spillet_distribution_op.py
@date 03/11/13
@description Calculates the distribution of oil thickness based on the thickest spillet in each cell of each time step
'''
import numpy
import logging

from pystoch import util
from pystoch.keywords import *

from pystoch.datatypes import DT
from pystoch import config

logger = logging.getLogger('pystoch.operators.thickest_spillet_distribution_op')


@util.coroutine
def thickest_spillet_distribution_op(result, bin_coefficient):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in thickest_spillet_distribution_op operation. Received type: %s' % type(result))

    dims = result.shape
    
    if not len(dims) == 3:
        raise PyStochOperatorError('invalid result argument in thickest_spillet_distribution_op operation. Expected array of rank 3, got rank %s' % len(dims))
    
    grid_dims = dims[1:3]
    nbins = dims[0]
    
    spillet_thickness_array = numpy.zeros(grid_dims,dtype=DT.PRECISION)
    bin_index = numpy.zeros(grid_dims,dtype=DT.INT32)

    xi, yi = numpy.indices(grid_dims)

    try:
        
        while True:
            block, index_position, weight, metadata = (yield)
        
            # Calculate oil volume seconds!
            #try:
            #    radius = block['radius']
            #except ValueError:
            #    #radius = 2. * numpy.sqrt(2. * spillet_dispersion * block['lifetime'])
            #    raise PyStochOperatorError('This spillet type has no radius information so spillet thickness can not be computed.')

            radius = block['radius']
                
                
            spillet_thickness = block['mass']/block['density'] / (numpy.pi * radius**2)
        
        
            blen = index_position.shape[0]
            for i in xrange(blen): 
            
                # Can't sum - need to take the max value over all time step...       
                spillet_thickness_array[tuple(index_position[i,:])] = max(spillet_thickness_array[tuple(index_position[i,:])], spillet_thickness[i])
                #print weighted_oil_volume[i]/cell_area
                   
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep
                
                # Take the square root of the thickness to make the distribution more uniform
                numpy.floor_divide(numpy.sqrt(spillet_thickness_array), bin_coefficient, out=bin_index)
                #if (numpy.max(bin_index) >= nbins):
                #    logger.warn('Expected maximum oil thickness exceeded!')
                bin_index[bin_index >= nbins] = nbins - 1
                # Make sure the bin index value never causes an index error
                                
                result[bin_index, xi, yi] += 1
                                
                spillet_thickness_array[:] = 0.0
                
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        logger.info('cell_area:\n%s' % cell_area)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
    
        raise
