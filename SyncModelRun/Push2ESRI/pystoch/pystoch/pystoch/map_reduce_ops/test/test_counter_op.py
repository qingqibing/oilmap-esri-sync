from nose.tools import *
from unittest.case import SkipTest
from numpy.testing import *
import unittest

import numpy
import cProfile

from pystoch.map_reduce_ops.counter_op import counter_op
from pystoch.datatypes import DT, Singleton
from pystoch.keywords import *

import pystoch.map_reduce_ops.counter_op as counter_op_module

class CounterOpTest(unittest.TestCase):

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
        co = counter_op(a)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.array([(1,1),],dtype=numpy.int32)
        weight = numpy.float32(12)
        metadata = {TIME:{ETIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.int32)
        b[1,1] = 1
        assert_array_equal(a, b)
        
    def test_invalid_array_type_in_cython(self):
    
        if counter_op_module.counter is None:
            raise SkipTest('Not using cython implmenation')
    
        # Test it with the wrong type
        a = numpy.zeros((3,3),numpy.int32)
        co = counter_op(a)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.array([(1,1),])
        weight = numpy.float32(12)
        metadata = {TIME:{ETIME:numpy.int32(1)}}
        
        # Send the value
        with assert_raises_regexp(ValueError,"Buffer dtype mismatch, expected 'DTYPE_i32t' but got 'long'"):
            co.send((block, index_pos, weight, metadata))
        
        
        # Test it with the wrong number of dimensions
        a = numpy.zeros((4,4,4),numpy.int32)
        co = counter_op(a)

        index_pos = numpy.array([(1,1),(2,2),(3,3)],dtype=numpy.int32)
        
        # Send the value
        with assert_raises_regexp(ValueError,"Buffer has wrong number of dimensions"):
            co.send((block, index_pos, weight, metadata))
        
        
        
    def test_array_of_value(self):
        a = numpy.zeros((3,3),numpy.int32)
        co = counter_op(a)

        # make a single value        
        block = numpy.zeros((3),DT.IDEAL_PARTICLE)     
        index_pos = numpy.array([(1,1),(1,2),(1,1)],dtype=numpy.int32)
        weight = numpy.ones(3)
        metadata = {TIME:{ETIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3),numpy.int32)
        b[1,1] = 2
        b[1,2] = 1
        assert_array_equal(a, b)
        
    def test_array_of_indicies(self):
    
        a = numpy.zeros((3,3),numpy.int32)
        co = counter_op(a)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.array([(1,1),(1,2),(1,1)],dtype=numpy.int32)
        weight = numpy.float(12)
        metadata = {TIME:{ETIME:numpy.int32(1)}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.int32)
        b[1,1] = 2
        b[1,2] = 1
        assert_array_equal(a, b)
        
        # Send it again
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((3,3),numpy.int32)
        b[1,1] = 4
        b[1,2] = 2
        assert_array_equal(a, b)
        
    def test_timing(self):
    
        a = numpy.zeros((200,200),numpy.int32)
        co = counter_op(a)
    
        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        index_pos = numpy.int32(numpy.random.randint(0,100,size=(200000,2)) )
        weight = numpy.float(12)
        metadata = {TIME:{ETIME:numpy.int32(1)}}
    
        cProfile.runctx('co.send((block, index_pos, weight, metadata))', globals=globals(),locals=locals())
    
        
    
    