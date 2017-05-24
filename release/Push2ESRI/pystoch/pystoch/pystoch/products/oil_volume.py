#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oil_volume.py
@date 03/11/13
@description build the oil volume product workflow
'''
import logging
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.oil_volume_op import oil_volume_op
from pystoch.map_reduce_ops.max_reduce import max_reduce

from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.oil_volume')

product_name = 'oil_volume'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    #allocate space for the gridded result
    metadata={'units':'m^3','long_name':'Aggregate Oil Volume'}
    reduce_array = grid_data.allocate(product_name,DT.SPRECISION,metadata=metadata)
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    coroutine = oil_volume_op(map_array)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = max_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array, DT.SPRECISION(0.0)))
    
