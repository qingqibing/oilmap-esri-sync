import numpy
import matplotlib
import matplotlib.pyplot as plt

from pystoch import util
from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.grid_data import GridData
from pystoch.coroutines import *
from pystoch.readers.oilmdl_reader import OilModelDirectAccessReader

import logging
logger = logging.getLogger('pystoch.scripts.oilmdl_oil')

nSims = 12
fbase = './trajectory_data/oilmap/pystoch_test_case/PYSTOCHTESTCASE_s{0:03}'
DT(ndims=2,precision=numpy.float64,location_units='LatLon')

extents = numpy.ones(1,DT.EXTENTS)
extent_calc = extents_coroutine(extents)

# make the data streamer
streamer = stream_coroutine(target=extent_calc)


for i in xrange(nSims):
    fname = fbase.format(i+1)
    logger.info('Reading from file: "%s"' % fname)
    file_reader =  OilModelDirectAccessReader(fname)
    streamer.send(file_reader)

logger.info('Got Extents: %s' % extents )

# make the grid
#extents['ll'][:]= (13, -7.7)
#extents['ur'][:]= (10., -4.7)
# 11.541300711929594, -6.211698049988199

extents['ll'][:] = extents['ll'][:] - 0.1
extents['ur'][:] = extents['ur'][:] + 0.1

grid_dimensions = numpy.ndarray(1,DT.IVECTOR)
grid_dimensions[:] = 50

grid = Grid.create_floating(extents,grid_dimensions)

#make the grid data:
gd = GridData(grid)

gd.allocate('hit',numpy.bool8)
gd.allocate('time_hit',numpy.int32)
gd.allocate('oil_volume',DT.SPRECISION)

# make the aggregator for the results
aggregator = aggregate_coroutine(gd)

# make the gridder
gridder = grid_coroutine(grid, target=aggregator)

# make the data streamer
nblocks = 100
streamer = stream_coroutine(target=gridder)

scale = DT.PRECISION(60.0)
offset = DT.PRECISION(-10.0)

for i in xrange(nSims):
    if i == 2:
        continue
    fname = fbase.format(i+1)
    logger.info('Reading from file: "%s"' % fname)
    file_reader =  OilModelDirectAccessReader(fname)
    streamer.send(file_reader)
    

x,y = grid.meshgrid_c()

    
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
    
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('Pystoch Test Case')
#ax.xlabel('Meters')
#ax.ylabel('Meters')
CS = ax.contour(x, y, gd.oil_volume)
plt.clabel(CS, inline=1, fontsize=10)

plt.show()


fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('Pystoch Test Case')
#ax.xlabel('Meters')
#ax.ylabel('Meters')
CS = ax.contour(x, y, gd.hit)
plt.clabel(CS, inline=1, fontsize=10)

plt.show()


