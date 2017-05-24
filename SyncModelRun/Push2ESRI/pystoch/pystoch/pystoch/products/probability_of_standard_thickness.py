#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file probability_of_standard_thickness.py
@date 08/22/13
@description Calculates the probability of a set of standard thicknesses occurring
'''
import numpy
import logging
from collections import OrderedDict
from pystoch.exceptions import PyStochOperatorError
import helper_functions 

from pystoch.datatypes import DT
from pystoch.map_reduce_ops.thickest_spillet_op import thickest_spillet_op
from pystoch.map_reduce_ops.exceed_reduce import exceed_reduce

from pystoch.config import get_config
from pystoch.keywords import *

logger = logging.getLogger('pystoch.products.probability_of_standard_thickness')

product_name = 'probability_of_standard_thickness'

def add_product(ops_list, reduce_list, cleaner_list, grid_data, product_metadata):

    product_type = product_metadata[PRODUCT_TYPE]
    
    config = get_config()
    cfg_opts = config.get(product_type,{}).get(GRIDDED_PRODUCTS,{}).get(product_name,{})
    standard_thicknesses= cfg_opts.get('standard_thicknesses',[0.0])
    
    reduce_arrays = []
    for i in xrange(len(standard_thicknesses)):
        metadata={
            'units':'counts',
            'long_name':'Count of simulations where the maximum spillet thickness exceeded %s meters' % standard_thicknesses[i],
            'coordinates':'latitude longitude',
            }
        reduce_array = grid_data.allocate(
            "%s_%s" % (product_name, standard_thicknesses[i]),
            DT.INT32, 
            metadata=metadata, 
            only_if_msr=True)
            
        reduce_arrays.append(reduce_array)
    
    

    # Make a temporary array that will be used in the operation
    map_array = grid_data.allocate(product_name,DT.SPRECISION, metadata=metadata, store=False)
    
        
    coroutine = thickest_spillet_op(map_array)
    # calculates the maximum oil thickness in each grid cell during a simulation
    
    # Append the operation coroutine to the list
    ops_list.append(coroutine)
    
    #bins the distribution of max oil thickness from each simulation
    for reduce_array, exceedance_val in zip(reduce_arrays, standard_thicknesses):
        coroutine = exceed_reduce(reduce_array, exceedance_val)
        reduce_list.append((coroutine, map_array))

    # Now add a reset value for the map array
    cleaner_list.append((map_array,0.0))
    
    