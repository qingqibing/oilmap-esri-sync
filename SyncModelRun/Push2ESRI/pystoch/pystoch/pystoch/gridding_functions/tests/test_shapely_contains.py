from nose.tools import *
from numpy.testing import *
import unittest

import numpy
from collections import OrderedDict
from shapely.geometry import Polygon


from pystoch.singleton import Singleton
from pystoch.datatypes import DT
from pystoch.gridding_functions.shapely_contains import shape_function
from pystoch.util import list_coroutine
from pystoch.readers.random_generator import RandomWalkGenerator
from pystoch.keywords import *
import cProfile

class WorkflowTest(unittest.TestCase):
    def setUp(self):
        """
        Setup test
        """
        Singleton._instances.clear()
        DT(ndims=2,precision=numpy.float32,location_units='LatLon')
        
        
    def test_simple(self):
    
        # make a shapes dictionary similar to what we get from workflow _get_shapes
        shapes = OrderedDict()
        
        nshapes = 5
        for i in xrange(nshapes):
            
            y = 1.0/(i+1)
            shape = Polygon([(0,0),(0,y),(y,y),(y,0)])
            shapes[str(i)] = shape
            
        # make a polygon that will not intersect!
        shapes[str(nshapes)] = Polygon([(-1,-1),(-2,-1),(-2,-2),(-1,-2)])
            
        result_list = []
        lst_co = list_coroutine(result_list)
        
        shape_co = shape_function(shapes, (lst_co,))
        
        blocksize = 100
        nblocks = 3
        random_file =  RandomWalkGenerator('noName',
                                            nblocks =nblocks,
                                            blocksize=blocksize
                                            )
        
        g = random_file.stream_record_blocks((RandomWalkGenerator.SURFACE_SPILLETS,))
        
        for block in g:
            shape_co.send((block.get(RandomWalkGenerator.SURFACE_SPILLETS),block.get(METADATA)))
            
        for tup in result_list:
            spillet_in_shape_array = tup[1]

            assert_true(spillet_in_shape_array[:,0].all())
            assert_true(spillet_in_shape_array[:,1].any())
            assert_true((spillet_in_shape_array[:,nshapes] == False).all())
            
            
    def test_timing(self):
    
        # make a shapes dictionary similar to what we get from workflow _get_shapes
        shapes = OrderedDict()
        
        nshapes = 100
        for i in xrange(nshapes):
            
            y = 1.0/(i+1)
            shape = Polygon([(0,0),(0,y),(y,y),(y,0)])
            shapes[str(i)] = shape
            
        # make a polygon that will not intersect!
        shapes[str(nshapes)] = Polygon([(-1,-1),(-2,-1),(-2,-2),(-1,-2)])
        
        shape_co = shape_function(shapes, ())
        
        blocksize = 10000
        nblocks = 5
        random_file =  RandomWalkGenerator('noName',
                                            nblocks =nblocks,
                                            blocksize=blocksize
                                            )
        
        g = random_file.stream_record_blocks((RandomWalkGenerator.SURFACE_SPILLETS,))
        
        for block in g:
            splts = block.get(RandomWalkGenerator.SURFACE_SPILLETS)
            mtd = block.get(METADATA)
            #shape_co.send((splts, mtd))
            
            cProfile.runctx('shape_co.send((splts, mtd))', globals=globals(),locals=locals())
            
