#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file thickest_spillet_op.py
@date 03/11/13
@description Calculates the thickest spillet in each cell of each time step
'''
import numpy
import logging

from pystoch.exceptions import PyStochOperatorError
from pystoch import util
from pystoch.keywords import *

from pystoch.datatypes import DT
from pystoch import config

try:
    # Temporary hack till I get support setup for building/installing on windows
    import pyximport
    #pyximport.install(setup_args={"script_args":["--compiler=mingw32"],"include_dirs":numpy.get_include()}, reload_support=True)
    pyximport.install(setup_args={"include_dirs":numpy.get_include()}, reload_support=True)
    import grid_max
except:
    grid_max = None

#grid_max = None

logger = logging.getLogger('pystoch.operators.thickest_spillet_op')


@util.coroutine
def thickest_spillet_op(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('invalid result argument in thickest_spillet_op operation. Received type: %s' % type(result))

    try:
        
        if grid_max is not None:
            while True:
                block, index_position, weight, metadata = (yield)
        
                radius = block['radius']
            
                spillet_thickness = block['mass']/block['density'] / (numpy.pi * radius**2) * numpy.ones(weight.shape)
        
                n = grid_max.c_grid_max(result, index_position, spillet_thickness.astype('float32'))
        
        else:
        
            while True:
                block, index_position, weight, metadata = (yield)
                try:
                    spillet_thickness = block['thickness']
                except ValueError:
                    radius = block['radius']
                    spillet_thickness = block['mass']/block['density'] / (numpy.pi * radius**2) * numpy.ones(weight.shape)
        
                blen = index_position.shape[0]
                for i in xrange(blen): 
                
                    # Can't sum - need to take the max value over all time step...       
                    result[tuple(index_position[i,:])] = max(result[tuple(index_position[i,:])], spillet_thickness[i])
             
                #result[[index_position[:,i] for i in xrange(index_position.shape[1])]] = max(result[[index_position[:,i] for i in xrange(index_position.shape[1])]], spillet_thickness)
                
                   
    except IndexError as ie:
    
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        logger.info('Spillet Thickness: %s' % type(spillet_thickness))
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in thickest_spillet_op coroutine')
    
        raise
        
        
    except ValueError as ve:
        logger.info('block:\n%s' % block)
        logger.info('Hit a value error during thickest_spillet_op coroutine - probably do to a spillet type that does not have a radius')
        raise
