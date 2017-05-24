#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file distribution_of_max_uniform_oil_thickness.py
@date 03/11/13
@description Calculates the distribution of the maximum thickness from each simulation
'''
import numpy
import logging
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.min_reduce import min_reduce
from pystoch.map_reduce_ops.area_exceeding_by_threshold_stats_reduce import area_exceeding_by_threshold_stats_reduce
logger = logging.getLogger('pystoch.products.help_functions')

def setup_min_time_to_thickness(grid_data, method_name, reduce_list, cleaner_list):

    min_time = {}

    thickness = grid_data[THICKNESS_BINS]
    dims = grid_data._dimensions.get(THICKNESS_BINS)

    metadata={
        'units':'time',
        'long_name':'Minimum time to %s_thickness' % method_name,
        'coordinates':'thickness_bins latitude longitude',
        'fill_value':numpy.iinfo(DT.INT32).max
        }
        
    reduce_array = grid_data.allocate(
        'min_time_to_%s_thickness'%method_name,
        DT.INT32, 
        initialize=numpy.iinfo(DT.INT32).max, 
        grid_data_dimension=dims, 
        metadata=metadata)
    
    map_array = reduce_array.copy()
    
    min_time['min_array'] = map_array
    min_time['thickness'] = thickness
    
    coroutine = min_reduce(reduce_array)
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array,numpy.iinfo(DT.INT32).max))
    
    return min_time
    


def setup_run_stats(grid_data, name, long_name, product_metadata, map_array, scalar, units, reduce_list):
    
    run_stats = {}
    
    thickness = grid_data[THICKNESS_BINS]
    dims = grid_data._dimensions.get(THICKNESS_BINS).copy()
    dims[NSIMS] = product_metadata[NSIMS]
    
    metadata={
        'units':units,
        'long_name':long_name,
        'coordinates':THICKNESS_BINS +' file_names',
        'fill_value':numpy.iinfo(DT.INT32).max,
        'scalar_grid_unit':scalar
        }
        
    stats_array = grid_data.allocate_coordinate(
        name,
        DT.PRECISION,
        data_dimension=dims, 
        metadata=metadata)
        
    coroutine = area_exceeding_by_threshold_stats_reduce(stats_array,thickness, grid_data[FILE_NAMES], scalar)
    reduce_list.append((coroutine, map_array))
    
    # do not do any cleaning - you don't own the map_array
    
    return run_stats
    
    
    
    
    
    
    
    
    
    
    
    
    