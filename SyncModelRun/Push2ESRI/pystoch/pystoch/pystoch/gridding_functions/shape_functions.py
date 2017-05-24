#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file grid_functions.py
@date 03/11/13
@description A module which imports and provides a mapping to all known grid mapping functions
'''

import shapely_contains

# use an ordered dict to express precedence
shape_functions_map = {}
shape_functions_map[shapely_contains.shape_function_name] = shapely_contains.shape_function
        
        
        
