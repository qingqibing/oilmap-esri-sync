from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.grid_data import GridData

from collections import OrderedDict

class GridDataTest2D(unittest.TestCase):
    def setUp(self):
        """
        Setup test
        """
        DT(ndims=2,precision=numpy.float32,location_units='LatLon')
    
    
    def make_grid(self):
    
        extents = numpy.ndarray(1,DT.EXTENTS)
        extents['ll'][:] = 5.0
        extents['ur'][:] = 10.0
    
        grid_spacing = numpy.ndarray(1,DT.VECTOR)
        grid_spacing[:] = 1.0
    
        grid_dimensions = numpy.ndarray(1,DT.IVECTOR)
        grid_dimensions[:] = 5
            
        return Grid(extents,grid_spacing, grid_dimensions)
    
    
    def tearDown(self):
        """
        Tear down test
        """
        # hack to clean up singleton DT
        Singleton._instances.clear()
    
    def test_base_dimensions(self):
    
        grid = self.make_grid()
        gd = GridData(grid)
        
        bd = gd.base_dimensions
        
        assert_equal(bd, gd._base_dimensions)
        assert_equal(bd['latitude'], 5)
        assert_equal(bd['longitude'], 5)
    
    
    def test_allocation(self):
        grid = self.make_grid()
        gd = GridData(grid)
        
        #@todo - turn off exception logging here...
        with assert_raises(KeyError):
            gd['count']
            
        a = gd.allocate('count', numpy.int32)
        
        c = gd.count        
        assert_is(a,c)
        
        b = gd['count']
        assert_is(a,b)

        metadata = {'bobs':'bits'}
        dims = OrderedDict()
        dims['dim1'] = 2
        dims['dim2'] = 3 
        gd.allocate('bob', numpy.float64, grid_data_dimension=dims, initialize=1.0, metadata=metadata)
        
        assert_equal( (gd.bob==1.0).all(), True)

        assert_equal( gd.bob.shape,  (2,3) + tuple(grid.grid_dimensions))
        
        assert_in('bob', gd._metadata)
        assert_in('count', gd._metadata)
        assert_equal(gd._metadata['bob'], metadata)
        assert_equal(gd._metadata['count'], {})
        


    def test_initialize_and_zero_out(self):
        grid = self.make_grid()
        gd = GridData(grid)
        gd.allocate('joe',numpy.float32, initialize=5.0)
        assert_equal( (gd.joe==5.0).all(), True)
        gd.joe[...] = 6.0
        assert_equal( (gd.joe==6.0).all(), True)

        gd2 = gd.copy()

        gd.zero_out()
        assert_equal( (gd.joe==5.0).all(), True)

        assert_equal( (gd2.joe==6.0).all(), True)
        gd2.zero_out()
        assert_equal( (gd2.joe==5.0).all(), True)
        
        
    
    def test_constructor_allocation(self):
        grid = self.make_grid()
        gd = GridData(grid, defaults={'count':numpy.int32})
    
        assert_array_equal(gd.count,numpy.zeros(grid.grid_dimensions,numpy.int32))
        
        assert_is(gd.count, gd['count'])
    
    def test_array_dictionary(self):

        grid = self.make_grid()
        gd = GridData(grid,defaults={'count':numpy.int32})
    
        dct = gd.array_dictionary()
        
        assert_in('count', dct)
        assert_array_equal(gd.count,numpy.zeros(grid.grid_dimensions,numpy.int32))
    
    
class GridDataTest3D(GridDataTest2D):
    def setUp(self):
        """
        Setup test
        """
        DT(ndims=3,precision=numpy.float32,location_units='LatLon')
    
    