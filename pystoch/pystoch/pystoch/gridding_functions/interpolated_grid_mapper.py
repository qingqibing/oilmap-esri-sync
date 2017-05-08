#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file interpolated_grid.py
@date 03/11/13
@description A module containing a courtine for binning particles by interpolated position
between their current and previous location. Once located in the grid, operations can be 
called for each particle to calculate different products.
'''
import numpy
import logging

from pystoch import util
from pystoch.datatypes import DT

logger = logging.getLogger('pystoch.map_reduce_ops.interpolated_grid')

# Name for this gridding method:
grid_function_name = 'interpolated bin gridding'

# Standard function name for all grid_functions
@util.coroutine
def grid_function(grid,operators):
    
    # Dummy allocations - will be reallocated as needed.
    index_position = numpy.zeros(0,dtype=DT.IVECTOR) # The IJ location of the particle
    prev_index_position = numpy.zeros(0,dtype=DT.IVECTOR) # The IJ location of the particle at the previous timestep
    index_diff = numpy.zeros(0,dtype=DT.IVECTOR) # The IJ location change between timesteps
    index_sum = numpy.zeros(0,dtype=DT.IVECTOR) # The sum of the IJ location change

    
    nsamples_per_grid = 3
    
    # Temporary hack:
    block_number = 0

    while True:
        (block, metadata) = (yield) # an array of particle datatype
        
        block_number += 1
        
        blen = len(block)
                
        particle_position = block['loc']
        prev_particle_position = block['prev_loc']

        # the number of dimensions in a position vector
        ndims = particle_position.shape[1]


        if index_position.shape != particle_position.shape:
            index_position = numpy.zeros(particle_position.shape,numpy.int32)
        else:
            index_position[:]=0
            
        if prev_index_position.shape != prev_particle_position.shape:
            prev_index_position = numpy.zeros(prev_particle_position.shape,numpy.int32)
        else:
            prev_index_position[:]=0
        
        if index_diff.shape != prev_particle_position.shape:
            index_diff = numpy.zeros(prev_particle_position.shape,numpy.int32)
        else:
            index_diff[:]=0
                          
        if index_sum.shape != blen:
            index_sum = numpy.zeros(blen,numpy.int32)
        else:
            index_sum[:]=0
                          
        # Calculate the IJ index of each particle now and previously
        grid.indexof(particle_position, out=index_position)
        grid.indexof(prev_particle_position, out=prev_index_position)

        #evaluate the absolute value of the index space difference
        index_diff[...] = numpy.abs(index_position - prev_index_position)

        index_sum[...] = numpy.sum(index_diff, axis=1)
            
        for i in xrange(blen):
                
            if index_sum[i] > 0:
        
                delta_pos = particle_position[i,:] - prev_particle_position[i,:]
                samples = index_sum[i] * nsamples_per_grid
            
                interpolated_positions = delta_pos.reshape(1,ndims) * numpy.arange(samples).reshape(samples,1) / DT.PRECISION(samples)
            
                interpolated_positions += prev_particle_position[i,:].reshape(1,ndims)
            
                interpolated_index_positions = grid.indexof(interpolated_positions)
                
                # Make the weight array the correct size
                weight = DT.PRECISION(1.0/samples) * numpy.ones((samples,))
                for target in operators:
                    target.send((block[i],interpolated_index_positions, weight, metadata))
             
            else:
                # Make the weight array the correct size
                weight = numpy.ones((1,))
                for target in operators:
                    target.send((block[i], prev_index_position[i,:].reshape(1,ndims), weight, metadata))
                