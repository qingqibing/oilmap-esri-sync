#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file splmdl_reader.py
@date 03/11/13
@description Implementation of the Spill Model PCD File data reader
'''
import numpy
from pystoch import util 
from pystoch.datatypes import DT
from pystoch.readers.abstract_reader import AbstractParticleReader
from pystoch.exceptions import PyStochIOError
from pystoch.keywords import * # Import keywords

import logging
logger = logging.getLogger('pystoch.readers.splmdl_reader')


class SplModelDirectAccessReader(AbstractParticleReader):

    RECORD_FILE_SUFFIX = 'pcl'
    DATA_FILE_SUFFIX = 'pcd'

    reader_key = frozenset([DATA_FILE_SUFFIX,RECORD_FILE_SUFFIX])
    supported_versions = set( (-8, -9, -10, -11) )


    SPLMDL_PCL_LOOKUP_RECORD_TYPE = numpy.dtype([
                            ('sim_time', numpy.int32, 1) , # current sim time in minutes since 1979
                            ('model_time', numpy.float32, 1),      # model time in hours since sim start
                            ('record_start', numpy.int32, 1),
                            ])
                        
    SPLMDL_PCL_HEADER_RECORD_TYPE = numpy.dtype([
                            ('pcd_version', numpy.int32, 1) ,
                            ('npseudo', numpy.int16, 1),
                            ('sim_time', numpy.int32, 1),    # simulation start time in minutes since 1979
                            ('junk',numpy.character,2),
                            ])


    PCL_RECORD_SIZE = 12


    # Define the possible values to put in the generator result
    SURFACE_SPILLETS                = 'Surface Spillets'
    SUBSURFACE_DISSOLVED_SPILLETS   = 'Subsurface Dissolved Spillets'
    SUBSURFACE_RESIDUAL_SPILLETS    = 'Subsurface Residual Spillets'
    TARBALL_SPILLETS                = 'Tarball Spillets'
    SEDIMENT_SPILLETS               = 'Sediment Spillets'
    SHORELINE_SPILLETS              = 'Shoreline Spillets'
    
    product_spillet_map = {}
    product_spillet_map[SURFACE] = [SURFACE_SPILLETS]
    product_spillet_map[SUBSURFACE] = [SUBSURFACE_DISSOLVED_SPILLETS, SUBSURFACE_RESIDUAL_SPILLETS]
    product_spillet_map[SHORE] = [SHORELINE_SPILLETS]

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        """
        # Ensure all constructors are called properly
        super(SplModelDirectAccessReader, self).__init__(*args, **kwargs)
    
        self._load_meta()
        
    def set_record_size(self, version, npseudo):
    
        if version == -11:
            rec_size = 9*4 + 4*8 + 2*4*npseudo        
        elif version == -10:
            rec_size = 7*4 + 4*8 + 2*4 * npseudo
        else:
            rec_size = 6*4 + 4*8 + 2*4 * npseudo
            
        self.PCD_RECORD_SIZE = rec_size
    
    def _load_meta(self):
        
        record_data = None
        header_data = None

        version_number = None

        with open('.'.join([self.fname,self.RECORD_FILE_SUFFIX]), 'rb') as pcl_file:
            
            # Read the header record
            header_data = numpy.fromfile(pcl_file,dtype=self.SPLMDL_PCL_HEADER_RECORD_TYPE,count=1)
            
            # Read the rest of the entries
            record_data = numpy.fromfile(pcl_file,dtype=self.SPLMDL_PCL_LOOKUP_RECORD_TYPE,count=-1)
            
        if header_data is None:
            raise PyStocheIOError("Could not read the header from the file: '%s'" % '.'.join([self.fname,self.RECORD_FILE_SUFFIX]))
            
        version_number = header_data[0]['pcd_version']
        if not version_number in self.supported_versions :
            raise NotImplementedError('Can not read pcd file version "%d"' % version_number)
        
        self._version_number = version_number
            
        if record_data is None:
            raise PyStochIOError("Could not read data from PCL file:'%s'" % '.'.join([self.fname,self.RECORD_FILE_SUFFIX]))
        
        if len(record_data) == 0 :
            raise PyStochIOError("PCL file '%s' is empty - no records!" % '.'.join([self.fname,self.RECORD_FILE_SUFFIX]))
        
        ### CONVERT FROM FORTRAN TO C INDEXING! ###
        record_data['record_start'] -= 1
        
        self._record_data = record_data
        
        npseudo = header_data[0]['npseudo']
        

        self.set_record_size(version_number, npseudo)
        
        
        #logger.info('record_header: \n%s' % header_data)
        #logger.info('record_lookup: \n%s' % record_data)
        if version_number == -11:
            lookup_size = 19*4
            self._SPLMDL_PCD_LOOKUP_RECORD_TYPE = numpy.dtype([
                ('surface_records', numpy.int32, 1),
                ('subsurface_dissolved_records', numpy.int32, 1) ,
                ('subsurface_residual_records', numpy.int32, 1) ,
                ('tarball_records', numpy.int32, 1) ,
                ('sediment_records', numpy.int32, 1) ,
                ('shoreline_records', numpy.int32, 1),
                ('wave_height',DT.SPRECISION,1),
                ('wind_average',DT.SPRECISION,1),
                ('velocity_max',DT.SPRECISION,1),
                ('surface_extent', DT.extent_type(ndims=2,prec=DT.SPRECISION), 1), #Must reorder from: #XMIN, XMAX, YMIN, YMAX
                ('subsurface_extent', DT.extent_type(ndims=3,prec=DT.SPRECISION), 1), #Must reorder from: #XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('junk', numpy.character, self.PCD_RECORD_SIZE - lookup_size),
                ])
        elif version_number == -10:
            lookup_size = 18*4
            self._SPLMDL_PCD_LOOKUP_RECORD_TYPE = numpy.dtype([
                ('surface_records', numpy.int32, 1),
                ('subsurface_dissolved_records', numpy.int32, 1) ,
                ('subsurface_residual_records', numpy.int32, 1) ,
                ('sediment_records', numpy.int32, 1) ,
                ('shoreline_records', numpy.int32, 1),
                ('wave_height',DT.SPRECISION,1),
                ('wind_average',DT.SPRECISION,1),
                ('velocity_max',DT.SPRECISION,1),
                ('surface_extent', DT.extent_type(ndims=2,prec=DT.SPRECISION), 1), #Must reorder from: #XMIN, XMAX, YMIN, YMAX
                ('subsurface_extent', DT.extent_type(ndims=3,prec=DT.SPRECISION), 1), #Must reorder from: #XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('junk', numpy.character, self.PCD_RECORD_SIZE - lookup_size),
                ])
        else: # -8 or -9
            lookup_size = 8*4
            self._SPLMDL_PCD_LOOKUP_RECORD_TYPE = numpy.dtype([
                ('surface_records', numpy.int32, 1),
                ('subsurface_dissolved_records', numpy.int32, 1) ,
                ('subsurface_residual_records', numpy.int32, 1) ,
                ('sediment_records', numpy.int32, 1) ,
                ('shoreline_records', numpy.int32, 1),
                ('wave_height',DT.SPRECISION,1),
                ('wind_average',DT.SPRECISION,1),
                ('velocity_max',DT.SPRECISION,1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('junk', numpy.character, self.PCD_RECORD_SIZE - lookup_size),
                ])
                        
        # particle_type is 0
        SPLMDL_SURFACE_PARTICLE = self.create_surface_spillet_type(version_number, npseudo)

        # particle_type is -1        
        SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE = self.create_subsurface_dissolved_spillet_type(version_number, npseudo)
        
        
        # particle_type is -2
        SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = self.create_subsurface_residual_spillet_type(version_number, npseudo)

        # particle_type is -3
        SPLMDL_TARBALL_PARTICLE = self.create_tarball_spillet_type(version_number, npseudo)

        # particle_type is -12
        SPLMDL_SEDIMENT_PARTICLE = self.create_sediment_spillet_type(version_number, npseudo)

        
        SPLMDL_SHORELINE_PARTICLE = self.create_shoreline_spillet_type(version_number, npseudo)
        
        self.spillet_types = {
            SplModelDirectAccessReader.SURFACE_SPILLETS     : {
                'dtype'  : SPLMDL_SURFACE_PARTICLE,
                'offset' : None,
                'count'  : None},
            SplModelDirectAccessReader.SHORELINE_SPILLETS   : {
                'dtype'  : SPLMDL_SHORELINE_PARTICLE,
                'offset' : None,
                'count'  : None},
            SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS  : {
                'dtype'  : SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE,
                'offset' : None,
                'count'  : None},
            SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS  : {
                'dtype'  : SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE,
                'offset' : None,
                'count'  : None},
            SplModelDirectAccessReader.TARBALL_SPILLETS :  {
                'dtype'  : SPLMDL_TARBALL_PARTICLE,
                'offset' : None,
                'count'  : None},
            SplModelDirectAccessReader.SEDIMENT_SPILLETS  : {
                'dtype'  : SPLMDL_SEDIMENT_PARTICLE,
                'offset' : None,
                'count'  : None},
            }
                
                
        if version_number <= -11 and SplModelDirectAccessReader.TARBALL_SPILLETS not in self.product_spillet_map[SURFACE]:
            # Modify the class variable based on whether this is version 11 or not... 
            # Not a great way to deal with this. Better ideas?
            self.product_spillet_map[SURFACE].append(SplModelDirectAccessReader.TARBALL_SPILLETS)
                
            self.product_spillet_map[SUBSURFACE].append(SplModelDirectAccessReader.TARBALL_SPILLETS)
        
    def create_surface_spillet_type(self, version_number, npseudo):
        SPLMDL_SURFACE_PARTICLE = None
        if version_number == -11:
            SPLMDL_SURFACE_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),             #lon, lat (degrees)
                ('prev_loc', DT.POINTDP2D,  1),       #lon, lat (degrees)
                ('lifetime', DT.SPRECISION, 1),       #age (hours)
                ('radius', DT.SPRECISION, 1),         #radius (meters)
                ('prev_radius', DT.SPRECISION, 1),    #radius (meters)
                ('density', DT.SPRECISION, 1),        #density (g/cm3 = MT/m3)
                ('mass', DT.SPRECISION, 1),           #mass (metricTons = 1000kg)
                ('viscosity', DT.SPRECISION, 1),      #viscosity (cP)
                ('armass', DT.SPRECISION, npseudo),   #aromatic mass (metricTons = 1000kg)
                ('almass', DT.SPRECISION, npseudo),   #aliphatic mass (metricTons = 1000kg)
                ('spillet_number', DT.INT32, 1),      #Spillet ID Number
                ('fwc', DT.SPRECISION, 1)             #Fraction Water Content  
                ])
        elif version_number == -10:
            SPLMDL_SURFACE_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),             #lon, lat (degrees)
                ('prev_loc', DT.POINTDP2D,  1),       #lon, lat (degrees)
                ('lifetime', DT.SPRECISION, 1),       #age (hours)
                ('radius', DT.SPRECISION, 1),         #radius (meters)
                ('prev_radius', DT.SPRECISION, 1),    #radius (meters)
                ('density', DT.SPRECISION, 1),        #density (g/cm3 = MT/m3)
                ('mass', DT.SPRECISION, 1),           #mass (metricTons = 1000kg)
                ('viscosity', DT.SPRECISION, 1),      #viscosity (cP)
                ('armass', DT.SPRECISION, npseudo),   #aromatic mass (metricTons = 1000kg)
                ('almass', DT.SPRECISION, npseudo)    #aliphatic mass (metricTons = 1000kg)
                ])
        elif version_number in (-8, -9):
            SPLMDL_SURFACE_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),           #lon, lat (degrees)
                ('prev_loc', DT.POINTDP2D, 1),      #lon, lat (degrees)
                ('lifetime',DT.SPRECISION,1),       #age (hours)
                ('radius',DT.SPRECISION,1),         #radius (meters)
                ('prev_radius',DT.SPRECISION,1),    #radius (meters)
                ('density',DT.SPRECISION,1),        #density (g/cm3 = MT/m3)
                ('mass',DT.SPRECISION,1),           #mass (metricTons = 1000kg)
                ('armass',DT.SPRECISION,npseudo),   #aromatic mass (metricTons = 1000kg)
                ('almass',DT.SPRECISION,npseudo)    #aliphatic mass (metricTons = 1000kg)
                ])
        return SPLMDL_SURFACE_PARTICLE
        
    def create_subsurface_dissolved_spillet_type(self, version_number, npseudo):
        SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE = None
        if version_number in (-9,-10,-11):
            subsurface_dissolved_record_size = 4 + 2*8 + 4*4 + 2*4*npseudo
            SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('prtTime',DT.SPRECISION,1),
                ('cdaw',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass',DT.SPRECISION,npseudo),
                ('CDbyAR',DT.SPRECISION,npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_dissolved_record_size)
                ])
        elif version_number == -8:
            subsurface_dissolved_record_size = 4 + 2*8 + 4*4 + 1*4*npseudo
            SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('prtTime',DT.SPRECISION,1),
                ('cdaw',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass',DT.SPRECISION,npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_dissolved_record_size)
                ])
        return SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE

    def create_subsurface_residual_spillet_type(self, version_number, npseudo):
        SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = None
        if version_number == -11:
            subsurface_residual_record_size = 4 + 2*8 + 8*4 + 2*4*npseudo
            SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm', DT.SPRECISION, 1),
                ('tInWC', DT.SPRECISION, 1),    #spillet's age (hours)
                ('diameter', DT.SPRECISION, 1), #representative droplet diameter (m)
                ('density', DT.SPRECISION, 1),
                ('mass', DT.SPRECISION, 1), 
                ('viscosity', DT.SPRECISION, 1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass', DT.SPRECISION, npseudo),
                ('almass', DT.SPRECISION, npseudo),
                ('spillet_number', DT.INT32, 1),      #Spillet ID Number
                ('fwc', DT.SPRECISION, 1),             #Fraction Water Content  
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_residual_record_size)
                ])
        if version_number == -10:
            subsurface_residual_record_size = 4 + 2*8 + 6*4 + 2*4*npseudo
            SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm', DT.SPRECISION, 1),
                ('tInWC', DT.SPRECISION, 1),    #spillet's age (hours)
                ('diameter', DT.SPRECISION, 1), #representative droplet diameter (m)
                ('density', DT.SPRECISION, 1),
                ('mass', DT.SPRECISION, 1), 
                ('viscosity', DT.SPRECISION, 1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass', DT.SPRECISION, npseudo),
                ('almass', DT.SPRECISION, npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_residual_record_size)
                ])
        elif version_number in (-8, -9): # -8 or -9
            subsurface_residual_record_size = 4 + 2*8 + 5*4 + 2*4*npseudo
            SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('tInWC',DT.SPRECISION,1),
                ('diameter',DT.SPRECISION,1),
                ('density',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass',DT.SPRECISION,npseudo),
                ('almass',DT.SPRECISION,npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_residual_record_size)
                ])
        return SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE
        
    def create_tarball_spillet_type(self, version_number, npseudo):
        SPLMDL_TARBALL_PARTICLE = None
        if version_number == -11:
            subsurface_tarball_size = 4 + 2*8 + 8*4 + 2*4*npseudo
            SPLMDL_TARBALL_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm', DT.SPRECISION, 1),
                ('tInWC', DT.SPRECISION, 1),    #spillet's age (hours)
                ('diameter', DT.SPRECISION, 1), #representative droplet diameter (m)
                ('density', DT.SPRECISION, 1),
                ('mass', DT.SPRECISION, 1), 
                ('viscosity', DT.SPRECISION, 1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass', DT.SPRECISION, npseudo),
                ('almass', DT.SPRECISION, npseudo),
                ('spillet_number', DT.INT32, 1),      #Spillet ID Number
                ('fwc', DT.SPRECISION, 1),             #Fraction Water Content  
                ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_tarball_size)
                ])
        return SPLMDL_TARBALL_PARTICLE
        
    def create_sediment_spillet_type(self, version_number, npseudo):
        # -8 or -9 or -10
        SPLMDL_SEDIMENT_PARTICLE = None
        if version_number in (-8, -9):
            sediment_record_size = 4 + 2*8 + 5*4 + 2*4*npseudo
            SPLMDL_SEDIMENT_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('tInWC',DT.SPRECISION,1),
                ('diameter',DT.SPRECISION,1),
                ('density',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass',DT.SPRECISION,npseudo),
                ('almass',DT.SPRECISION,npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - sediment_record_size)
                ])
        elif version_number == -10:
            sediment_record_size = 4 + 2*8 + 6*4 + 2*4*npseudo
            SPLMDL_SEDIMENT_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('tInWC',DT.SPRECISION,1),
                ('diameter',DT.SPRECISION,1),
                ('density',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ('viscosity', DT.SPRECISION, 1),
                ('armass',DT.SPRECISION,npseudo),
                ('almass',DT.SPRECISION,npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - sediment_record_size)
                ])
        elif version_number == -11:
            sediment_record_size = 4 + 2*8 + 8*4 + 2*4*npseudo
            SPLMDL_SEDIMENT_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('zm',DT.SPRECISION,1),
                ('tInWC',DT.SPRECISION,1),
                ('diameter',DT.SPRECISION,1),
                ('density',DT.SPRECISION,1),
                ('mass',DT.SPRECISION,1),
                ('viscosity', DT.SPRECISION, 1),
                ('armass',DT.SPRECISION,npseudo),
                ('almass',DT.SPRECISION,npseudo),
                ('spillet_number', DT.INT32, 1),      #Spillet ID Number
                ('fwc', DT.SPRECISION, 1),             #Fraction Water Content  
                ('junk', numpy.character, self.PCD_RECORD_SIZE - sediment_record_size)
                ])
        return SPLMDL_SEDIMENT_PARTICLE
        
    def create_shoreline_spillet_type(self, version_number, npseudo):
        SPLMDL_SHORELINE_PARTICLE = None
        if version_number in (-10, -11):    
            shoreline_record_size = 4 + 2*8 + 2*4 + 4*4 + 2*4*npseudo
            SPLMDL_SHORELINE_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('prev_loc', DT.POINTSP2D, 1),
                ('shoreline_width', DT.SPRECISION, 1),
                ('density', DT.SPRECISION, 1),
                ('mass', DT.SPRECISION, 1),
                ('fwc', DT.SPRECISION, 1), #fraction of water content in oil on shore
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass', DT.SPRECISION, npseudo),
                ('almass', DT.SPRECISION, npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - shoreline_record_size)
                ])
        elif version_number >= -9 :
            shoreline_record_size = 4 + 2*8 + + 2*4 + 3*4 + 2*4*npseudo
            SPLMDL_SHORELINE_PARTICLE = numpy.dtype([
                ('particle_type', numpy.int32, 1),
                ('loc', DT.POINTDP2D, 1),
                ('prev_loc', DT.POINTSP2D, 1),
                ('shoreline_width', DT.SPRECISION, 1),
                ('density', DT.SPRECISION, 1),
                ('mass', DT.SPRECISION, 1),
                ### Unknown number of psuedo components - must be defined when the header is read!
                ('armass', DT.SPRECISION, npseudo),
                ('almass', DT.SPRECISION, npseudo),
                ('junk', numpy.character, self.PCD_RECORD_SIZE - shoreline_record_size)
                ])
        return SPLMDL_SHORELINE_PARTICLE
        
        
        
    def stream_record_blocks(self,output_definition=None):
        """
        A generator function which yields blocks of particle records to the caller
        """
        if output_definition is None:
            # default to output everything
            output_definition = tuple(self.spillet_types.keys())
        
        # pre-allocations 
        particle_records = numpy.zeros(1,dtype=self._SPLMDL_PCD_LOOKUP_RECORD_TYPE)


        nblocks = len(self._record_data)
        
        # a variable to save the last time in for estimating deltaT. Use native units of the file - minutes
        last_time = numpy.int32(self._record_data['sim_time'][0] - self._record_data['sim_time'][1]) 
        # Assume the second time step is the same as the first.
        start_time = numpy.int32(self._record_data['sim_time'][0] + last_time)
        
        with open('.'.join([self.fname,self.DATA_FILE_SUFFIX]),'rb') as pcd_file:
        
            
            for block_number in xrange(nblocks):

                # Read the lookup record from the pcd file
                record_start = self._record_data['record_start'][block_number]
                pcd_file.seek(record_start*self.PCD_RECORD_SIZE)
                particle_records[...] = numpy.fromfile(pcd_file, dtype=self._SPLMDL_PCD_LOOKUP_RECORD_TYPE, count=1)
                
                if self._version_number <= -10:
                    # remap the extent data from the PCD order to the Dtype order and direction
                    #XMIN, XMAX, YMIN, YMAX => RU, LL 
                    #XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX, => RUU, LLL
                    
                    surface_extent = particle_records['surface_extent'][0].copy()
                    particle_records['surface_extent']['ur'] = (surface_extent['ll'][1], surface_extent['ur'][1])
                    particle_records['surface_extent']['ll'] = (surface_extent['ll'][0], surface_extent['ur'][0])
                    
                    subsurface_extent = particle_records['subsurface_extent'][0].copy()
                    # note extents are upward positive!
                    particle_records['subsurface_extent']['ur'] = (subsurface_extent['ll'][1], subsurface_extent['ur'][0], -subsurface_extent['ur'][1])
                    particle_records['subsurface_extent']['ll'] = (subsurface_extent['ll'][0], subsurface_extent['ll'][2], -subsurface_extent['ur'][2])
                              
               
                # Now sort out the mess...
                output = {}
                
                output[METADATA] = {
                    TIME:{
                        ETIME: 60 * numpy.int32(self._record_data['sim_time'][block_number] - start_time),
                        DTIME: 60 * numpy.int32(self._record_data['sim_time'][block_number] - last_time),
                        BTIME: self._record_data['sim_time'],
                        },
                   BLOCK:{
                        N_OF_M_IN_F: (block_number,nblocks),
                        N_OF_M_IN_TS: (1, 1), # all in one timestep
                        "PCD_RECORD_DATA":particle_records
                        },
                    FILE_NAME:self.fname
                    }
                last_time = numpy.int32(self._record_data['sim_time'][block_number])

                if len(output_definition) > 0:
                    # Someday change this to read only what we need?
                       
                    # Read the all the records
                    nsurface_particles               = particle_records[0]['surface_records']
                    nsubsurface_dissolved_particles  = particle_records[0]['subsurface_dissolved_records']
                    nsubsurface_residual_particles   = particle_records[0]['subsurface_residual_records']

                    ntarball_particles = 0
                    if self._version_number <= -11: 
                        ntarball_particles   = particle_records[0]['tarball_records']
                        
                    nsediment_particles              = particle_records[0]['sediment_records']
                    nshoreline_particles             = particle_records[0]['shoreline_records']
                
                    tstep_bytes = (nsurface_particles +
                        nsubsurface_dissolved_particles +
                        nsubsurface_residual_particles +
                        ntarball_particles +
                        nsediment_particles +
                        nshoreline_particles) * self.PCD_RECORD_SIZE
                
                
                    buffer = pcd_file.read(tstep_bytes) # make a string buffer containing all of these records
                
                    offsets = {
                        SplModelDirectAccessReader.SURFACE_SPILLETS    : (0 ) * self.PCD_RECORD_SIZE,
                        SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS : (nsurface_particles ) * self.PCD_RECORD_SIZE,
                        SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS : (nsurface_particles + nsubsurface_dissolved_particles) * self.PCD_RECORD_SIZE,
                        SplModelDirectAccessReader.TARBALL_SPILLETS : (nsurface_particles + nsubsurface_dissolved_particles + nsubsurface_residual_particles) * self.PCD_RECORD_SIZE,
                        SplModelDirectAccessReader.SEDIMENT_SPILLETS : (nsurface_particles + nsubsurface_dissolved_particles + nsubsurface_residual_particles + ntarball_particles) * self.PCD_RECORD_SIZE,
                        SplModelDirectAccessReader.SHORELINE_SPILLETS : (nsurface_particles + nsubsurface_dissolved_particles + nsubsurface_residual_particles + ntarball_particles + nsediment_particles) * self.PCD_RECORD_SIZE,
                    }

                    counts = {
                        SplModelDirectAccessReader.SURFACE_SPILLETS                 : nsurface_particles,
                        SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS    : nsubsurface_dissolved_particles,
                        SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS     : nsubsurface_residual_particles,
                        SplModelDirectAccessReader.TARBALL_SPILLETS                 : ntarball_particles,
                        SplModelDirectAccessReader.SEDIMENT_SPILLETS                : nsediment_particles,
                        SplModelDirectAccessReader.SHORELINE_SPILLETS               : nshoreline_particles,
                    }

                
                    for spillet_type in output_definition:

                        # need to actually read some spillet data
                        reader_args=self.spillet_types[spillet_type].copy()
                
                        reader_args['count'] = counts[spillet_type]
                        reader_args['offset'] = offsets[spillet_type]
                
                        particles = numpy.frombuffer(buffer, **reader_args)
                        output[spillet_type] = particles



                #logger.info(util.pretty_print(output))

                yield output
                
#     @util.coroutine
#     def _extents_coroutine(self,ndims):
#     
#         result = DT.extents(ndims=ndims, prec=DT.DPRECISION)
#     
#         key = 'surface_extent'
#         if ndims == 3: 
#             key = 'subsurface_extent'
#         
#         while True:      
#             
#             block = (yield result)
#     
#             particle_records = block[METADATA][BLOCK]["PCD_RECORD_DATA"]
#         
#             # Add a little margin to the actual value...
#             pmin = particle_records[key]['ll']
#             pmax = particle_records[key]['ur']
#             
#             if (pmin == 0).all() & (pmax == 0).all():
#                 logger.warn('Skipping bad extents data in version -10 PCD file')
#                 continue
#             
#             result['ll'][0] = numpy.minimum(result['ll'][0], pmin - 0.001*abs(pmin))
#             result['ur'][0] = numpy.maximum(result['ur'][0], pmax + 0.001*abs(pmax))
#      
#             
#     def get_extents(self,ndims, spillets=None):
#         """
#         spillets is a list/tuple of the types of spillets to calculate the extent over
#         #@todo Will crash if you mix spillets with 2d and 3d coordinates!
#         """
#         
#         if self._version_number == -10:
#             # Use special new metadata to get extents!
#             
#         
#             ext_co = self._extents_coroutine(ndims)
#         
#         
#             for block in self.stream_record_blocks(tuple()):
#                 extents = ext_co.send(block)
#     
#             return extents
#         else:
#             return super(SplModelDirectAccessReader, self).get_extents(ndims, spillets)


            
        
    def get_surface_extents(self):
        return self.get_extents(2,(SplModelDirectAccessReader.SURFACE_SPILLETS,))

    def get_subsurface_extents(self):
        return self.get_extents(2,(SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS, SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS))
            

            
            

            
            
            
            
            
            
            
