from mpl_toolkits.basemap import Basemap, cm
# requires netcdf4-python (netcdf4-python.googlecode.com)
from netCDF4 import Dataset 
import numpy as np
import matplotlib.pyplot as plt

from plot_function import plot_var, SAVE

# plot rainfall from NWS using special precipitation
# colormap used by the NWS, and included in basemap.


#nc = Dataset('./OilMdl_results/SCENARIO2_INST_SUMMER/scenario2_surface.nc')
#nc = Dataset('/Users/dstuebe/Documents/ASA Projects/13-092 Qatar Maersk/OilMdl_results/SCENARIO8_4WKS_SUMMER/scenario8_surface.nc')
nc = Dataset('transfer_prelim2_shore.nc')
#nc = Dataset('transfer_prelim2_surface.nc')


lats = nc.variables['latitude'][:]
lons = nc.variables['longitude'][:]

nsims = np.float32(nc.number_of_simulations)
ptype = nc.product_type


# Oil Volume
#data = np.log10(nc.variables['oil_volume'][:])
#units = 'Log10 Volume (m^3)'
#title = 'Total Oil Volume'
#clevs = np.linspace(0,8,17)
#plot_var(lats, lons, data, units, title, clevs)


# Min Time
data = nc.variables['min_time'][:]
#p_data = nc.variables['hit_probability'][:]/nsims
#mask_data = np.ma.array(data)
#mask_data[:] = np.ma.nomask
units = 'Days'
title = 'min time to oil'
plot_var(lats, lons, data, units, title)

#plot_var(lats, lons, mask_data/86400.0, units, title)

# 
# # hit probability
# data = nc.variables['hit_probability'][:]
# units = 'Probability'
# title = 'Probability of a grid cell being hit'
# clevs = np.linspace(0.01,1,28)
# p_h = data/nsims
# plot_var(lats, lons, p_h, units, title,clevs=clevs)
# 
# 
# # max_shore_grid_thickness
# data = nc.variables['max_shore_grid_thickness'][:]
# units = 'Log10 Thickness (nm)'
# title = 'Maximum Thickness (uniform method)'
# clevs = np.linspace(0,8,17)
# plot_var(lats, lons, np.log10(data*10**9), units, title,clevs=clevs)
# 
# 
# 
# # distribution_of_max_uniform_oil_thickness
# data = nc.variables['distribution_of_max_shore_grid_thickness'][:]
# 
# 
# units = 'Probability of thickness > 40 nm'
# title = 'Probability of the thickness occurring (diagonal grid length method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[2:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 1000 nm'
# title = 'Probability of the thickness occurring (diagonal grid length method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[10:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 10,000 nm'
# title = 'Probability of the thickness occurring (diagonal grid length method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[32:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 50,000 nm'
# title = 'Probability of the thickness occurring (diagonal grid length method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[70:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# 
# 
# units = 'Probability of thickness > 100,000 nm'
# title = 'Probability of the thickness occurring (diagonal grid length method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[100:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 

if not SAVE:
    plt.show()