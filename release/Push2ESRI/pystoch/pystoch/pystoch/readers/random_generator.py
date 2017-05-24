#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file abstract_reader.py
@date 03/11/13
@description An abstract class for the particle readers
'''
import numpy
from pystoch import util
from pystoch.datatypes import DT
from pystoch.readers.abstract_reader import AbstractParticleReader
from pystoch.exceptions import PyStochIOError

from pystoch.keywords import * # Import keywords


import logging
logger = logging.getLogger('pystoch.readers.random_generator')

class RandomWalkGenerator(AbstractParticleReader):

    # Define the possible values to put in the generator result
    
    SURFACE_SPILLETS                = 'surface spillets'
    SUBSURFACE_SPILLETS             = 'subsurface spillets'
    SHORELINE_SPILLETS              = 'shoreline spillets'
    GREEN_AND_PURPLE_SPILLETS       = 'green and purple spillets'

    product_spillet_map = {}
    product_spillet_map[SURFACE] = [SURFACE_SPILLETS]
    product_spillet_map[SUBSURFACE] = [SUBSURFACE_SPILLETS,GREEN_AND_PURPLE_SPILLETS]
    product_spillet_map[SHORE] = [SHORELINE_SPILLETS]

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        @blocksize is the number of particle records to read per block of data returned
        """
        # Ensure all constructors are called properly
        super(RandomWalkGenerator, self).__init__(*args, **kwargs)
        
        self.nblocks = kwargs.get('nblocks',10)
        self.blocksize = kwargs.get('blocksize',100)
        
        self.spillet_types = {
            RandomWalkGenerator.SURFACE_SPILLETS : {
                'dtype'  : DT.IDEAL_PARTICLE,
                'offset' : None,
                'count'  : None},
            RandomWalkGenerator.SUBSURFACE_SPILLETS : {
                'dtype'  : DT.IDEAL_PARTICLE,
                'offset' : None,
                'count'  : None},
            RandomWalkGenerator.SHORELINE_SPILLETS : {
                'dtype'  : DT.IDEAL_PARTICLE,
                'offset' : None,
                'count'  : None},
            RandomWalkGenerator.GREEN_AND_PURPLE_SPILLETS : {
                'dtype'  : DT.IDEAL_PARTICLE,
                'offset' : None,
                'count'  : None},
                }
        
        # Can not gaurentee the half open distribution when scale and offset is applied due 
        # too floating point round off. 5+5*[0 1) becomes [5 10]!
        #self.rdist_func = kwargs.get('random_distribution',util.random_sample)
        #self.r_offset_vec = kwargs.get('random_offset',numpy.zeros(DT.NDIMS,DT.PRECISION))
        #self.r_scale_vec = kwargs.get('random_scale',numpy.ones(DT.NDIMS,DT.PRECISION))
        
        
    def stream_record_blocks(self,output_definition=None):
        """
        A generator function which yields blocks of particle records to the caller
        
        Note - all particles, (surface/subsurface etc) have DT.NDIMS dimension!
        """
        if output_definition is None:
            # default to output everything
            output_definition = (
                RandomWalkGenerator.SURFACE_SPILLETS,
                RandomWalkGenerator.SUBSURFACE_SPILLETS,
                RandomWalkGenerator.SHORELINE_SPILLETS,
                RandomWalkGenerator.GREEN_AND_PURPLE_SPILLETS
            )
        
        for i in xrange(self.nblocks):
            
            output = {}
            
            
            output[METADATA] = {
                    TIME:{
                        ETIME: 3600 * numpy.int32(i+1),  # hourly data
                        DTIME: numpy.int32(3600)
                        },
                    BLOCK:{
                        N_OF_M_IN_F: (i,self.nblocks),
                        N_OF_M_IN_TS: (1,1) # all in one timestep
                        }
                    }
    
            if RandomWalkGenerator.SURFACE_SPILLETS in output_definition:
                output[RandomWalkGenerator.SURFACE_SPILLETS] = self.make_particles(i)
            
            if RandomWalkGenerator.SUBSURFACE_SPILLETS in output_definition:
                output[RandomWalkGenerator.SUBSURFACE_SPILLETS] = self.make_particles(i)
            
            if RandomWalkGenerator.SHORELINE_SPILLETS in output_definition:
                output[RandomWalkGenerator.SHORELINE_SPILLETS] = self.make_particles(i)
            
            if RandomWalkGenerator.GREEN_AND_PURPLE_SPILLETS in output_definition:
                output[RandomWalkGenerator.GREEN_AND_PURPLE_SPILLETS] = self.make_particles(i)
            
            yield output
            
            
    def make_particles(self,iteration=0):
    
            particles = numpy.zeros((self.blocksize,),dtype=DT.IDEAL_PARTICLE)
            # Grrr - no way to pass the buffer to put random numbers in ?
            
            particles['loc'] = util.random_sample(particles['loc'].shape,dtype=DT.PRECISION)
            particles['prev_loc'] = util.random_sample(particles['loc'].shape,dtype=DT.PRECISION)
            
            particles['lifetime'][:] = (# Cheat and make time a function of block number
                                        DT.SPRECISION(iteration)
                                        )
            
            mass_offset = DT.SPRECISION(0.9)
            mass_scale = DT.SPRECISION(.1)
            mass_time_param = DT.SPRECISION(1)/numpy.log10(DT.SPRECISION(iteration + 2))
            # 1/log10(i+2) * (rand[0.9 - 1.0) ) ) 
            particles['mass'] = (    
                                 mass_time_param *
                                  (util.random_sample(*particles['mass'].shape)*
                                   mass_scale + mass_offset)
                                )
            
            dens_offset = DT.SPRECISION(0.9)
            dens_scale = DT.SPRECISION(.1)
             # dens = rand[0.9 - 1.0)                                                
            particles['density'] = (   
                                    numpy.random.rand(*particles['density'].shape)*
                                       dens_scale + dens_offset
                                    )
                                    
            return particles
        
    def get_surface_extents(self):
        return self.get_extents(2,None)


    def get_subsurface_extents(self):
        return self.get_extents(2,None)
        

    def get_extents(self,ndims, spillets=None):
        if ndims == 2:
            return DT.extents(ndims=2, prec=DT.PRECISION,ur_default=(1,1), ll_default=(0,0))
        elif ndims ==3:
            return DT.extents(ndims=3, prec=DT.PRECISION,ur_default=(1,1,1), ll_default=(0,0,0))
        else:
            raise PyStochIOError('Invalid number of dimensions selected.')
        
        
        

            