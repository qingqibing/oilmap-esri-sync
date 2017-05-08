#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file shore_oil_stats.py
@date 03/11/13
@description Calculates the distribution of oil thickness based on the thickest spillet in each cell of each time step
'''
import numpy
import logging
from collections import OrderedDict
from pystoch.exceptions import PyStochOperatorError

from pystoch.map_reduce_ops.stats_reduce import stats_reduce
from pystoch.map_reduce_ops.shore_oil_stats_op import shore_oil_stats_op


from pystoch.map_reduce_ops.shore_oil_stats_op import FIRST_CONTACT_LATITUDE, \
    FIRST_CONTACT_LONGITUDE, TIME_TO_SHORE, MASS_OF_OIL_ONSHORE

from pystoch.datatypes import DT
from pystoch.config import get_config
from pystoch.keywords import *


logger = logging.getLogger('pystoch.products.shore_oil_stats')

product_name = 'shore_oil_stats'


def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    config = get_config()
 
    # make each variable for the netcdf file
    
    array_map = {}
    value_map = {}
    
    dims = OrderedDict()
    dims[NSIMS] = product_metadata[NSIMS]
    
    # Make each statistics array for the nc output#
    metadata={
        'units':'degrees_north',
        'long_name':'latitude',
        'coordinates':FILE_NAMES,
        'fill_value':numpy.nan
        }
    reduce_array = grid_data.allocate_coordinate(FIRST_CONTACT_LATITUDE,DT.PRECISION, data_dimension=dims, metadata=metadata)
    array_map[FIRST_CONTACT_LATITUDE] = reduce_array
    value_map[FIRST_CONTACT_LATITUDE] = numpy.nan
    
    metadata={
        'units':'degrees_east',
        'long_name':'longitude',
        'coordinates':FILE_NAMES,
        'fill_value':numpy.nan
        }
    reduce_array = grid_data.allocate_coordinate(FIRST_CONTACT_LONGITUDE,DT.PRECISION, data_dimension=dims, metadata=metadata)
    array_map[FIRST_CONTACT_LONGITUDE] = reduce_array
    value_map[FIRST_CONTACT_LONGITUDE] = numpy.nan
    
    metadata={
        'units':'time in minutes since simulation start',
        'long_name':'time of first shore oil contact',
        'coordinates':FILE_NAMES,
        'fill_value':-1
        }
    reduce_array = grid_data.allocate_coordinate(TIME_TO_SHORE, DT.INT32, data_dimension=dims, metadata=metadata)
    array_map[TIME_TO_SHORE] = reduce_array
    value_map[TIME_TO_SHORE] = -1
    
    metadata={
        'units':'MT',
        'long_name':'mass of oil on shore',
        'coordinates':FILE_NAMES,
        }
    reduce_array = grid_data.allocate_coordinate(MASS_OF_OIL_ONSHORE, DT.PRECISION, data_dimension=dims, metadata=metadata)
    array_map[MASS_OF_OIL_ONSHORE] = reduce_array
    value_map[MASS_OF_OIL_ONSHORE] = 0.0
    
    reset_map = value_map.copy()
        
    # Calculate cell area:
    cell_area = grid_data._grid.cell_area
    
    
    
    coroutine = shore_oil_stats_op(value_map, cell_area)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = stats_reduce(array_map, grid_data[FILE_NAMES])
    
    reduce_list.append((coroutine, value_map))
    
         
    # Now add a reset value for the map arrays
    cleaner_list.append((value_map, reset_map))

    
