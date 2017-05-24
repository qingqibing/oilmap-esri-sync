from nose.tools import *
from numpy.testing import *
import unittest
import os
import numpy

from pystoch.map_reduce_ops.counter_op import counter_op
from pystoch.datatypes import DT, Singleton

from pystoch.output.netcdf_out import netcdf_out
from pystoch.grids import Grid
from pystoch.grid_data import GridData
from collections import OrderedDict

from netCDF4 import Dataset


FNAME = 'scratch.nc'
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
        
        try:
            os.unlink(FNAME)
        except OSError:
            pass
        
        
    def make_grid(self):
    
        extents = numpy.ndarray(1,DT.EXTENTS)
        extents['ll'][:] = 5.0
        extents['ur'][:] = 10.0
    
        grid_spacing = numpy.ndarray(1,DT.VECTOR)
        grid_spacing[:] = 1.0
    
        grid_dimensions = numpy.ndarray(1,DT.IVECTOR)
        grid_dimensions[:] = 5
            
        return Grid(extents,grid_spacing, grid_dimensions)

    def test_nc_from_grid_data(self):
        grid = self.make_grid()
        gd = GridData(grid)
        
        a = gd.allocate('count', numpy.int32)
        
        metadata = {'bobs':'bits'}
        dims = OrderedDict()
        dims['dim1'] = 2
        dims['dim2'] = 3 
        gd.allocate('bob', numpy.float64, grid_data_dimension=dims, initialize=1.0, metadata=metadata)
        
        
        netcdf_out(FNAME, 'scenario', 10, 'SHORE', gd)
        
        # Now read it back and make sure its right...
        
        rootgrp = Dataset(FNAME, 'r')
        assert_equal(rootgrp.title, 'Pystoch Oil Analysis')
        assert_equal(rootgrp.institution, 'RPS ASA')
        assert_equal(rootgrp.Conventions, "CF-1.6" )
    
        # do something weird because the keys come back in unicode
        assert_equal(tuple(str(s) for s in rootgrp.dimensions.keys()), ('latitude','longitude','dim1','dim2'))
        
        nc_var = rootgrp.variables['count']
        assert_equal(len(nc_var.ncattrs()),1)
        assert_equal(nc_var.dimensions,('longitude','latitude'))
        
        assert_array_equal(nc_var, gd.count)
        
        nc_var = rootgrp.variables['bob']
        assert_equal(len(nc_var.ncattrs()),2)
        assert_in('bobs', nc_var.ncattrs())
        assert_equal(nc_var.dimensions,('dim1','dim2','longitude','latitude',))
        
        assert_array_equal(nc_var, gd.bob)
            
        
        
        
        
        
        
        
        
        