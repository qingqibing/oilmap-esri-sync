#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oilmdl_reader.py
@date 03/11/13
@description Implementation of the Oil Model STT Data Reader
'''
import numpy
from pystoch.datatypes import DT
from pystoch.readers.abstract_reader import AbstractParticleReader
from pystoch.exceptions import PyStochIOError
from pystoch.keywords import *

import logging
logger = logging.getLogger('pystoch.readers.oilmdl_reader')


            
reader_key = frozenset(['stt','stp'])


STP_RECORD_SIZE = 20

OILMDL_STP_FILE_TYPE = numpy.dtype([('rec_position', numpy.int32, 1),
                        ('sim_time', numpy.int32, 1) ,
                        ('n_surface_records', numpy.int32, 1),
                        ('n_shore_records', numpy.int32, 1),
                        ('n_subsurface_records', numpy.int32, 1),
                        ])

OILMDL_STP_VER_TYPE = numpy.dtype([('version', numpy.int32, 1),
                        ('junk', numpy.character, 16)
                        ])

class OilModelDirectAccessReader(AbstractParticleReader):

    # Define the possible values to put in the generator result
    SURFACE_SPILLETS                = 'surface spillets'
    SUBSURFACE_SPILLETS             = 'subsurface spillets'
    SHORELINE_SPILLETS              = 'shoreline spillets'

    product_spillet_map = {}
    product_spillet_map[SURFACE] = [SURFACE_SPILLETS]
    product_spillet_map[SUBSURFACE] = [SUBSURFACE_SPILLETS]
    product_spillet_map[SHORE] = [SHORELINE_SPILLETS]

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        """
        # Ensure all constructors are called properly
        super(OilModelDirectAccessReader, self).__init__(*args, **kwargs)
    
        self._load_meta()
    

    
    
    def _load_meta(self):
        
        record_data = None
        with open(self.fname + '.stp','rb') as stp_file:
            # Move to the end of the first recors - it is empty
            stt_version = numpy.fromfile(stp_file,dtype=OILMDL_STP_VER_TYPE,count=1)
            stt_version = stt_version['version'][0]
            
            
            stp_file.seek(1*STP_RECORD_SIZE)
            try:
                record_data = numpy.fromfile(stp_file,dtype=OILMDL_STP_FILE_TYPE,count=-1)
            except ValueError as ve:
                logger.exception(ve)
                raise PyStochIOError("Value error caught while reading:'%s', possibly due to empty file?" % (self.fname+'.stp'))
            
        if record_data is None:
            raise PyStochIOError("Could not read data from STP file:'%s'" % (self.fname+'.stp'))
        
        if len(record_data) == 0 :
            raise PyStochIOError("STP file '%s' is empty - no records!" % (self.fname+'.stp'))
        
        ### CONVERT FROM FORTRAN TO C INDEXING! ###
        record_data['rec_position'] -= 1
                    
        self._record_data = record_data
    
        #logger.info(record_data)
    
        if stt_version == 1002:
            self.STT_RECORD_SIZE = 50

            # The exact type used in RunStoch / OilMdl
            OILMDL_STT_FILE_SURFACE_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTDP2D, 1),               #lon, lat (degrees)
                        ('prev_loc', DT.POINTDP2D, 1),          #lon, lat (degrees)
                        ('mass',DT.SPRECISION,1),               #mass (MT)
                        ('density',DT.SPRECISION,1),            #density(MT/M3 = g/cm3)
                        ('fwc',DT.SPRECISION,1),                #fraction of water content (None)
                        ('lifetime',DT.SPRECISION,1),           #age (hours)
                        ('nwhere',numpy.int16,1)                #? onshore or on water?
                        ])

            OILMDL_STT_FILE_SHORE_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTDP2D, 1),
                        ('mousse_volume',DT.SPRECISION,1),
                        ('mass',DT.SPRECISION,1),
                        ('density',DT.SPRECISION,1),
                        ('fwc',DT.SPRECISION,1),
                        ('radius',DT.SPRECISION,1),
                        ('shoreline_width',DT.SPRECISION,1),
                        ('junk',numpy.character,self.STT_RECORD_SIZE - (2*8 + 6*4))
                        ])

            OILMDL_STT_FILE_SUBSURFACE_PARTICLE = numpy.dtype([
                        #Figure our what the real types are!
                        ('loc', DT.POINTDP2D, 1),
                        ('prev_loc', DT.POINTDP2D, 1),
                        ('zm',DT.SPRECISION,1),   
                        ('mass',DT.SPRECISION,1),   
                        ('age',DT.SPRECISION,1),   
                        ('flag',numpy.int16,1),   
                        ('junk',numpy.character,self.STT_RECORD_SIZE - (2*8 +2*8 + 3*4 + 2))
                        ])

        elif stt_version == 1003:
            self.STT_RECORD_SIZE = 54
    
            OILMDL_STT_FILE_SURFACE_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTDP2D, 1),
                        ('prev_loc', DT.POINTDP2D, 1),
                        ('mass',DT.SPRECISION,1),
                        ('density',DT.SPRECISION,1),
                        ('fwc',DT.SPRECISION,1),
                        ('lifetime',DT.SPRECISION,1),
                        ('radius',DT.SPRECISION,1),
                        ('nwhere',numpy.int16,1)
                        ])

            OILMDL_STT_FILE_SHORE_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTDP2D, 1),
                        ('mousse_volume',DT.SPRECISION,1),
                        ('mass',DT.SPRECISION,1),
                        ('density',DT.SPRECISION,1),
                        ('fwc',DT.SPRECISION,1),
                        ('radius',DT.SPRECISION,1),
                        ('shoreline_width',DT.SPRECISION,1),
                        ('junk',numpy.character,self.STT_RECORD_SIZE - (2*8 + 6*4))
                        ])

            OILMDL_STT_FILE_SUBSURFACE_PARTICLE = numpy.dtype([
                        #Figure our what the real types are!
                        ('loc', DT.POINTDP2D, 1),
                        ('prev_loc', DT.POINTDP2D, 1),
                        ('zm',DT.SPRECISION,1),   
                        ('mass',DT.SPRECISION,1),   
                        ('age',DT.SPRECISION,1),   
                        ('flag',numpy.int16,1),   
                        ('junk',numpy.character,self.STT_RECORD_SIZE - (2*8 +2*8 + 3*4 + 2))
                        ])
    
        else:
            raise PyStochIOError("Unknown STT file version: '%s'" % stt_version)
    
    
        self.spillet_types = {
            OilModelDirectAccessReader.SURFACE_SPILLETS     : {
                'dtype'  : OILMDL_STT_FILE_SURFACE_PARTICLE,
                'offset' : None,
                'count'  : None},
            OilModelDirectAccessReader.SHORELINE_SPILLETS   : {
                'dtype'  : OILMDL_STT_FILE_SHORE_PARTICLE,
                'offset' : None,
                'count'  : None},
            OilModelDirectAccessReader.SUBSURFACE_SPILLETS  : {
                'dtype'  : OILMDL_STT_FILE_SUBSURFACE_PARTICLE,
                'offset' : None,
                'count'  : None},
            }
    
        
    def stream_record_blocks(self,output_definition=None):
        """
        A generator function which yields blocks of particle records to the caller
        """
        if output_definition is None:
            # default to output everything
            output_definition = (
                OilModelDirectAccessReader.SURFACE_SPILLETS,
                OilModelDirectAccessReader.SUBSURFACE_SPILLETS,
                OilModelDirectAccessReader.SHORELINE_SPILLETS
            )
        
        
        with open(self.fname + '.stt','rb') as stt_file:

            stt_file.seek(self._record_data['rec_position'][0]*self.STT_RECORD_SIZE)
        
            nblocks = len(self._record_data)

            
            # a variable to save the last time in for estimating deltaT. Use native units of the file - minutes
            last_time = numpy.int32(self._record_data['sim_time'][0] - (self._record_data['sim_time'][1] - self._record_data['sim_time'][0])) 
            # Assume the second time step is the same as the first.
            start_time = numpy.int32(self._record_data['sim_time'][0])
            
            for block_number in xrange(nblocks):

                n_surface_spillets = self._record_data['n_surface_records'][block_number]
                n_subsurface_spillets = self._record_data['n_subsurface_records'][block_number]
                n_shore_spillets = self._record_data['n_shore_records'][block_number]
            
                offsets = {
                    OilModelDirectAccessReader.SURFACE_SPILLETS    : (0 ) * self.STT_RECORD_SIZE,
                    OilModelDirectAccessReader.SHORELINE_SPILLETS  : (n_surface_spillets) * self.STT_RECORD_SIZE,
                    OilModelDirectAccessReader.SUBSURFACE_SPILLETS : (n_surface_spillets + n_shore_spillets) * self.STT_RECORD_SIZE,
                }

                counts = {
                    OilModelDirectAccessReader.SURFACE_SPILLETS    : n_surface_spillets,
                    OilModelDirectAccessReader.SHORELINE_SPILLETS  : n_shore_spillets,
                    OilModelDirectAccessReader.SUBSURFACE_SPILLETS : n_subsurface_spillets,
                }

            
                tstep_bytes = (n_surface_spillets +
                    n_subsurface_spillets +
                    n_shore_spillets) * self.STT_RECORD_SIZE
            
                buffer = stt_file.read(tstep_bytes)
            
                # Now sort out the mess...
                output = {}
                
                output[METADATA] = {
                    TIME:{
                        ETIME: 60 * numpy.int32(self._record_data['sim_time'][block_number] - start_time),
                        DTIME: 60 * numpy.int32(self._record_data['sim_time'][block_number] - last_time)
                        },
                   BLOCK:{
                        N_OF_M_IN_F: (block_number,nblocks),
                        N_OF_M_IN_TS: (1, 1) # all in one timestep
                        },
                    FILE_NAME:self.fname
                    }
                last_time = numpy.int32(self._record_data['sim_time'][block_number])    
                        
                
                for spillet_type in output_definition:
                    
                    
                    # need to actually read some spillet data
                    reader_args=self.spillet_types[spillet_type].copy()
                
                    reader_args['count'] = counts[spillet_type]
                    reader_args['offset'] = offsets[spillet_type]
                
                    #logger.info("%s: %s" % (spillet_type, reader_args))
                
                    particles = numpy.frombuffer(buffer, **reader_args)
                    
                    
                    
                    if spillet_type == OilModelDirectAccessReader.SURFACE_SPILLETS:
                        #if (particles['nwhere']!=1).any():
                        #   logger.info(particles[particles['nwhere']!=1])
                        particles = particles[particles['nwhere']==1]
                        
                        if (particles['nwhere']==-1).any():
                            raise PyStochIOError('OilModel Reader got a spillet in a boom (nwhere==-1). Booming is not implemented yet!')


                    output[spillet_type] = particles


                yield output
            
    def get_surface_extents(self):
        return self.get_extents(2,(OilModelDirectAccessReader.SURFACE_SPILLETS,))

    def get_subsurface_extents(self):
        return self.get_extents(2,(OilModelDirectAccessReader.SUBSURFACE_SPILLETS,))
            
            
            
            
            