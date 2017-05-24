#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file max_of_uniform_oil_thickness.py
@date 03/11/13
@description Calculates the distribution of oil thickness in each time step of every simulation
'''
import numpy
import logging
from collections import OrderedDict
from pystoch.exceptions import PyStochOperatorError

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.uniform_oil_thickness_distribution_op import uniform_oil_thickness_distribution_op
from pystoch.map_reduce_ops.sum_reduce import sum_reduce
from pystoch.config import get_config
from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.uniform_oil_thickness_distribution')

product_name = 'uniform_oil_thickness_distribution'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    config = get_config()
    # This method now uses a quadratic index space
    nbins = config[product_type].thickness.bins
    bin_coefficient = config[product_type].thickness.coefficient
        
    dims, bin_values = grid_data.make_bin_data('thickness_bins', nbins, bin_coefficient)

    metadata={
        'units':'counts',
        'long_name':'Uniform Oil Thickness Distribution',
        'coordinates':'thickness_bins latitude longitude',
        }
    reduce_array = grid_data.allocate(product_name,DT.PRECISION, grid_data_dimension=dims, metadata=metadata)
    
    
    # Calculate cell area:
    cell_area = grid_data._grid.cell_area
    
    # Make a temporary array that will be used in the operation
    map_array = reduce_array.copy()
    coroutine = uniform_oil_thickness_distribution_op(map_array, cell_area, bin_coefficient)
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    coroutine = sum_reduce(reduce_array)
    
    reduce_list.append((coroutine, map_array))

    # Now add a reset value for the map array
    cleaner_list.append((map_array,0.0))