#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file bin_grid.py
@date 03/11/13
@description A module containing a courtine for binning particles by position. Once located
in the grid operations can be called for each particle to calculate different products.
'''
import numpy
import logging
from pystoch.datatypes import DT
from pystoch import util

logger = logging.getLogger('pystoch.gridding_functions.bin_grid_mapper')

# Name for this gridding method:
grid_function_name = 'bin gridding'

# Standard function name for all grid_functions
@util.coroutine
def grid_function(grid,operators):

    index_position = numpy.zeros(0,dtype=DT.IVECTOR) # The IJ location of the particle

    while True:
        (block, metadata) = (yield) # an array of particle datatype
                
        blen = len(block)
        
        particle_position = block['loc']
        
        if index_position.shape != particle_position.shape:
            index_position = numpy.zeros(particle_position.shape,numpy.int32)
        else:
            index_position[:]=0

        grid.indexof(particle_position, out=index_position)
            
                
        for target in operators:
            # send: Particles, index_position, weights and metadata for each cell
            target.send((block,index_position,DT.PRECISION(1.0), metadata))
        