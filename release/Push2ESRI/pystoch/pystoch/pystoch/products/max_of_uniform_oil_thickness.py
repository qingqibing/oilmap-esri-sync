#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_of_uniform_oil_thickness.py
@date 03/11/13
@description build the avgerage oil thickness product workflow
'''
import numpy
import logging
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.max_uniform_oil_thickness_op import max_uniform_oil_thickness_op
from pystoch.map_reduce_ops.max_reduce import max_reduce

from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.oil_volume')

product_name = 'max_of_uniform_oil_thickness'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result
    
    metadata={'units':'m','long_name':'Max of Uniform Oil Thickness','fill_value':DT.SPRECISION(0.0)}
    reduce_array = grid_data.allocate(product_name,DT.SPRECISION, metadata=metadata)
    
    # Calculate cell area:
    cell_area = grid_data._grid.cell_area
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    coroutine = max_uniform_oil_thickness_op(map_array, cell_area)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = max_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))

    # Now add a reset value for the map array
    cleaner_list.append((map_array, DT.SPRECISION(0.0)))
    
    