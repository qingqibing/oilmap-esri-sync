#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file netcdf_out.py
@date 03/23/13
@description Implementation GridData output using netcdf4Python
'''
import numpy
import os
from netCDF4 import Dataset

input_name = '/Users/dstuebe/Documents/ASA Projects/kara_sea/mpi_run_surface.nc'

head, tail = os.path.split(input_name)
output_name = '%s_post_process.nc' % tail[:-3] 

input = Dataset(input_name)
output = Dataset(output_name, 'w', format='NETCDF3_64BIT')

output.createDimension('latitude',len(input.dimensions['latitude']))
output.createDimension('longitude',len(input.dimensions['longitude']))


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
            
        d_var = dest.createVariable(var_name, s_var.dtype, dims, **kwargs)
    
        copy_attrs(s_var, s_var.ncattrs(), d_var)

        print d_var
        print s_var

        # assume small enough to copy in one shot...        
        d_var[:] = s_var[:]

copy_attrs(input, input.ncattrs(), output)
output.title = 'Pystoch post processing analysis'

## To copy all existing use this:
#copy_vars(input, input.variables.keys(), output)

var_copy_list=[
    'latitude',
    'longitude',
    #'hit_count',
    #'min_time',
        
    ## Surface variables
    #'max_of_uniform_oil_thickness',
    'max_of_spillet_thickness',

    ## Shore variables
    #'max_shore_grid_thickness',
    

    ]
copy_vars(input, var_copy_list, output)

#### Manually create variables!
nsims = numpy.float32(input.number_of_simulations)

## make a floating point variable for probability
p_data = input.variables['hit_probability'][:]/nsims
dest = output.createVariable('probability_of_oiling', numpy.float32, ('longitude','latitude'))
dest.coordinates = "longitude latitude"
dest.units = "probability"
dest.long_name = 'Probability of oiling during simulated spills'
dest[:] = p_data


## dump masked min_time to oiling based on 0.01 probability
source = input.variables['min_time']
dest = output.createVariable('masked_min_time', numpy.float32, ('longitude','latitude'), fill_value=-1.0)
copy_attrs(source, ['coordinates','long_name'],dest)
dest.units = 'time in hours'
data = numpy.ma.array(source[:])/3600.
data[p_data < 0.01] = numpy.ma.masked
dest[:] = data


## Surface
source = input.variables['distribution_of_thickest_spillet']
## Shore
#source = input.variables['distribution_of_max_shore_grid_thickness']
p_data = source[:]

# dest = output.createVariable('probability_of_oiling_gt_40nm', numpy.float32, ('longitude','latitude'))
# dest.coordinates = "longitude latitude"
# dest.units = "probability"
# dest.long_name = 'Probability of oiling during simulated spills'
# dest[:] = numpy.sum(p_data[2:,...],0)/nsims
# 
# dest = output.createVariable('probability_of_oiling_gt_1000nm', numpy.float32, ('longitude','latitude'))
# dest.coordinates = "longitude latitude"
# dest.units = "probability"
# dest.long_name = 'Probability of oiling during simulated spills'
# dest[:] = numpy.sum(p_data[10:,...],0)/nsims

dest = output.createVariable('probability_of_oiling_gt_50000nm', numpy.float32, ('longitude','latitude'))
dest.coordinates = "longitude latitude"
dest.units = "probability"
dest.long_name = 'Probability of oiling during simulated spills'
dest[:] = numpy.sum(p_data[70:,...],0)/nsims



#### Process stats array to csv!
## Surface
stats_array = 'area_oiled_stats_by_thickest_spillet_method'
## Shore
#stats_array = 'shore_line_oiled_stats_by_grid_thickness_method'


table = input.variables[stats_array][:]
head, tail = os.path.split(input_name)
output_name = '%s_stats.csv' % tail[:-3] 

thickness = input.variables['thickness_bins'][:]

shape = list(table.shape)
shape[1] += 1
new_array = numpy.zeros(shape)
new_array[:,0] = thickness[:]
new_array[:,1:] = table

file_names_array = input.variables['file_names'][:]
file_names_list = ['thickness(m)',]
for i in xrange(file_names_array.shape[0]):
    fpath = ''.join(file_names_array[i,:].tolist())
    fpath = fpath[:fpath.index('\r')]
    head, tail = os.path.split(fpath)
    file_names_list.append(tail)
    
numpy.savetxt(output_name, new_array, delimiter=",", header=','.join(file_names_list))

input.close()
output.close()
     