from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch.map_reduce_ops.thickest_spillet_op import thickest_spillet_op
from pystoch.datatypes import DT, Singleton
from pystoch.keywords import *


class ThickestSpilletTest(unittest.TestCase):

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
        
    def test_single_value(self):
    
        a = numpy.zeros((3,3),numpy.float32)
        co = thickest_spillet_op(a)

        # make a single value        
        block = numpy.zeros((1),DT.IDEAL_PARTICLE)
        block['mass'] = 10.0
        block['density'] = 5.0
        block['radius'] = numpy.sqrt(1.0/numpy.pi)
        index_pos = numpy.array([(1,1),],dtype=numpy.int32)
        weight = numpy.ones((1,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.float32)
        b[1,1] = 2.0
        assert_array_almost_equal(a, b)
        
    def test_array_of_value(self):
        a = numpy.zeros((3,3),numpy.float32)
        co = thickest_spillet_op(a)

        # make a single value        
        block = numpy.zeros((3),DT.IDEAL_PARTICLE) 
        block['mass'] = (11.0, 5.0, 100.0)
        block['density'] = 5.0
        block['radius'] = numpy.sqrt(1.0/numpy.pi)    
        index_pos = numpy.array([(1,1),(1,2),(1,1)],dtype=numpy.int32)
        weight = numpy.ones((3,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.float32)
        b[1,1] = 19.99999809
        b[1,2] = 0.99999988
        assert_array_almost_equal(a, b)
        
    def test_array_of_indicies(self):
    
        a = numpy.zeros((3,3),numpy.float32)
        co = thickest_spillet_op(a)

        # make a single value        
        block = numpy.zeros((1),DT.IDEAL_PARTICLE)
        block['mass'] = 10.0
        block['density'] = 5.0
        block['radius'] = numpy.sqrt(1.0/numpy.pi)    

        index_pos = numpy.array([(1,1),(1,2),(1,1)],dtype=numpy.int32)
        weight = numpy.ones((3,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.float32)
        b[1,1] = 1.99999976
        b[1,2] = 1.99999976
        assert_array_equal(a, b)
        
        # Send it again
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.float32)
        b[1,1] = 1.99999976
        b[1,2] = 1.99999976
        assert_array_equal(a, b)
    
    