from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch import util
from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.readers.oilmdl_reader import OilModelDirectAccessReader

import logging
logger = logging.getLogger('pystoch.readers.test.test_oilmdl_reader')

class OilModelReaderTest(unittest.TestCase):

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
    
        fbase = './trajectory_data/oilmap/2D_TEST1/2D_TEST1_s002'

        file_reader =  OilModelDirectAccessReader(fbase)

        g = file_reader.stream_record_blocks()
    
        cnt = 0
        for block in g:
            cnt += 1
            
            surf_p = block.get(OilModelDirectAccessReader.SURFACE_SPILLETS)
            assert_is_instance(surf_p, numpy.ndarray)
            assert((surf_p['loc'][:,0]<13).all())
            assert((surf_p['loc'][:,0]>10.5).all())
            
            shore_p = block.get(OilModelDirectAccessReader.SHORELINE_SPILLETS)
            assert_is_instance(shore_p, numpy.ndarray)
            assert((shore_p['loc'][:,0]<13).all())
            assert((shore_p['loc'][:,0]>11).all())
            
    
        assert_equal(cnt,146)

        g = file_reader.stream_record_blocks([OilModelDirectAccessReader.SURFACE_SPILLETS,])
    
        cnt = 0
        for block in g:
            cnt += 1
            
            surf_p = block.get(OilModelDirectAccessReader.SURFACE_SPILLETS)
            assert_is_instance(surf_p, numpy.ndarray)
            assert((surf_p['loc'][:,0]<13).all())
            assert((surf_p['loc'][:,0]>10.5).all())
            
            shore_p = block.get(OilModelDirectAccessReader.SHORELINE_SPILLETS)
            assert_is(shore_p, None)
            
        assert_equal(cnt,146)


    def test_get_surface_extents(self):
    
        fbase = './trajectory_data/oilmap/2D_TEST1/2D_TEST1_s002'

        file_reader =  OilModelDirectAccessReader(fbase)
        
        extents = file_reader.get_surface_extents()
        #print extents
        assert_equal(extents['ur'][0], [12.111989703210389, -5.990171015739441])
        assert_equal(extents['ll'][0], [11.940183021485787, -6.882050547120684])
        
        
    def test_get_subsurface_extents(self):
    
        fbase = './trajectory_data/oilmap/3D_TEST1/3D_TEST1_s002'

        file_reader =  OilModelDirectAccessReader(fbase)
        
        extents = file_reader.get_subsurface_extents()
        print extents
        assert_equal(extents['ur'][0], [12.177623808167088, -6.049693190574646])
        assert_equal(extents['ll'][0], [11.934229367702432, -6.934055744392753])
        
        
        