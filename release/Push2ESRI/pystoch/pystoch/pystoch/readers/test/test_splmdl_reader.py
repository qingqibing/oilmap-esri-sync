from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch import util
from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.readers.splmdl_reader import SplModelDirectAccessReader

import logging
logger = logging.getLogger('pystoch.readers.test.test_splmdl_reader')

class SplModelReaderTest(unittest.TestCase):

    def setUp(self):
        """
        Setup test
        """
        DT(ndims=2,precision=numpy.float32,location_units='LatLon')
        
    
    def tearDown(self):
        """
        Tear down test
        """
        Singleton._instances.clear()
    

    def test_read_file(self):
    
        fbase = './trajectory_data/simap/3D_TEST1/3D_TEST1_S0001'

        file_reader =  SplModelDirectAccessReader(fbase)

        g = file_reader.stream_record_blocks()
    
        cnt = 0
        for block in g:
            cnt += 1
            
            surf_p = block.get(SplModelDirectAccessReader.SURFACE_SPILLETS)
            assert_is_instance(surf_p, numpy.ndarray)
            assert((surf_p['loc'][:,0]<-90.).all())
            assert((surf_p['loc'][:,0]>-98).all())
            
    
            subsurf_dis = block.get(SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS)
            assert_is_instance(subsurf_dis, numpy.ndarray)
            assert((subsurf_dis['loc'][:,0]<-90.).all())
            assert((subsurf_dis['loc'][:,0]>-98).all())
    
            subsurf_res = block.get(SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS)
            assert_is_instance(subsurf_res, numpy.ndarray)
            print subsurf_res['loc']
            assert((subsurf_res['loc'][:,0]<-90.).all())
            assert((subsurf_res['loc'][:,0]>-98).all())
    
            sediment_p = block.get(SplModelDirectAccessReader.SEDIMENT_SPILLETS)
            assert_is_instance(sediment_p, numpy.ndarray)
            assert((sediment_p['loc'][:,0]<-90.).all())
            assert((sediment_p['loc'][:,0]>-98).all())
    
            shoreline_p = block.get(SplModelDirectAccessReader.SHORELINE_SPILLETS)
            assert_is_instance(shoreline_p, numpy.ndarray)
            assert((shoreline_p['loc'][:,0]<-90.).all())
            assert((shoreline_p['loc'][:,0]>-98).all())
    
    
        assert_equal(cnt,145)



    def test_particle_types(self):
    
        fbase = './trajectory_data/simap/3D_TEST1/3D_TEST1_S0001'

        file_reader =  SplModelDirectAccessReader(fbase)

        tup = (SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS,
                SplModelDirectAccessReader.SEDIMENT_SPILLETS)
        g = file_reader.stream_record_blocks(output_definition=tup)
    
        cnt = 0
        for block in g:
            cnt += 1
            
            sub_dis = block.get(SplModelDirectAccessReader.SUBSURFACE_DISSOLVED_SPILLETS)
            assert_is_instance(sub_dis, numpy.ndarray)
    
            sed = block.get(SplModelDirectAccessReader.SEDIMENT_SPILLETS)
            assert_is_instance(sed, numpy.ndarray)
        
            assert_is(block.get(SplModelDirectAccessReader.SURFACE_SPILLETS), None)
            assert_is(block.get(SplModelDirectAccessReader.SUBSURFACE_RESIDUAL_SPILLETS), None)
            assert_is(block.get(SplModelDirectAccessReader.SHORELINE_SPILLETS), None)
    
    
        assert_equal(cnt,145)





    def test_get_surface_extents(self):
    
        fbase = './trajectory_data/simap/3D_TEST1/3D_TEST1_S0001'

        file_reader =  SplModelDirectAccessReader(fbase)
        
        extents = file_reader.get_surface_extents()
        
        # use print if the value changes to get the correct one...
        #print extents
        assert_equal(extents['ur'][0], [-93.75031411802539, 26.66173803043253])
        assert_equal(extents['ll'][0], [-94.18028580350175, 25.556892383411906])


    def test_get_subsurface_extents(self):
    
        fbase = './trajectory_data/simap/3D_TEST1/3D_TEST1_S0001'

        file_reader =  SplModelDirectAccessReader(fbase)
        
        extents = file_reader.get_subsurface_extents()
        
        # use print if the value changes to get the correct one...
        print extents
        assert_equal(extents['ur'][0], [-93.78352646189451, 26.73507521394121])
        assert_equal(extents['ll'][0], [-94.18946347461868, 25.557863595120416])


