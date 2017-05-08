#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file products.py
@date 03/11/13
@description A module which imports and provides a mapping to all known products which can be calculated
'''

import hit_count
import hit_probability
import oil_volume
import oil_volume_distribution
import min_time
import probability_of_standard_thickness

import max_of_uniform_oil_thickness
import uniform_oil_thickness_distribution
import distribution_of_max_uniform_oil_thickness

import thickest_spillet_oil_distribution
import max_of_spillet_thickness
import distribution_of_thickest_spillet

import max_shore_grid_thickness
import shore_oil_stats
import distribution_of_max_shore_grid_thickness

import max_concentration

### Surface Gridded
surface_gridded_products_map = {}
surface_gridded_products_map[hit_count.product_name]                            = hit_count.add_product
surface_gridded_products_map[hit_probability.product_name]                      = hit_probability.add_product
surface_gridded_products_map[probability_of_standard_thickness.product_name]    = probability_of_standard_thickness.add_product

surface_gridded_products_map[oil_volume.product_name]                   = oil_volume.add_product
surface_gridded_products_map[oil_volume_distribution.product_name]      = oil_volume_distribution.add_product
surface_gridded_products_map[min_time.product_name]                     = min_time.add_product

surface_gridded_products_map[max_of_uniform_oil_thickness.product_name] = max_of_uniform_oil_thickness.add_product
surface_gridded_products_map[distribution_of_max_uniform_oil_thickness.product_name] = distribution_of_max_uniform_oil_thickness.add_product
surface_gridded_products_map[uniform_oil_thickness_distribution.product_name] = uniform_oil_thickness_distribution.add_product

surface_gridded_products_map[max_of_spillet_thickness.product_name] = max_of_spillet_thickness.add_product
surface_gridded_products_map[thickest_spillet_oil_distribution.product_name] = thickest_spillet_oil_distribution.add_product
surface_gridded_products_map[distribution_of_thickest_spillet.product_name] = distribution_of_thickest_spillet.add_product
 
### Surface Shape     
surface_shape_products_map = {}
        
        
### Shore Gridded
shore_gridded_products_map = {}
shore_gridded_products_map[hit_count.product_name]                    = hit_count.add_product
shore_gridded_products_map[hit_probability.product_name]              = hit_probability.add_product

shore_gridded_products_map[oil_volume.product_name]                   = oil_volume.add_product
shore_gridded_products_map[oil_volume_distribution.product_name]      = oil_volume_distribution.add_product
shore_gridded_products_map[min_time.product_name]                     = min_time.add_product

shore_gridded_products_map[max_shore_grid_thickness.product_name]     = max_shore_grid_thickness.add_product
shore_gridded_products_map[distribution_of_max_shore_grid_thickness.product_name]   = distribution_of_max_shore_grid_thickness.add_product
shore_gridded_products_map[shore_oil_stats.product_name]   = shore_oil_stats.add_product

### Shore Shape
shore_shape_products_map = {}

### Subsurface Gridded
subsurface_gridded_products_map = {}
subsurface_gridded_products_map[hit_count.product_name]                    = hit_count.add_product
subsurface_gridded_products_map[hit_probability.product_name]              = hit_probability.add_product

subsurface_gridded_products_map[min_time.product_name]                     = min_time.add_product
subsurface_gridded_products_map[max_concentration.product_name]            = max_concentration.add_product

### Surface Shape
subsurface_shape_products_map = {}



