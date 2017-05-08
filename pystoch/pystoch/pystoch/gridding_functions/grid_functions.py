#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file grid_functions.py
@date 03/11/13
@description A module which imports and provides a mapping to all known grid mapping functions
'''

import bin_grid_mapper
import interpolated_grid_mapper

# use an ordered dict to express precedence
gridding_functions_map = {}
gridding_functions_map[bin_grid_mapper.grid_function_name] = bin_grid_mapper.grid_function
gridding_functions_map[interpolated_grid_mapper.grid_function_name] = interpolated_grid_mapper.grid_function
        
        
        
