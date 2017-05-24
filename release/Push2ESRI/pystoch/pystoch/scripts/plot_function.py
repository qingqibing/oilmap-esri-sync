from mpl_toolkits.basemap import Basemap, cm
# requires netcdf4-python (netcdf4-python.googlecode.com)
from netCDF4 import Dataset 
import numpy as np
import matplotlib.pyplot as plt

SAVE=False


def plot_var(lats, lons, data, units, title, clevs=None, mutable={'save':SAVE}):    
    # create figure and axes instances
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])

    m = Basemap(projection='merc',
            lat_ts=45.0,
            llcrnrlat=lats[0],
            urcrnrlat=lats[-1],
            llcrnrlon=lons[0],
            urcrnrlon=lons[-1],
            resolution='i',
            ax=ax
            )
        
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawcountries()

    # draw parallels.
    parallels = np.arange(0.,90,5.)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
    # draw meridians
    meridians = np.arange(0.,360.,5.)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
    ny = data.shape[0]; nx = data.shape[1]
    lonz, latz = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lonz, latz) # compute map proj coordinates.
    # draw filled contours.
    #clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
    if clevs is None:
        cs = m.contourf(x,y,np.transpose(data)) #,clevs)cmap=cm.s3pcpn)
        #cs = m.contourf(x,y,data) #,clevs)cmap=cm.s3pcpn)
    else:
        cs = m.contourf(x,y,np.transpose(data), levels=clevs) #,clevs)cmap=cm.s3pcpn)
        #cs = m.contourf(x,y,data, levels=clevs) #,clevs)cmap=cm.s3pcpn)
 
    # add colorbar.
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    cbar.set_label(units)
    # add title
    plt.title(title)
    
    if 'save' not in mutable:
        mutable['save'] = True
        
    if 'save_cnt' not in mutable:
        mutable['save_cnt'] = 1
    
    if mutable['save']:
        plt.savefig('figure_%s.png'% mutable['save_cnt'])
        mutable['save_cnt'] +=1
        