#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file grids.py
@date 03/11/13
@description Grid class for use in stochastic processing

@todo Fix/flatten the dimension of all the vectors
'''
import numpy
from datatypes import DT
from exceptions import PyStochError
import logging
logger = logging.getLogger('pystoch.grids')

METERS_PER_DEGREE = 111000.0

class Grid(object):
    """
    Grid object does not actually allocate a grid unless it is requested
        # Vectors are: Longitude, Latitude, (Height - positive upward!)
    """
    
    
       
    FLOATING = 'floating'
    FIXED = 'fixed'
    FILE = 'file'
    
    def __init__(self, extents, grid_spacing, grid_dimensions):
        # Ensure all constructors are called properly
        super(Grid, self).__init__()
        
        self.extents = extents.flatten()
        # flatten is already a copy operation
        self.grid_spacing = grid_spacing.flatten() 
        self.grid_dimensions = grid_dimensions.flatten()
        
        assert (self.grid_dimensions > 0).all(),  'Grid dimensions must be positive'
        
        if grid_dimensions.prod() > 10**5:
            logger.warn('Grid Dimensions specify greater than 100,000 elements!')
        if grid_dimensions.prod() > 10**6:
            raise RuntimeError('Grid Dimension too large! Do no run with more than 1,000,000 elements.')
        

    
    @classmethod
    def create_from_file(cls, file):
        pass
        
    @classmethod
    def create_fixed(cls, extents=None, grid_spacing=None):
    
        span = (extents['ur'] - extents['ll'])
        logger.debug(span)
        
        assert (span > 0.0).all(), 'The upper right extent must be greater than the lower left extent'

        grid_spacing = numpy.array(grid_spacing,dtype=DT.PRECISION).flatten()
    
        grid_dimensions = numpy.zeros(grid_spacing.shape,dtype=numpy.int32)
        numpy.floor_divide(span.flatten(),grid_spacing, out=grid_dimensions)
        return cls(extents, grid_spacing, grid_dimensions)
        
    @classmethod
    def create_floating(cls, extents=None, grid_dimensions=None):

        span = (extents['ur'] - extents['ll'])
        assert (span > 0.0).all(), 'The upper right extent must be greater than the lower left extent'
        
        grid_dimensions = numpy.array(grid_dimensions,dtype=numpy.int32).flatten()

        grid_spacing = numpy.zeros(grid_dimensions.shape,dtype=DT.PRECISION)

        grid_spacing[:] = span/grid_dimensions
        return cls(extents, grid_spacing, grid_dimensions)
        
    def indexof(self,data,out=None):
        '''
        Assume data is an array of arbitrary dimension return a array of the same dimension
        containing the index location of the points in data.
        '''
        index = out
        if out is None:
            index = numpy.zeros(data.shape,dtype=numpy.int32)
        
        #logger.info("self.extents['ll']: \n %s" % self.extents['ll'])
        #logger.info("self.grid_spacing: \n %s" % self.grid_spacing)
        
        numpy.floor_divide(data-self.extents['ll'],self.grid_spacing, out=index)
        
        return index
            
    @property
    def cell_area(self):
    
        center = (self.extents['ur'] + self.extents['ll']) / 2.0 
        
        lat_c = center.flatten()[1] 

        return self.grid_spacing[:2].prod()*METERS_PER_DEGREE**2*numpy.cos(lat_c*numpy.pi/180.0) 
    
        
    @property
    def cell_diagonal(self):
    
        center = (self.extents['ur'] + self.extents['ll']) / 2.0 
        
        lat_c = center.flatten()[1] 
            
        return numpy.sqrt((self.grid_spacing[0]*METERS_PER_DEGREE)**2 + (self.grid_spacing[1]*METERS_PER_DEGREE*numpy.cos(lat_c*numpy.pi/180.0))**2)

        
    def meshgrid(self, grid_type):
    
        spacing = self.coordinates(grid_type)
        return numpy.meshgrid(*spacing) 
            
    def coordinates(self, grid_type):
        spacing = []
        
        if grid_type == 'A':
            for dim in xrange(DT.NDIMS):
                x = numpy.linspace( self.extents['ll'][0][dim], 
                                    self.extents['ur'][0][dim],
                                    self.grid_dimensions[dim] + 1 )            
                spacing.append(x)
                
        elif grid_type == 'B':
            for dim in xrange(DT.NDIMS):
                x = numpy.linspace( self.extents['ll'][0][dim]+self.grid_spacing[dim]/2.0, 
                                    self.extents['ur'][0][dim]-self.grid_spacing[dim]/2.0,
                                    self.grid_dimensions[dim] )            
                spacing.append(x)
        else:
            raise PyStochError('Invalid grid_type "%s" specified in coordinates function!' % grid_type)

        return spacing
    

    def __str__(self):
        str = ""
        str += "======== Printing Grid Object ==========\n"
        str += "= Grid extents: '%s'\n" % self.extents
        str += "= Grid dimensions: '%s'\n" % self.grid_dimensions
        str += "= Grid spacing: '%s'\n" % self.grid_spacing
        str += "========== End Grid Object =============\n"
        return str

        
    
    


