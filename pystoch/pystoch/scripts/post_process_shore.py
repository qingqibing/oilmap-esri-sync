#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file netcdf_out.py
@date 03/23/13
@description Implementation GridData output using netcdf4Python

This script is deprecated - it was used to change dimension names 'lat' and 'lon' to 
'longitude' and 'latitude' before pystoch was updated to use the same dimension and 
variable name.
'''
import numpy
import os
from netCDF4 import Dataset

input_name = 'scenario10_final_shore.nc'

head, tail = os.path.split(input_name)
output_name = '%s_post_process.nc' % tail[:-3] 

input = Dataset(input_name)
output = Dataset(output_name, 'w', format='NETCDF3_64BIT')



output.createDimension('latitude',len(input.dimensions['lat']))
output.createDimension('longitude',len(input.dimensions['lon']))


def copy_attrs(source, att_names, dest):
    for att_name in att_names:
        if att_name == '_FillValue': 
            continue
        setattr(dest, att_name, getattr(source,att_name))

def copy_vars(source, var_names, dest):
    for var_name in var_names:
        s_var = source.variables[var_name]
        
        kwargs = {}
        if hasattr(s_var,'_FillValue'):
            kwargs['fill_value'] = s_var._FillValue
            
        dims = s_var.dimensions
        new_dims = []
        for d in dims:
            if d == 'lon':
                new_dims.append('longitude')
            if d == 'lat':
                new_dims.append('latitude')
                
            
        d_var = dest.createVariable(var_name, s_var.dtype, tuple(new_dims), **kwargs)
    
        copy_attrs(s_var, s_var.ncattrs(), d_var)

        print d_var
        print s_var

        # assume small enough to copy in one shot...        
        d_var[:] = s_var[:]

copy_attrs(input, input.ncattrs(), output)
output.title = 'Pystoch post processing analysis'

## To copy all existing use this:
#copy_vars(input, input.variables.keys(), output)


copy_vars(input, input.variables.keys(), output)



input.close()
output.close()
     