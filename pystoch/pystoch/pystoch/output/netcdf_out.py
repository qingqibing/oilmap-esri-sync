#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file netcdf_out.py
@date 03/23/13
@description Implementation GridData output using netcdf4Python
'''
import numpy
from netCDF4 import Dataset
from pystoch import util
from pystoch.datatypes import DT
from pystoch.exceptions import PyStochIOError
import time

import logging
logger = logging.getLogger('pystoch.output.netcdf_out')


def netcdf_out(fname, scenario_name, nsims, product_type, grid_data):

    rootgrp = Dataset(fname, 'w', format='NETCDF3_64BIT')
    
    create_dimensions(rootgrp, grid_data)
    
    create_global_attributes(rootgrp, scenario_name, nsims, product_type, grid_data)
    
    create_variables(rootgrp, grid_data)
        
    rootgrp.close()
    
    
    
def create_dimensions(rootgrp, grid_data):
    
    dim_set = set()
    
    for varname, dim_dict in grid_data._dimensions.iteritems():
    
        for dimname, dim_size in dim_dict.iteritems():
        
            if dimname not in dim_set:
    
                logger.info('Creating dimension: %s - %s' % (dimname, dim_size))
                #logger.info(dim_set)
                rootgrp.createDimension(dimname, dim_size)
                dim_set.add(dimname)        



def create_global_attributes(rootgrp, scenario_name, nsims, product_type, grid_data):

    rootgrp.title = 'Pystoch Oil Analysis'
    rootgrp.institution = 'RPS ASA'
    rootgrp.source = 'pystoch version 0.1' #@todo - read a version number somewhere...
    rootgrp.history = 'Created ' + time.ctime(time.time())
    rootgrp.references = 'http://www.asascience.com/'
    rootgrp.comment = 'Stochastic oil analysis of %s' % scenario_name  
    rootgrp.description = 'pystoch stocastic oil model analysis'
    rootgrp.Conventions = "CF-1.6" 
    rootgrp.number_of_simulations = nsims
    rootgrp.product_type = product_type
    rootgrp.grid_left_lower = grid_data._grid.extents['ll']
    rootgrp.grid_right_upper = grid_data._grid.extents['ur']
    rootgrp.grid_spacing = grid_data._grid.grid_spacing
    

def create_variables(rootgrp, grid_data):

    
    for varname, array in grid_data.array_dictionary().iteritems():
    
        logger.info('Creating variable: %s' % varname)
        v_dims = tuple(grid_data._dimensions[varname].keys())
        
        kwargs = {}
        if 'fill_value' in grid_data._metadata[varname]:
            kwargs['fill_value'] = grid_data._metadata[varname]['fill_value']
                
        nc_var = rootgrp.createVariable(varname, array.dtype, v_dims, **kwargs)
        
        for attname, attval in grid_data._metadata[varname].iteritems():
            if attname == 'fill_value':
                continue
            if attval is None:
                continue
            setattr(nc_var, attname, attval)
            
            
        if "coordinates" not in grid_data._metadata[varname]:        
            nc_var.coordinates = 'longitude latitude'
              
        try:
            nc_var[:] = array
        except (IndexError, ValueError) as ex:
            logger.error('Index error writing variable "%s" to the netcdf file' % varname)
            logger.error(grid_data._dimensions[varname])
            logger.error(grid_data._metadata[varname])
            for dim in nc_var.dimensions:
                logger.error('NetCDF variable dimensions: %s - %s' % (dim, len(dim)))
            logger.error('Array shape: %s' % array.shape)
            
            raise ex
    
    
    
    
    
    



