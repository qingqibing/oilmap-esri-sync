#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file add_counter.py
@date 03/11/13
@description 
'''
import logging
import numpy
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.min_time_op import min_time_op
from pystoch.map_reduce_ops.min_reduce import min_reduce
from pystoch.map_reduce_ops.clean_array import clean_array

from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.min_time')


product_name = 'min_time'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result and initialize with max int
    metadata={'units':'time in minutes since simulation start','long_name':'minimum time to oil','fill_value':numpy.iinfo(DT.INT32).max}
    reduce_array = grid_data.allocate(product_name, DT.INT32, initialize=numpy.iinfo(DT.INT32).max, metadata=metadata)
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    
    coroutine = min_time_op(map_array)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    # use the array allocated in grid data as the result in the reduce method
    coroutine = min_reduce(reduce_array)
    
    # append the reduce coroutine and the argument it will be passed to the reduce list
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array, numpy.iinfo(DT.INT32).max))
    