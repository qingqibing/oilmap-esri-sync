#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oil_volume_op.py
@date 03/11/13
@description A module containing a function for summing the oil volume in a grid cell
'''
import numpy
import logging

from pystoch import util
from pystoch.keywords import *

logger = logging.getLogger('pystoch.operators.oil_volume_op')


@util.coroutine
def oil_volume_op(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in oil_volume operation. Received type: %s' % type(result))

    try:

        while True:
            block, index_position, weight, metadata = (yield)
        
            #logger.info('block %s' % list(block.shape))
            #logger.info('index_pos %s' % list(index_position.shape))
            #logger.info('weight %s' % list(weight.shape))
            #logger.info('weight %s' % weight)

            # Calculate oil volume seconds!
            weighted_oil_volume = block['mass']/block['density'] / weight # * metadata[TIME][DTIME]
        
            blen = index_position.shape[0]
            for i in xrange(blen):        
                result[tuple(index_position[i,:])] += weighted_oil_volume[i]
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in oil_volume_op coroutine')
    
        raise