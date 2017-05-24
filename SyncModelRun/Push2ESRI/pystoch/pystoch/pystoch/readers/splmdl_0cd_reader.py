#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file splmdl_reader.py
@date 10/04/13
@description Implementation of the Spill Model 0CD File data reader
'''

import numpy
from pystoch import util 
from pystoch.datatypes import DT
from pystoch.readers.abstract_reader import AbstractParticleReader
from pystoch.exceptions import PyStochIOError
from pystoch.keywords import * # Import keywords

import logging
logger = logging.getLogger('pystoch.readers.splmdl_0cd_reader')

from pystoch.readers.splmdl_reader import SplModelDirectAccessReader


class SplModel0cdDirectAccessReader(SplModelDirectAccessReader):

    RECORD_FILE_SUFFIX = '0cl'
    DATA_FILE_SUFFIX = '0cd'
    reader_key = frozenset([DATA_FILE_SUFFIX,RECORD_FILE_SUFFIX])

    def set_record_size(self, version, npseudo):
    
        if version != -11:
            raise PyStocheIOError("Invalide version number in 0CL file: '%s'" % '.'.join([self.fname,RECORD_FILE_SUFFIX]))
        
        rec_size = 11*4 + 4*8 
            
        self.PCD_RECORD_SIZE = rec_size
        
        
    def create_surface_spillet_type(self, version_number, npseudo):
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
            ### Unknown number of npseudo components - must be defined when the header is read!
            ('sum_armass', DT.SPRECISION, 1),   #aromatic mass (metricTons = 1000kg)
            ('sum_almass', DT.SPRECISION, 1),   #aliphatic mass (metricTons = 1000kg)
            ('spillet_number', DT.INT32, 1),      #Spillet ID Number
            ('fwc', DT.SPRECISION, 1)             #Fraction Water Content 
            ])
        return SPLMDL_SURFACE_PARTICLE
   
                
    def create_subsurface_dissolved_spillet_type(self, version_number, npseudo):
        subsurface_dissolved_record_size = 4 + 2*8 + 4*4 
        SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE = numpy.dtype([
            ('particle_type', numpy.int32, 1),
            ('loc', DT.POINTDP2D, 1),
            ('zm',DT.SPRECISION,1),
            ('prtTime',DT.SPRECISION,1),
            ('cdaw',DT.SPRECISION,1),
            ('mass',DT.SPRECISION,1),
            ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_dissolved_record_size)
            ])    
        return SPLMDL_SUBSURFACE_DISSOLVED_PARTICLE

                
    def create_subsurface_residual_spillet_type(self, version_number, npseudo):
        subsurface_residual_record_size = 4 + 2*8 + 10*4 
        SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE = numpy.dtype([
            ('particle_type', numpy.int32, 1),
            ('loc', DT.POINTDP2D, 1),
            ('zm', DT.SPRECISION, 1),
            ('tInWC', DT.SPRECISION, 1),    #spillet's age (hours)
            ('diameter', DT.SPRECISION, 1), #representative droplet diameter (m)
            ('density', DT.SPRECISION, 1),
            ('mass', DT.SPRECISION, 1), 
            ('viscosity', DT.SPRECISION, 1),
            ('sum_armass', DT.SPRECISION, 1),
            ('sum_almass', DT.SPRECISION, 1),            
            ('spillet_number', DT.INT32, 1),      #Spillet ID Number
            ('fwc', DT.SPRECISION, 1),             #Fraction Water Content 
            ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_residual_record_size)
            ])
        return SPLMDL_SUBSURFACE_RESIDUAL_PARTICLE
          
    def create_tarball_spillet_type(self, version_number, npseudo):        
        subsurface_tarball_size = 4 + 2*8 + 10*4
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
            ('sum_armass', DT.SPRECISION, 1),
            ('sum_almass', DT.SPRECISION, 1),   
            ('spillet_number', DT.INT32, 1),      #Spillet ID Number
            ('fwc', DT.SPRECISION, 1),             #Fraction Water Content  
            ('junk', numpy.character, self.PCD_RECORD_SIZE - subsurface_tarball_size)
            ])
        return SPLMDL_TARBALL_PARTICLE  
                    
    def create_sediment_spillet_type(self, version_number, npseudo):
        # -8 or -9 or -10
        sediment_record_size = 4 + 2*8 + 10*4 
        SPLMDL_SEDIMENT_PARTICLE = numpy.dtype([
            ('particle_type', numpy.int32, 1),
            ('loc', DT.POINTDP2D, 1),
            ('zm',DT.SPRECISION,1),
            ('tInWC',DT.SPRECISION,1),
            ('diameter',DT.SPRECISION,1),
            ('density',DT.SPRECISION,1),
            ('mass',DT.SPRECISION,1),
            ('viscosity', DT.SPRECISION, 1),
            ### Unknown number of psuedo components - must be defined when the header is read!
            ('sum_armass',DT.SPRECISION,1),
            ('sum_almass',DT.SPRECISION,1),
            ('spillet_number', DT.INT32, 1),      #Spillet ID Number
            ('fwc', DT.SPRECISION, 1),             #Fraction Water Content 
            ('junk', numpy.character, self.PCD_RECORD_SIZE - sediment_record_size)
            ])
        return SPLMDL_SEDIMENT_PARTICLE
        
    def create_shoreline_spillet_type(self, version_number, npseudo):
        shoreline_record_size = 4 + 2*8 + + 2*4 + 6*4 
        SPLMDL_SHORELINE_PARTICLE = numpy.dtype([
            ('particle_type', numpy.int32, 1),
            ('loc', DT.POINTDP2D, 1),
            ('prev_loc', DT.POINTSP2D, 1),
            ('shoreline_width', DT.SPRECISION, 1),
            ('density', DT.SPRECISION, 1),
            ('mass', DT.SPRECISION, 1),
            ('water_content_fraction', DT.SPRECISION, 1), #fraction of water content in oil on shore
            ('sum_armass', DT.SPRECISION, 1),
            ('sum_almass', DT.SPRECISION, 1),
            ('junk', numpy.character, self.PCD_RECORD_SIZE - shoreline_record_size)
            ])
        return SPLMDL_SHORELINE_PARTICLE
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                