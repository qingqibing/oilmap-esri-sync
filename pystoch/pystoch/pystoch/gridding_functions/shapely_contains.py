#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file bin_grid.py
@date 08/27/13
@description A module containing a courtine for determining which spillets are contained
in a set of polygons defined by a shape file
'''
import numpy
import logging
logger = logging.getLogger('pystoch.gridding_function.shapely_contains')

from pystoch.datatypes import DT
from pystoch import util
from shapely.geometry import Point
from shapely import speedups

if speedups.available:
    logger.info('Turned on shapely speedups')
    speedups.enable()
    

# Name for this shape analysis methods:
shape_function_name = 'shapely contains'

@util.coroutine
def shape_function(shapes,operators):

    slen = len(shapes)
    

    while True:
        (block, metadata) = (yield) # an array of particle datatype
                
        blen = len(block)
        
        particle_position = block['loc']
        
        spillets_in_shape = numpy.zeros((blen, slen),dtype='bool')
        
        for i, pos in  enumerate(particle_position):
            p = Point(pos)
            for j,shape in enumerate(shapes.itervalues()):
                if shape.intersects(p):
                    spillets_in_shape[i,j] = True
                
        for target in operators:
            # send: Particles, index_position, weights and metadata for each cell
            target.send((block,spillets_in_shape, metadata))
        