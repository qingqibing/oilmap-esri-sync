#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_concentration_op.py
@date 03/11/13
@description A coroutine which calculates the maximum concentration in a grid cell
'''

import numpy
import logging

from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

logger = logging.getLogger('pystoch.map_reduce_ops.max_concentration_op')


@util.coroutine
def max_concentration_op(result, cell_depth_range, cell_area):
    """
    Cell depth range is specified positive downward (upper/surface, lower/bottom)
    Cell area is in square meters
    """

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in max_concentration_op. Received type: %s' % type(result))

    aggregator = result.copy()
    aggregator[:] = 0.0

    cell_height = cell_depth_range[1] - cell_depth_range[0]
    cell_volume = cell_height * cell_area

    try:
        #count = 0
        while True:
            block, index_position, weighting, metadata = (yield) # Standard arguments passed from the grid_mapper
            
            
            weighted_oil_concentration = block['mass']/ weighting / cell_volume
            
            #logger.info('block shape: %s' % list(block.shape))
            #logger.info('index_position shape: %s' % list(index_position.shape))
            
            if block.shape == tuple():
                #logger.info('block shape empty!')
                if block['zm'] >= cell_depth_range[0] and block['zm'] < cell_depth_range[1]:
                       
                    for i in xrange(index_position.shape[0]):         
                        aggregator[tuple(index_position[i,:])] += weighted_oil_concentration[i]
                
            elif block.shape == (index_position.shape[0],):
                #logger.info('block shape full!')

                depth = block['zm']
                # assuming positive downward
                in_range = numpy.logical_and( depth >= cell_depth_range[0], depth < cell_depth_range[1])
            
                # tried to do this with nditer but failed. Need to come back to optimize later...        
                for i in xrange(len(in_range)):
                    if in_range[i]:
                        index_tuple = tuple(index_position[i,:])
                        oil_c =  weighted_oil_concentration[i]           
                        aggregator[index_tuple] += oil_c
                   
            else:
                raise IndexError('Incompatible block shape and index_position shape: %s, %s' % (block.shape, index_position.shape))
                   
            n_of_m_tsteps = metadata[BLOCK][N_OF_M_IN_TS]
            if n_of_m_tsteps[0] == n_of_m_tsteps[1]: # if this is the last block in the timestep
                
                numpy.maximum(aggregator, result, out=result)
                                
                aggregator[:]= 0.0
            
    except IndexError as ie:
    
         
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weighting:\n%s' % weighting)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in max_concentration_op coroutine')
        
        raise 