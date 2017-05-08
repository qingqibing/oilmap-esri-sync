#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_shore_grid_thickness.py
@date 05/21/13
@description Calculate the maximum thickness on shore using the grid dimension as the area
'''
import logging
import numpy
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.max_shore_grid_thickness_op import max_shore_grid_thickness_op
from pystoch.map_reduce_ops.max_reduce import max_reduce

from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.max_shore_grid_thickness')


product_name = 'max_shore_grid_thickness'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result and initialize with max int
    metadata={'units':'m','long_name':'maximum on shore oil thickness'}
    reduce_array = grid_data.allocate(product_name, DT.SPRECISION, metadata=metadata)
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    
    # Calculate cell diagonal:
    cell_diagonal = grid_data._grid.cell_diagonal
    
    coroutine = max_shore_grid_thickness_op(map_array, cell_diagonal)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    # use the array allocated in grid data as the result in the reduce method
    coroutine = max_reduce(reduce_array)
    
    # append the reduce coroutine and the argument it will be passed to the reduce list
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array, DT.SPRECISION(0.0)))
    