#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file min_time_op.py
@date 03/11/13
@description A module containing a function for recording the minimum time for a grid cell to be hit
'''
import numpy
import logging

from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

logger = logging.getLogger('pystoch.operators.min_time_op')


@util.coroutine
def min_time_op(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in min time operation. Received type: %s' % type(result))

    try:
        #count = 0
        while True:
            block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
        
            #logger.info('block %s' % list(block.shape))
            #logger.info('index_pos %s' % list(index_position.shape))
            #logger.info('weight %s' % list(weight.shape))
            #logger.info('weight %s' % weight)
            #logger.info(metadata)
            blen = index_position.shape[0]

            #fancy vectorized way of taking the minimum from the cells where particles are indexed. 
            result[[index_position[:,i] for i in xrange(index_position.shape[1])]] = numpy.minimum(
                    result[[index_position[:,i] for i in xrange(index_position.shape[1])]],
                    metadata[TIME][ETIME]
                    )
            
            #count +=1
            #logger.info('Block count: %s; Block size: %s' % (count, len(block)))
            
    except IndexError as ie:
    
         
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
        
        raise 