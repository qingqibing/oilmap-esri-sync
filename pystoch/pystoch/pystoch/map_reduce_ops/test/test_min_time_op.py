from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch.map_reduce_ops.min_time_op import min_time_op
from pystoch.datatypes import DT, Singleton
from pystoch.keywords import *

class MinTimeOpTest(unittest.TestCase):

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
    
        a = numpy.zeros((3,3),numpy.int32)
        a[:] = numpy.iinfo(a.dtype).max
        co = min_time_op(a)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.array([(1,1),])
        weight = numpy.float32(12)
        metadata = {TIME:{ETIME:numpy.int32(12)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.int32)
        b[:] = numpy.iinfo(b.dtype).max
        b[1,1] = 12
        assert_array_equal(a, b)
        
    def test_array_of_value(self):
        a = numpy.zeros((3,3),numpy.int32)
        a[:] = numpy.iinfo(a.dtype).max
        co = min_time_op(a)

        # make a single value        
        block = numpy.zeros((3),DT.IDEAL_PARTICLE)     
        index_pos = numpy.array([(1,1),(1,2),(1,1)])
        weight = numpy.ones(3)
        metadata = {TIME:{ETIME:numpy.int32(12)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.int32)
        b[:] = numpy.iinfo(b.dtype).max
        b[1,1] = 12
        b[1,2] = 12
        assert_array_equal(a, b)
        
    def test_array_of_indicies(self):
    
        a = numpy.zeros((3,3),numpy.int32)
        a[:] = numpy.iinfo(a.dtype).max
        co = min_time_op(a)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.array([(1,1),(1,2),(1,1)])
        weight = numpy.float(12)
        metadata = {TIME:{ETIME:numpy.int32(9)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.int32)
        b[:] = numpy.iinfo(b.dtype).max
        b[1,1] = 9
        b[1,2] = 9
        assert_array_equal(a, b)
        
        # Send it again
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.int32)
        b[:] = numpy.iinfo(b.dtype).max
        b[1,1] = 9
        b[1,2] = 9
        assert_array_equal(a, b)
    
    