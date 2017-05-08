#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_concentration.py
@date 03/11/13
@description Calculate the maximum concentration in the volume of a cell from a single spillet
'''
import numpy
import logging
from pystoch.exceptions import PyStochOperatorError

from pystoch import config
from pystoch.datatypes import DT
from pystoch.map_reduce_ops.max_concentration_op import max_concentration_op
from pystoch.map_reduce_ops.max_reduce import max_reduce

from pystoch.config import get_config
from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.max_concentration')

product_name = 'max_concentration'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    config = get_config()
    # This method now uses a quadratic index space
    cell_depth_range = config[product_type].products.max_concentration.cell_depth_range

    #allocate space for the gridded result
    
    metadata={'units':'g/cm^3','long_name':'Maximum Oil Concentration'}
    reduce_array = grid_data.allocate(product_name,DT.SPRECISION, metadata=metadata)
    
    # Calculate cell area:
    cell_area = grid_data._grid.cell_area # m**2
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    coroutine = max_concentration_op(map_array,cell_depth_range, cell_area)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = max_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array, DT.SPRECISION(0.0)))
    