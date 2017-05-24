#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_shore_grid_thickness_op.py
@date 03/11/13
@description A coroutine which calculates the maximum thickness in a grid cell for shore spillets
'''

import numpy
import logging

from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

logger = logging.getLogger('pystoch.map_reduce_ops.max_shore_grid_thickness_op')


@util.coroutine
def max_shore_grid_thickness_op(result, shore_length, min_time=None):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in max_shore_grid_thickness_op operation. Received type: %s' % type(result))

    aggregator = result.copy()
    aggregator[:] = 0.0


    try:
        #count = 0
        while True:
            block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
            
            weighted_oil_thickness = block['mass']/block['density'] / weight / (shore_length * block['shoreline_width'])

            
            blen = index_position.shape[0]
            for i in xrange(blen): 
            
                # Can't sum - need to take the max value over all time step...       
                aggregator[tuple(index_position[i,:])] += weighted_oil_thickness[i]
                   
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep
                
                if min_time is not None:
                    raise NotImplementedError('Need to implement this function!')
                                    
                numpy.maximum(aggregator, result, out=result)
                # Previous method - incorrect!
                #result[aggregator > 0.0] = aggregator[aggregator > 0.0]
                                
                aggregator[:]= 0.0
            
    except IndexError as ie:
    
         
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in counterp_op coroutine')
        
        raise 