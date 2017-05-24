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


            
reader_key = frozenset(['oml','omp'])


OMP_RECORD_SIZE = 12

OILMDL_OMP_FILE_TYPE = numpy.dtype([('rec_position', numpy.int32, 1),
                        ('sim_time', numpy.int32, 1) ,
                        ('n_oil_recs', numpy.int32, 1),
                        ])

OILMDL_OMP_VER_TYPE = numpy.dtype([('version', numpy.int32, 1),
                        ('junk', numpy.character, 8)
                        ])

class OilModelDirectAccessOMReader(AbstractParticleReader):

    # Define the possible values to put in the generator result
    OIL_SPILLETS                = 'oil spillets'

    product_spillet_map = {}
    product_spillet_map[SURFACE] = [OIL_SPILLETS]
    product_spillet_map[SUBSURFACE] = [OIL_SPILLETS]
    product_spillet_map[SHORE] = [OIL_SPILLETS]

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        """
        # Ensure all constructors are called properly
        super(OilModelDirectAccessOMReader, self).__init__(*args, **kwargs)
    
        self._load_meta()
    
    
    def _load_meta(self):
        
        record_data = None
        with open(self.fname + '.omp','rb') as omp_file:
            # Move to the end of the first recors - it is empty
            omp_version = numpy.fromfile(omp_file,dtype=OILMDL_OMP_VER_TYPE,count=1)
            omp_version = omp_version['version'][0]
            
            
            omp_file.seek(1*OMP_RECORD_SIZE)
            try:
                record_data = numpy.fromfile(omp_file,dtype=OILMDL_OMP_FILE_TYPE,count=-1)
            except ValueError as ve:
                logger.exception(ve)
                raise PyStochIOError("Value error caught while reading:'%s', possibly due to empty file?" % (self.fname+'.omp'))
            
        if record_data is None:
            raise PyStochIOError("Could not read data from OMP file:'%s'" % (self.fname+'.omp'))
        
        if len(record_data) == 0 :
            raise PyStochIOError("STP file '%s' is empty - no records!" % (self.fname+'.omp'))
        
        ### CONVERT FROM FORTRAN TO C INDEXING! ###
        record_data['rec_position'] -= 1
                    
        self._record_data = record_data
    
        #logger.info(record_data)
    
        if omp_version == 1002:
            self.OML_RECORD_SIZE = 40

            # The exact type used in RunStoch / OilMdl
            OILMDL_OML_FILE_OIL_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTSP2D, 1),               #lon, lat (degrees)
                        ('none',DT.SPRECISION,1),               #mass (MT)
                        ('nwhere',numpy.int32,1),               #? onshore or on water?
                        ('mass',DT.SPRECISION,1),               #mass (MT)
                        ('radius',DT.SPRECISION,1),             #radius (M)
                        ('thickness',DT.SPRECISION,1),          #
                        ('visco',DT.SPRECISION,1),              #
                        ('fwc',DT.SPRECISION,1),                #fraction of water content (None)
                        ('flashpt',DT.SPRECISION,1),            #
                        ])
                        

        else:
            raise PyStochIOError("Unknown OMP file version: '%s'" % omp_version)
    
    
        self.spillet_types = {
            OilModelDirectAccessOMReader.OIL_SPILLETS     : {
                'dtype'  : OILMDL_OML_FILE_OIL_PARTICLE,
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
                OilModelDirectAccessOMReader.OIL_SPILLETS,
            )
        
        
        with open(self.fname + '.oml','rb') as oml_file:

            oml_file.seek(self._record_data['rec_position'][0]*self.OML_RECORD_SIZE)
        
            nblocks = len(self._record_data)

            
            # a variable to save the last time in for estimating deltaT. Use native units of the file - minutes
            last_time = numpy.int32(self._record_data['sim_time'][0] - self._record_data['sim_time'][1]) 
            # Assume the second time step is the same as the first.
            start_time = numpy.int32(self._record_data['sim_time'][0] + last_time)
            
            for block_number in xrange(nblocks):

                n_spillets = self._record_data['n_oil_recs'][block_number]
                
            
                offsets = {
                    OilModelDirectAccessOMReader.OIL_SPILLETS    : (0 ) * self.OML_RECORD_SIZE,
                }

                counts = {
                    OilModelDirectAccessOMReader.OIL_SPILLETS    : n_spillets,
                }

            
                tstep_bytes = (n_spillets ) * self.OML_RECORD_SIZE
            
                buffer = oml_file.read(tstep_bytes)
            
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
                    
                    
#                     if spillet_type == OilModelDirectAccessReader.SURFACE_SPILLETS:
#                         #if (particles['nwhere']!=1).any():
#                         #   logger.info(particles[particles['nwhere']!=1])
#                         particles = particles[particles['nwhere']==1]
#                         
#                         if (particles['nwhere']==-1).any():
#                             raise PyStochIOError('OilModel Reader got a spillet in a boom (nwhere==-1). Booming is not implemented yet!')
# 

                    output[spillet_type] = particles


                yield output
            
    def get_surface_extents(self):
        return self.get_extents(2,(OilModelDirectAccessOMReader.OIL_SPILLETS,))

    def get_subsurface_extents(self):
        return self.get_extents(2,(OilModelDirectAccessOMReader.OIL_SPILLETS,))
            
            
            
    def count_nw_codes(self):
    
        counts = []
        for block in self.stream_record_blocks():
            tscnt = {}
            
            nw = block['oil spillets']['nwhere']
            for val in nw:
                tscnt[val] = tscnt.get(val,0) + 1
                
            counts.append(tscnt)
            
        return counts
            
    
    
            
            
            
