#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oilmdl_reader.py
@date 03/11/13
@description Implementation of the Oil Model STT Data Reader

@TODO - figure out how to read the file using the names/dtype structure that I want for pystoch!
'''
import h5py
import numpy
from pystoch.datatypes import DT
from pystoch.readers.abstract_reader import AbstractParticleReader
from pystoch.exceptions import PyStochIOError
from pystoch.keywords import *

import logging
logger = logging.getLogger('pystoch.readers.oilmdl_reader')


            
reader_key = frozenset(['h5'])

TRAJECTORY_STATS = 'trajectory_stats'


class OilModelHdfReader(AbstractParticleReader):

    # Define the possible values to put in the generator result
    SURFACE_SPILLETS                = 'surface_spillets'
    SUBSURFACE_SPILLETS             = 'subsurface spillets'
    SHORELINE_SPILLETS              = 'shore_spillets'

    product_spillet_map = {}
    product_spillet_map[SURFACE] = [SURFACE_SPILLETS]
    product_spillet_map[SUBSURFACE] = [SUBSURFACE_SPILLETS]
    product_spillet_map[SHORE] = [SHORELINE_SPILLETS]

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        """
        # Ensure all constructors are called properly
        super(OilModelHdfReader, self).__init__(*args, **kwargs)
    
        self._load_meta()
    

    
    
    def _load_meta(self):
        
        record_data = None
        with h5py.File(self.fname + '.h5','r') as hdf:
            
            record_data = hdf[TRAJECTORY_STATS][...]
            
                      
        self._record_data = record_data
    
        if self._record_data is None:
            raise PyStochIOError('Unable to read hdf file!')
       
    
        
    def stream_record_blocks(self,output_definition=None):
        """
        A generator function which yields blocks of particle records to the caller
        """
        if output_definition is None:
            # default to output everything
            output_definition = (
                OilModelHdfReader.SURFACE_SPILLETS,
                OilModelHdfReader.SUBSURFACE_SPILLETS,
                OilModelHdfReader.SHORELINE_SPILLETS
            )
        
        nblocks = len(self._record_data)
        
        # a variable to save the last time in for estimating deltaT. Use native units of the file - minutes
        last_time = 2 * self._record_data['Time (minutes since 12-31-1979)'][0] - self._record_data['Time (minutes since 12-31-1979)'][1]

        # Assume the second time step is the same as the first.
        start_time = self._record_data['Time (minutes since 12-31-1979)'][0]
        
        with h5py.File(self.fname + '.h5','r') as hdf:
          
            for block_number in xrange(nblocks):
  
                # Now sort out the mess...
                output = {}
                
                output[METADATA] = {
                    TIME:{
                        ETIME: 60 * (self._record_data['Time (minutes since 12-31-1979)'][block_number] - start_time),
                        DTIME: 60 * (self._record_data['Time (minutes since 12-31-1979)'][block_number] - last_time)
                        },
                   BLOCK:{
                        N_OF_M_IN_F: (block_number,nblocks),
                        N_OF_M_IN_TS: (1, 1) # all in one timestep
                        },
                    FILE_NAME:self.fname
                    }
                last_time = numpy.int32(self._record_data['Time (minutes since 12-31-1979)'][block_number])    
                        
                
                group_name = self._record_data['Time Step Group Name'][block_number]
                    
                group = hdf[group_name]
                    
                for spillet_type in output_definition:
                    particles = None

                    dset = group.get( spillet_type, None)
                    if dset is None:
                        continue                   

                    output[spillet_type] = dset[...]


                yield output
            
    def get_surface_extents(self):
        logger.info("Ignoring surface only request and returning extent bounds of all spillets")
        return self.get_extents(2,(OilModelHdfReader.SURFACE_SPILLETS,))

    def get_subsurface_extents(self):
        logger.info("Ignoring subsurface only request and returning extent bounds of all spillets")
        return self.get_extents(2,(OilModelHdfReader.SUBSURFACE_SPILLETS,))
            
            
            
    def get_extents(self,ndims, spillets=None):
    
        result = DT.extents(ndims=ndims, prec=DT.SPRECISION)
        
        pmin = result['ll'][0]
        pmax = result['ur'][0]
        
        pmax[0] = numpy.max(self._record_data["UR Bound"]["Lon"],axis=0)
        pmax[1] = numpy.max(self._record_data["UR Bound"]["Lat"], axis=0)
    
        pmin[0] = numpy.min(self._record_data["LL Bound"]["Lon"],axis=0)
        pmin[1] = numpy.min(self._record_data["LL Bound"]["Lat"], axis=0)
    
        # Add a little margin to the actual value...
        result['ll'][0] = pmin - 0.001*abs(pmin)
        result['ur'][0] = pmax + 0.001*abs(pmax)
        
        return result

    
    
    
    
    
    
    
            
            
            
            