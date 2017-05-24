from nose.tools import *
from numpy.testing import *
import unittest

import numpy

from pystoch.singleton import Singleton
from pystoch.datatypes import DT
from pystoch.workflow import WorkFlow
from pystoch.grids import Grid
from pystoch.readers import oilmdl_reader
from pystoch.readers import splmdl_reader
from pystoch.exceptions import PyStochWorkflowError
from pystoch.util import SURFACE, SUBSURFACE, SHORE
from pystoch.gridding_functions import bin_grid_mapper
from pystoch.readers.random_generator import RandomWalkGenerator
from pystoch.keywords import *
from pystoch import config

class WorkflowTest(unittest.TestCase):
    def setUp(self):
        """
        Setup test
        """
        Singleton._instances.clear()
        DT(ndims=2,precision=numpy.float32,location_units='LatLon')
        cfg = config.Config()
        cfg._unlock()
    
    def test_select_trajectory_files(self):
    
        # Test with files from spill model - pcd/pcl extension
        wf = WorkFlow()
        path = './trajectory_data/simap/3D_TEST1'
        prefix = '3D_TEST1_S'
        
        wf.select_trajectory_files(path, prefix, None)
        
        assert_equal(len(wf._file_readers),2)
        
        for item in wf._file_readers:
            assert_is_instance(item, splmdl_reader.SplModelDirectAccessReader)
        assert_is(wf.trajectory_file_class, splmdl_reader.SplModelDirectAccessReader)

        # Test with files from oil model - stt/stp extension
        wf = WorkFlow()
        path = './trajectory_data/oilmap/2D_TEST1'
        prefix = '2D_TEST1_s'
        
        wf.select_trajectory_files(path, prefix, None)
        
        assert_equal(len(wf._file_readers),4)        
        for item in wf._file_readers:
            assert_is_instance(item, oilmdl_reader.OilModelDirectAccessReader)
        assert_is(wf.trajectory_file_class, oilmdl_reader.OilModelDirectAccessReader)
    
        # Test with files where one of the two required files is missing
        wf = WorkFlow()
        path = './trajectory_data/test_file_structure'
        prefix = 'foo'
        
        with assert_raises(PyStochWorkflowError) as rte:
            wf.select_trajectory_files(path, prefix, None)
        
    def test_select_grid_method(self):
    
        wf = WorkFlow()
        
        cfg = config.Config()
        cfg.grid.method = 'bin gridding'
        cfg.grid.spacing = (1.,1.,1.)

        
        wf.select_grid_method()

        assert_equal(wf._grid_type, Grid.FIXED)
        assert_equal(wf._grid_spacing, (1.,1.,1.))
        assert_equal(wf._grid_dimensions, None)
        assert_is(wf._grid_function, bin_grid_mapper.grid_function)
        


    def test_create_grid(self):
    
        wf = WorkFlow()
        
        cfg = config.Config()
        
        cfg.grid.method = 'bin gridding'
        cfg.grid.spacing = (.1,.1,.1)
        
        # test making fixed grids
        wf.select_grid_method()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        grid = wf._create_grid(2,extents)        
        assert_array_equal(grid.grid_dimensions, numpy.array((10,10)))
        
        extents = DT.extents(ndims=3, prec=DT.PRECISION, ll_default=(-1,-1,-1), ur_default=(1,1,1))
        grid = wf._create_grid(3,extents)        
        assert_array_equal(grid.grid_dimensions, numpy.array((20,20,20)))

        
        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = (10,10,10)
        del cfg.grid['spacing']


        # test making floating grids
        wf.select_grid_method()

        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        grid = wf._create_grid(2,extents)        
        assert_array_equal(grid.grid_spacing, numpy.array((.1,.1),dtype=DT.PRECISION))
        
        extents = DT.extents(ndims=3, prec=DT.PRECISION, ll_default=(-1,-1,-1), ur_default=(1,1,1))
        grid = wf._create_grid(3,extents)        
        assert_array_equal(grid.grid_spacing, numpy.array((.2,.2,.2),dtype=DT.PRECISION))

        with assert_raises_regexp(PyStochWorkflowError,"Grid dimension must be 2 or 3: Recieved 'poo'"):
            grid = wf._create_grid('poo',extents)

    def test_setup_products_exceptions(self):
    
        wf = WorkFlow()
        path = './trajectory_data/oilmap/2D_TEST1'
        prefix = '2D_TEST1_s'
        
        with assert_raises_regexp(PyStochWorkflowError,'Must select a grid or shape method before calling setup_products'):
            wf.setup_products()

        cfg = config.Config()        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = (10,10,10)
        wf.select_grid_method() 

        with assert_raises_regexp(PyStochWorkflowError,'Must select_trajectory_files before calling setup_products'):
            wf.setup_products()
        wf.select_trajectory_files(path, prefix, None)
        
        with assert_raises_regexp(PyStochWorkflowError,'Must set at least one product!'):
            wf.setup_products()

        with assert_raises_regexp(PyStochWorkflowError,'Can not call setup_products more than once!'):
            wf.setup_products()

    def test_setup_products_surface(self):
    
        wf = WorkFlow()
        path = './trajectory_data/oilmap/2D_TEST1/'
        prefix = '2D_TEST1_s'
        
        cfg = config.Config()        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = [10,10,10]
        cfg.surface.gridded_products.hit_count = {}
        cfg.surface.gridded_products.oil_volume = {}

        
        wf.select_grid_method() 
        wf.select_trajectory_files(path, prefix, None)
       
        wf.setup_products()

        assert_equal(len(wf._gridder_map), 1)
        surface_gridder = wf._gridder_map[SURFACE]
        assert_equal(surface_gridder.__name__,'grid_function')

    def test_setup_products_subsurface(self):
        # make another with surface and subsurface...
        wf = WorkFlow()
        path = './trajectory_data/simap/3D_TEST1'
        prefix = '3D_TEST1_S'
        
        cfg = config.Config()        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = [10,10,10]
        cfg.surface.gridded_products.hit_count = {}
        cfg.subsurface.gridded_products.hit_count = {}
        
        wf.select_grid_method() 
        # Dangerous to use fixed grid with real data - may create a very large grid!
        #wf.select_grid_method(Grid.FIXED,'bin gridding',grid_spacing=(.001,.001,300)) 

        wf.select_trajectory_files(path, prefix, None)
       
        wf.setup_products()

        assert_equal(len(wf._gridder_map), 2)
        surface_gridder = wf._gridder_map[SURFACE]
        assert_equal(surface_gridder.__name__,'grid_function')
        
        surface_gridder = wf._gridder_map[SUBSURFACE]
        assert_equal(surface_gridder.__name__,'grid_function')

    def test_surface_count_run(self):
    
        wf = WorkFlow()
        path = './trajectory_data/oilmap/2D_TEST1/'
        prefix = '2D_TEST1_s'
        
        cfg = config.Config()        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = [10,10]
        cfg.surface.gridded_products.hit_count = {}

        wf.select_grid_method() 
        wf.select_trajectory_files(path, prefix, None)
       
        wf.setup_products()
        wf.run()

        gd = wf._grid_data[SURFACE]        
        # Value from the hit count array from the fist test with this data. 
        assert_equal(gd.hit_count[0,9], 815)
        
        
    def test_subsurface_count_run(self):
    
        wf = WorkFlow()
        path = './trajectory_data/simap/3D_TEST1'
        prefix = '3D_TEST1_S'
        
        cfg = config.Config()        
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = [10,10]
        
        cfg.surface.gridded_products.hit_count = {}
        cfg.subsurface.gridded_products.hit_count = {}

        
        wf.select_grid_method() 
        wf.select_trajectory_files(path, prefix, None)
       
        wf.setup_products()
        wf.run()

        gd = wf._grid_data[SURFACE]        
        # Value from the hit count array from the fist test with this data. 
        print gd.hit_count
        assert_equal(gd.hit_count[2,1],992)
        
        
    def test_hit_count_by_bin(self):
    
        files = 20
        blocks = 50
        blocksize = 100
    
        grid_dimensions = (10,10)
    
        cfg = config.Config()
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = grid_dimensions
    
        cfg.surface.gridded_products.hit_count = {}
    
    
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        scaling = numpy.float(files * blocks * blocksize) / numpy.float(numpy.array(grid_dimensions).prod() ) 
        # Value from the hit count array from the fist test with this data. 
        assert_array_almost_equal(gd.hit_count/scaling, numpy.ones(grid_dimensions), decimal=1)
        
    def test_oil_volume_by_bin(self):
    
        files = 10
        blocks = 100
        blocksize = 100
    
        grid_dimensions = (10,10)
    
        cfg = config.Config()
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = grid_dimensions
    
        cfg.surface.gridded_products.oil_volume = {}

    
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        scaling = numpy.float(files * blocks * blocksize) / numpy.float(numpy.array(grid_dimensions).prod() ) 
        # Value 0.7from the oil volume from the fist test with this data. Difficult to predict correct value
        # from the random generator - mass is a function of block number
        assert_array_almost_equal(gd.oil_volume/scaling, 0.08 *numpy.ones(grid_dimensions), decimal=1)
        
        
    def test_hit_count_by_interpolated_bin(self):
    
        files = 2
        blocks = 50
        blocksize = 100
    
        grid_dimensions = (5,5)

        cfg = config.Config()
        cfg.grid.method = 'interpolated bin gridding'
        cfg.grid.dimensions = grid_dimensions
        
        cfg.surface.gridded_products.hit_count = {}

        
        # Run again with interpolated gridding
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        
        # Hit count distribution will be roughly gaussian - but better to just use observed values...
        #gauss = numpy.zeros(grid_dimensions,DT.PRECISION)
        #itr = numpy.nditer(gauss,flags=["multi_index"],op_flags=['readwrite'])
        #ndims = len(grid_dimensions)
        #for v in itr:
        #    x = itr.multi_index - numpy.ones(ndims,dtype=numpy.int32)*2
        #    #v[...] = numpy.sum(x**2)
        #    v[...] = numpy.exp( -0.17 *numpy.sum(x**2))

        result = numpy.array(   [[ 0.16342601,  0.294661,    0.31472843,  0.2921901,   0.16520414],
                                 [ 0.28637077,  0.684879 ,   0.80244319,  0.67541105,  0.28694809],
                                 [ 0.31572141,  0.80456771,  1.,          0.80692315,  0.31276556],
                                 [ 0.29158969,  0.68781175,  0.79971827,  0.68935895,  0.29387585],
                                 [ 0.16940698,  0.28854147,  0.31191114,  0.2906198,   0.17012285],])

        assert_array_almost_equal(gd.hit_count / numpy.float(gd.hit_count.max()), result, decimal=1)
        
    def test_oil_volume_by_interpolated_bin(self):
    
        files = 2
        blocks = 50
        blocksize = 100
    
        grid_dimensions = (5,5)
        # Run again with interpolated gridding
        cfg = config.Config()
        cfg.grid.method = 'interpolated bin gridding'
        cfg.grid.dimensions = grid_dimensions
        
        cfg.surface.gridded_products.oil_volume = {}

        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        
        # Hit count distribution will be roughly gaussian - but better to just use observed values...
        #gauss = numpy.zeros(grid_dimensions,DT.PRECISION)
        #itr = numpy.nditer(gauss,flags=["multi_index"],op_flags=['readwrite'])
        #ndims = len(grid_dimensions)
        #for v in itr:
        #    x = itr.multi_index - numpy.ones(ndims,dtype=numpy.int32)*2
        #    #v[...] = numpy.sum(x**2)
        #    v[...] = numpy.exp( -0.17 *numpy.sum(x**2))

        result = numpy.array(   [[ 0.16342601,  0.294661,    0.31472843,  0.2921901,   0.16520414],
                                 [ 0.28637077,  0.684879 ,   0.80244319,  0.67541105,  0.28694809],
                                 [ 0.31572141,  0.80456771,  1.,          0.80692315,  0.31276556],
                                 [ 0.29158969,  0.68781175,  0.79971827,  0.68935895,  0.29387585],
                                 [ 0.16940698,  0.28854147,  0.31191114,  0.2906198,   0.17012285],])

        assert_array_almost_equal(gd.oil_volume / numpy.float(gd.oil_volume.max()), result, decimal=1)
        
    def test_min_time_by_interpolated_bin(self):
    
        files = 2
        blocks = 50
        blocksize = 100
    
        grid_dimensions = (5,5)
        # Run again with interpolated gridding
        
        cfg = config.Config()
        cfg.grid.method = 'interpolated bin gridding'
        cfg.grid.dimensions = grid_dimensions

        cfg.surface.gridded_products.min_time = {}

        
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        # all 25 cells get hit with the first 100 particles
        assert_true((gd.min_time == 3600).all())

    def test_min_time_by_bin(self):
    
        files = 2
        blocks = 50
        blocksize = 50
    
        grid_dimensions = (10,10)
        # Run again with interpolated gridding
        cfg = config.Config()
        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = grid_dimensions

        cfg.surface.gridded_products.min_time = {}

        
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE]     
        # all 25 cells get hit with the first 100 particles
        assert_true((gd.min_time < 20*3600).all())
        assert_true((gd.min_time == 3600).any())
        assert_true((gd.min_time > 0).any())


    def test_oil_volume_distribution_by_bin(self):
    
        # over-ride the actual config
        cfg=config.Config()
        
        cfg.surface.volume.bins = 100
        cfg.surface.volume.coefficient = 0.5
        
        cfg.surface.gridded_products.oil_volume_distribution = {}

        
        files = 2
        blocks = 50
        blocksize = 50
    
        grid_dimensions = [10,10]
        # Run again with interpolated gridding

        cfg.grid.method = 'bin gridding'
        cfg.grid.dimensions = grid_dimensions

        
        wf = WorkFlow()
        wf.select_grid_method() 
       
        # Instead of loading files, manually emulate select_trajectory_files with random particle generator
        wf.trajectory_file_class = RandomWalkGenerator
        wf._file_readers = [RandomWalkGenerator('name',nblocks=blocks, blocksize=blocksize) for i in range(files)]
       
        wf.setup_products()
        
        extents = DT.extents(ndims=2, prec=DT.PRECISION, ll_default=(0,0), ur_default=(1,1))
        
        assert_equal(extents['ll'], wf._grids[SURFACE].extents['ll'])
        assert_equal(extents['ur'], wf._grids[SURFACE].extents['ur'])
        
        wf.run()
        
        gd = wf._grid_data[SURFACE] 
        #print gd.oil_volume_distribution  
        assert_true((gd.oil_volume_distribution[0,:,:] > 10).all())
        assert_true((gd.oil_volume_distribution[90,:,:] == 0).all())
        assert_true((gd.oil_volume_distribution[1,:,:] > 0).any())
        assert_true((numpy.sum(gd.oil_volume_distribution,axis=0) == 100).any())



    def test_get_shapes(self):
        
        wf = WorkFlow()
        wf._shape_file = 'trajectory_data/polygons/Test SHP File.SHP'
        wf._shapes = {}
        
        wf._get_shapes()
        
        assert_equal(len(wf._shapes), 3)
        assert_equal(len(wf._shapes[SURFACE]),3)
        assert_equal(wf._shapes[SURFACE],wf._shapes[SUBSURFACE])
        assert_equal(wf._shapes[SURFACE],wf._shapes[SHORE])
        
        assert_equal(wf._shapes[SURFACE]['0'].properties['ID'],'Polygon 1' )

        
        
        
        


        
        