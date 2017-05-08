from nose.tools import *
import unittest
from numpy.testing import *

from pystoch.grids import Grid
import numpy
from pystoch.datatypes import DT, Singleton


class GridsTest2D(unittest.TestCase):

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
        
        g = Grid(extents,grid_spacing, grid_dimensions)
        return g
    
    def tearDown(self):
        """
        Tear down test
        """
        # hack to clean up singleton DT
        Singleton._instances.clear()
    
    def test_indexof(self):

        
        g = self.make_grid()
    
        data = numpy.ndarray(1,DT.POINT)
        data[:] = 5.5
    
        idx = g.indexof(data)

        assert_array_equal(idx, numpy.zeros((1,DT.NDIMS)))
    
        # write more tests later...
    
    
    def test_class_methods(self):

        extents = numpy.ndarray(1,DT.EXTENTS)
        extents['ll'][:] = 5.0
        extents['ur'][:] = 10.0
    
        grid_spacing = numpy.ndarray(1,DT.VECTOR)
        grid_spacing[:] = 1.0
    
        grid_dimensions = numpy.ndarray(1,DT.IVECTOR)
        grid_dimensions[:] = 5
            
        g_fixed = Grid.create_floating(extents,grid_dimensions)
        g_floating = Grid.create_fixed(extents,grid_spacing)


        grid_spacing = grid_spacing.flatten()
        assert_array_equal(g_fixed.grid_spacing, grid_spacing)
        assert_equal(g_fixed.grid_spacing.dtype, numpy.float32)
        assert_equal(g_fixed.grid_spacing.shape, grid_spacing.shape)

        grid_dimensions = grid_dimensions.flatten()
        assert_array_equal(g_floating.grid_dimensions, grid_dimensions)
        assert_equal(g_floating.grid_dimensions.dtype, numpy.int32)
        assert_equal(g_floating.grid_dimensions.shape, grid_dimensions.shape)
    
    
    def test_meshgrid(self):
        g = self.make_grid()
        
        mesh_tup = g.meshgrid('A')
        
        shape = (1,6,1)
        tile = (6,1,6)  
        for coord_array in mesh_tup:
                  
            x = numpy.arange(6,dtype=numpy.float32)+5.0
            #2d: x = numpy.tile(x.reshape(1,6),(6,1))
            #3d: x = numpy.tile(x.reshape(1,6,1),(6,1,6))
         
            x = numpy.tile(x.reshape(shape[:DT.NDIMS]),tile[:DT.NDIMS])
            assert_array_equal(coord_array, x)
            
            # rotate the shape and tile for the next coordinate axis...
            shape = (shape[1],shape[2], shape[0])
            tile = (tile[1],tile[2], tile[0])
        
        
    def test_meshgrid(self):
        g = self.make_grid()
        
        mesh_tup = g.meshgrid('B')
        
        shape = (1,5,1)
        tile = (5,1,5)  
        for coord_array in mesh_tup:
                  
            x = numpy.arange(5,dtype=numpy.float32)+5.5
         
            x = numpy.tile(x.reshape(shape[:DT.NDIMS]),tile[:DT.NDIMS])

            assert_array_equal(coord_array, x)
            
            # rotate the shape and tile for the next coordinate axis...
            shape = (shape[1],shape[2], shape[0])
            tile = (tile[1],tile[2], tile[0])
        
    def test_cell_area(self):
    
        g = self.make_grid()
        
        ca = g.cell_area
        assert_equal(ca, 12215592136.986717)
        
    def test_cell_diagonal(self):
    
        g = self.make_grid()
        
        ca = g.cell_diagonal
        assert_equal(ca, 156307.6647284253)
        
        
class GridsTest3D(GridsTest2D):

    def setUp(self):
        """
        Setup test
        """
        DT(ndims=3,precision=numpy.float32,location_units='LatLon')
    
            



    