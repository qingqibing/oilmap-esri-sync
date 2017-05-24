#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file oil_volume.py
@date 03/11/13
@description build the oil volume product workflow
'''
import logging
from collections import OrderedDict

from pystoch.exceptions import PyStochOperatorError

from pystoch import config
from pystoch.datatypes import DT
from pystoch.map_reduce_ops.oil_volume_distribution_op import oil_volume_distribution_op
from pystoch.map_reduce_ops.sum_reduce import sum_reduce

from pystoch.config import get_config
from pystoch.keywords import *


logger = logging.getLogger('pystoch.products.oil_volume')

product_name = 'oil_volume_distribution'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    config = get_config()
    # This method now uses a quadratic index space
    nbins = config[product_type].volume.bins
    bin_coefficient = config[product_type].volume.coefficient    
    

    dims, bin_values = grid_data.make_bin_data('volume_bins', nbins, bin_coefficient)


    metadata = {
        'units':'counts',
        'long_name':'Oil Volume Distribution',
        'coordinates':'volume_bins latitude longitude',
        }
    reduce_array = grid_data.allocate(product_name,DT.PRECISION, grid_data_dimension=dims, metadata=metadata)
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    coroutine = oil_volume_distribution_op(map_array, bin_coefficient)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = sum_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))
    
    # Now add a reset value for the map array
    cleaner_list.append((map_array,0.0))
    
