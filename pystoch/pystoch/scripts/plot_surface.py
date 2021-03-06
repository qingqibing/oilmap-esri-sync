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
nc = Dataset('blowout_prelim_stats_surface.nc')
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
#mask_data[p_data < 0.01] = np.ma.masked
units = 'Days'
title = 'min time to oil'
plot_var(lats, lons, data/86400.0, units, title)
#plot_var(lats, lons, mask_data/86400.0, units, title)

# 
# # max_of_uniform_oil_thickness
# data = nc.variables['max_of_uniform_oil_thickness'][:]
# units = 'Log10 Thickness (nm)'
# title = 'Maximum Thickness (uniform method)'
# clevs = np.linspace(0,8,17)
# plot_var(lats, lons, np.log10(data*10**9), units, title,clevs=clevs)

# hit probability
data = nc.variables['hit_probability'][:]
units = 'Probability'
title = 'Probability of a grid cell being hit'
clevs = np.linspace(0.01,1,28)
p_h = data/nsims
plot_var(lats, lons, p_h, units, title,clevs=clevs)

## uniform_oil_thickness_distribution
#data = nc.variables['uniform_oil_thickness_distribution'][:]
#
#units = 'Probability of thickness > 0.1 mm given oiling'
#title = 'Probability of thickness given oiling occuring'
#clevs = np.linspace(0.05,1,20)
#counts = np.sum(data[1:,...],0)
#mask_data = np.ma.array(np.sum(data[100:,...],0)/counts)
#mask_data[counts < 10] = np.ma.masked
#plot_var(lats, lons, mask_data, units, title, clevs)
#
#
#units = 'Probability of thickness > 0.1 mm'
#title = 'Probability of a thickness'
#plot_var(lats, lons, mask_data*p_h, units, title, clevs)



# max_of_spillet_thickness
data = nc.variables['max_of_spillet_thickness'][:]
units = 'Log10 Thickness (nm)'
title = 'Maximum Thickness (spillet method)'
clevs = np.linspace(0,8,17)
plot_var(lats, lons, np.log10(data*10**9), units, title,clevs=clevs)

# 
# # distribution_of_max_uniform_oil_thickness
# data = nc.variables['distribution_of_max_uniform_oil_thickness'][:]
# 
# 
# units = 'Probability of thickness > 40 nm'
# title = 'Probability of the thickness occurring (uniform method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[2:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 1000 nm'
# title = 'Probability of the thickness occurring (uniform method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[10:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 10,000 nm'
# title = 'Probability of the thickness occurring (uniform method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[32:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# units = 'Probability of thickness > 50,000 nm'
# title = 'Probability of the thickness occurring (uniform method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[70:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# 
# 
# units = 'Probability of thickness > 100,000 nm'
# title = 'Probability of the thickness occurring (uniform method)'
# clevs = np.linspace(0.01,1,28)
# mask_data = np.ma.array(np.sum(data[100:,...],0)/nsims)
# mask_data[mask_data <= 0.01] = np.ma.masked
# plot_var(lats, lons, mask_data, units, title, clevs)
# 
# 
# #units = 'Probability of 40 nm < thickness < 5,000 nm'
# #title = 'Probability of the thickness occurring (uniform method)'
# #clevs = np.linspace(0.01,1,28)
# #mask_data = np.ma.array(np.sum(data[1:12,...],0)/nsims)
# #mask_data[mask_data <= 0.01] = np.ma.masked
# #plot_var(lats, lons, mask_data, units, title, clevs)
# 

# distribution_of_thickest_spillet
data = nc.variables['distribution_of_thickest_spillet'][:]

units = 'Probability of thickness > 40 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[2:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)

units = 'Probability of thickness > 1000 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[10:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)

units = 'Probability of thickness > 10,000 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[32:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)

units = 'Probability of thickness > 50,000 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[70:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)


units = 'Probability of thickness > 100,000 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[100:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)


units = 'Probability of thickness > 323,000 nm'
title = 'Probability of the thickness occurring (spillet method)'
clevs = np.linspace(0.01,1,28)
mask_data = np.ma.array(np.sum(data[190:,...],0)/nsims)
mask_data[mask_data == 0.0] = np.ma.masked
plot_var(lats, lons, mask_data, units, title, clevs)

if not SAVE:
    plt.show()
