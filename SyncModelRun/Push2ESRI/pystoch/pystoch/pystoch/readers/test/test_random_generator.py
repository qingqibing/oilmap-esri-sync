from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch import util
from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.readers.random_generator import RandomWalkGenerator
from pystoch.keywords import *

import logging
logger = logging.getLogger('pystoch.readers.test.test_random_generator')


class RandomGeneratorTestSP2D(unittest.TestCase):

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
    
    def test_random_generatore_sizes(self):
    
        blocksize = 50
        nblocks = 100
        random_file =  RandomWalkGenerator('noName',
                                            nblocks =nblocks,
                                            blocksize=blocksize
                                            )
        
        g = random_file.stream_record_blocks()
        
        cnt = 0
        for block in g:
            for key,value in block.iteritems():
                if key is METADATA:
                    assert_equal(value[TIME], {ETIME: numpy.int32(3600*(cnt+1)), DTIME:numpy.int32(3600)})
                else:
                    assert_equal(len(value),blocksize)
            cnt +=1

            
        assert_equal(cnt,nblocks)
        
        
    def test_random_generator_limits(self):
        
        nblocks = 100
        blocksize = 2000
        
        random_file =  RandomWalkGenerator('noName',
                                            nblocks=nblocks,
                                            blocksize=blocksize
                                            )
        
        g = random_file.stream_record_blocks()
                
        for block in g:
        
            for key,particles in block.iteritems():
                
                if key is not METADATA:
                    max_loc = numpy.max(particles['loc'])
                    min_loc = numpy.min(particles['loc'])
                    
                    
        
        
    def test_random_extents(self):
    
        nblocks = 100
        blocksize = 2000 
        random_file =  RandomWalkGenerator('noName',
                                            nblocks=nblocks,
                                            blocksize=blocksize,
                                            )
        
        extents = random_file.get_surface_extents()

        ans = DT.extents(ndims=2, prec=DT.PRECISION,ll_default=(0,0), ur_default=(1,1))
        
        assert_array_equal(ans['ll'],extents['ll'])
        assert_array_equal(ans['ur'],extents['ur'])
        
        
        extents = random_file.get_subsurface_extents()

        ans = DT.extents(ndims=2, prec=DT.PRECISION,ll_default=(0,0,0), ur_default=(1,1,1))
        
        assert_array_equal(ans['ll'],extents['ll'])
        assert_array_equal(ans['ur'],extents['ur'])
        
        
        
        
class RandomGeneratorTestSP3D(RandomGeneratorTestSP2D):
    """
    Same tests in SP 3D!
    """
    
    def setUp(self):
        """
        Setup test
        """
        DT(ndims=3,precision=numpy.float32,location_units='LatLon')
        
        
class RandomGeneratorTestDP3D(RandomGeneratorTestSP2D):
    """
    Same tests in DP 3D!
    """
    
    def setUp(self):
        """
        Setup test
        """
        DT(ndims=3,precision=numpy.float64,location_units='LatLon')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        