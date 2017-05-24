#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file add_counter.py
@date 03/11/13
@description 
'''
import logging
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.counter_op import counter_op
from pystoch.map_reduce_ops.sum_reduce import sum_reduce

from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.hit_count')


product_name = 'hit_count'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result
    metadata={'units':'counts','long_name':'Oiled area mask and particle count'}
    reduce_array = grid_data.allocate(product_name,DT.INT32, metadata=metadata)
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    
    coroutine = counter_op(map_array)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    # use the array allocated in grid data as the result in the reduce method
    coroutine = sum_reduce(grid_data[product_name])
    
    # append the reduce coroutine and the argument it will be passed to the reduce list
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array,0))