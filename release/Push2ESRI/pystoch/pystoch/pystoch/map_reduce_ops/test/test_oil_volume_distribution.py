from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch.map_reduce_ops.oil_volume_distribution_op import oil_volume_distribution_op
from pystoch.datatypes import DT, Singleton
from pystoch.keywords import *


class OilVoulmeDistributionTest(unittest.TestCase):

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
    
        a = numpy.zeros((3,3,3),DT.INT32)
        co = oil_volume_distribution_op(a,2.0)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        block['mass'] = 10.1
        block['density'] = 5.0
        index_pos = numpy.array([(1,1),])
        weight = numpy.ones((1,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)},BLOCK:{N_OF_M_IN_TS:(1,1),}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3,3),DT.INT32)
        b[0,:,:] = 1
        b[0,1,1] = 0
        b[1,1,1] = 1
        assert_array_equal(a, b)
        
    def test_array_of_value(self):
        a = numpy.zeros((3,3,3),DT.INT32)
        co = oil_volume_distribution_op(a,2.0)

        # make a single value        
        block = numpy.zeros((3),DT.IDEAL_PARTICLE) 
        block['mass'] = numpy.array([20.1,10.1,1.1])
        block['density'] = numpy.array([5.,5.,5.])
        index_pos = numpy.array([(1,1),(1,2),(1,1)])
        weight = numpy.ones((3,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)},BLOCK:{N_OF_M_IN_TS:(1,1),}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        
        b = numpy.zeros((3,3,3),DT.INT32)
        b[0,0,0] = 1
        b[0,0,1] = 1
        b[0,0,2] = 1

        b[0,1,0] = 1
        b[2,1,1] = 1 # two particles in the (1,1) grid cell but total volume is still less than 3
        b[0,2,1] = 1

        b[0,2,0] = 1
        b[1,1,2] = 1
        b[0,2,2] = 1
        
        assert_array_equal(a, b)
        
    def test_array_of_indicies(self):
    
        a = numpy.zeros((5,3,3),DT.INT32)
        co = oil_volume_distribution_op(a,2.0)

        # make a single value        
        block = numpy.zeros((),DT.IDEAL_PARTICLE)
        block['mass'] = 10.1
        block['density'] = 5.0
        index_pos = numpy.array([(1,1),(1,2),(1,1)])
        weight = numpy.ones((3,))
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)},BLOCK:{N_OF_M_IN_TS:(1,2),}}
        
        # Send the value
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((5,3,3),numpy.float32)
        assert_array_equal(a, b)
        
        
        
        # Update the metadata and send it again
        metadata = {TIME:{ETIME:numpy.int32(1), DTIME:numpy.int32(1)},BLOCK:{N_OF_M_IN_TS:(2,2),}}
        co.send((block, index_pos, weight, metadata))
        b = numpy.zeros((5,3,3),numpy.float32)
        b[0,0,0] = 1
        b[0,1,0] = 1
        b[0,2,0] = 1

        b[0,0,1] = 1
        b[4,1,1] = 1 # two particles in the (1,1) grid cell but total volume is still less than 3
        b[0,2,1] = 1

        b[0,0,2] = 1
        b[2,1,2] = 1
        b[0,2,2] = 1
        
        assert_array_equal(a, b)
    
    