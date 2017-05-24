#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_uniform_oil_thickness_op.py
@date 03/11/13
@description A module containing a function for the maximum uniform the oil thickness in a grid cell
'''
import numpy
import logging

from pystoch import util
from pystoch.keywords import *

logger = logging.getLogger('pystoch.operators.max_uniform_oil_thickness_op')


@util.coroutine
def max_uniform_oil_thickness_op(result,cell_area, min_time=None):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in uniform_oil_thickness_op operation. Received type: %s' % type(result))

    try:
    
        aggregator = result.copy()
        aggregator[:] = 0.0
        
        while True:
            block, index_position, weight, metadata = (yield)
        
            #logger.info('block shape: %s' % list(block.shape))
            #logger.info('block: %s' % block)
            #logger.info('index_pos shape: %s' % list(index_position.shape))
            #logger.info('weight shape: %s' % list(weight.shape))
            #logger.info('weight: %s' % weight)

            # Calculate oil volume seconds!
            weighted_oil_thickness = block['mass']/block['density'] / weight / cell_area
        
        
            blen = index_position.shape[0]
            for i in xrange(blen): 
            
                # Can't sum - need to take the max value over all time step...       
                aggregator[tuple(index_position[i,:])] += weighted_oil_thickness[i]
                   
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep
                
                if min_time is not None:
                    min_array = min_time['min_array']
                    thickness = min_time['thickness']
                    
                    for i in xrange(min_array.shape[0]):
                        ind_array = aggregator > thickness[i]
                        min_array[i,ind_array] = numpy.minimum(
                            min_array[i,ind_array], metadata[TIME][ETIME] )
                    
                
                numpy.maximum(aggregator, result, out=result)
                # Previous method - incorrect!
                #result[aggregator > 0.0] = aggregator[aggregator > 0.0]
                                
                aggregator[:]= 0.0
                
            
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        logger.info('cell_area:\n%s' % cell_area)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
    
        raise
