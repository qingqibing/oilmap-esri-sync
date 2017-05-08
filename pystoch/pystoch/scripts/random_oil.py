import numpy
import matplotlib
import matplotlib.pyplot as plt


from pystoch import util
from pystoch.datatypes import DT, Singleton
from pystoch.grids import Grid
from pystoch.grid_data import GridData
from pystoch.coroutines import *
from pystoch.readers.random_generator import RandomWalkGenerator


DT(ndims=2,precision=numpy.float32,location_units='LatLon')

# make the grid
extents = numpy.ones(1,DT.EXTENTS)
extents['ll'] *= -10.0
extents['ur'] *= 50.0

grid_spacing = numpy.zeros(1,DT.VECTOR)
grid_spacing[:] = 4.0

grid = Grid.create_fixed(extents,grid_spacing)

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
bsize = 10000
nblocks = 100
streamer = stream_coroutine(blocksize=bsize, target=gridder)

scale = DT.PRECISION(60.0)
offset = DT.PRECISION(-10.0)

for i in xrange(3):
    file_reader =  RandomWalkGenerator(
        'noName',
        nblocks =nblocks,
        random_distribution = util.random_sample,
        random_offset = offset*numpy.ones(1,DT.VECTOR),
        random_scale = scale*numpy.ones(1,DT.VECTOR)
        )
    streamer.send(file_reader)
    

x,y = grid.meshgrid_c()

    
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
    
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('Oil Volume Hours for Random Uniform Particles')
#ax.xlabel('Meters')
#ax.ylabel('Meters')
CS = ax.contour(x, y, gd.oil_volume)
plt.clabel(CS, inline=1, fontsize=10)

plt.show()


