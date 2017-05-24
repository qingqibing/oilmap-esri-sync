#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_of_spillet_thickness.py
@date 03/11/13
@description Calculate the maximum thickness in a cell from a single spillet
'''
import numpy
import logging
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.thickest_spillet_op import thickest_spillet_op
from pystoch.map_reduce_ops.max_reduce import max_reduce

from pystoch.config import get_config
from pystoch.keywords import *


logger = logging.getLogger('pystoch.products.max_of_spillet_thickness')

product_name = 'max_of_spillet_thickness'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result
    
    metadata={'units':'m','long_name':'Maximum of spillet thickness','fill_value':DT.SPRECISION(0.0)}
    reduce_array = grid_data.allocate(product_name,DT.SPRECISION, metadata=metadata)
    
    # Calculate cell area:
    cell_area = grid_data._grid.cell_area
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()

    #config = get_config()
    #advective_dispersion = config[product_type].products.max_of_spillet_thickness.get('advective_dispersion',numpy.nan)
    #spillet_dispersion = advective_dispersion * 0.2 # m^2/s
    #coroutine = thickest_spillet_op(map_array, spillet_dispersion)

    coroutine = thickest_spillet_op(map_array)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = max_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array, DT.SPRECISION(0.0)))
    
    