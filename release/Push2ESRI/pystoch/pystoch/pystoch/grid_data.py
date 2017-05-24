#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file grid_data.py
@date 03/11/13
@description GridData class for use in stochastic processing

'''
import numpy
import logging
from util import OrderedDict

from datatypes import DT
from exceptions import PyStochGridDataError
from keywords import *

from parallel import *

logger = logging.getLogger('pystoch.grid_data')

class DummyNumpy(numpy.ndarray):
    
    def __init__(self, dimensions, dtype=None):
        self.__dimensions = dimensions
        self.__dtype = dtype
        
    def __setitem__(self,*args):
        pass
        
    def __getitem__(self,*args):
        raise PyStochGridDataError("Can not getitem from the dummy object created in place of allocation (usually for parallel) with dimensions %s and dtype %s"% (self.__dimensions,self.__dtype))
        
    def __getattr__(self, name):
    
        raise PyStochGridDataError("Can not getattr '%s' from the dummy object created in place of allocation (usually for parallel) with dimensions %s and dtype %s"% (name,self.__dimensions,self.__dtype))
    

class GridData(object):
    """
    An object to hold the gridded data arrays using standard named variables  
    """
    def __init__(self, grid, defaults=None):
        """
        """
        super(GridData, self).__init__()
    
        self._base_dimensions = OrderedDict()
        self._base_dimensions[LONGITUDE] = grid.grid_dimensions[0]
        self._base_dimensions[LATITUDE] = grid.grid_dimensions[1]
        if len(grid.grid_dimensions) == 3:
            self._base_dimensions[HEIGHT] = grid.grid_dimensions[2]    
    
        self._arrays = []           # the name of the arrays...
        self._grid = grid           # The grid that the data is on
        self._initializations = {}  # Inital values for each array
        self._metadata = {}         # for use in writing out to netcdf - define attributes
        self._dimensions = {}       # for use in writing out to netcdf - define additional dimensions
               
        self._grid_has_coordinates = False
                
        if defaults is not None:

            for (k,v) in defaults.iteritems():
                if hasattr(v, 'dtype'):
                    self.allocate(k,dtype=v)
                elif isinstance(v, dict):
                    self.allocate(k,**v)
                else:
                    raise PyStochGridDataError('Invalid argument in defaults with name "%s" and value: %s' % (k,v))

    @property
    def base_dimensions(self):
        """
        Always return a copy!
        """
        return self._base_dimensions.copy()

    def allocate_coordinate(self,name,dtype,data_dimension=None, initialize=0.0, metadata=None, store=True):
        """
        Add a special array to be used as a coordinate variable for a n dimensional array
        """
        if isinstance(data_dimension, OrderedDict):
            dimensions = tuple(dim for dim in data_dimension.itervalues())
        else:
            raise PyStochGridDataError('Invalid argment grid_data_dimension. Expected None or dictionary, recieved: %s' % data_dimension)
        
        array = numpy.zeros(dimensions,dtype=dtype)
        
        if initialize is not 0.0:
            array[:] = initialize
        
        if store:
            self.insert(name, array, data_dimension, initialize, metadata)
        return array

    def _make_lat_lon(self):
    
        if not self._grid_has_coordinates:
    
            coords = self._grid.coordinates("B") 
            # @todo make the grid data 1D variables


            # Create the Longitude
            dims = OrderedDict()
            dims[LONGITUDE] = self._grid.grid_dimensions[0]

            metadata = {
                'units':'degrees_east',
                'long_name':LONGITUDE,
                'coordinates':None,
                'CoordinateAxisType':'Lon',
                }
            longitudes = self.allocate_coordinate(LONGITUDE, DT.PRECISION, data_dimension=dims, metadata=metadata)
            longitudes[...] = coords[0]

            # Create the Latitude
            dims = OrderedDict()
            dims[LATITUDE] = self._grid.grid_dimensions[1]

            metadata = {
                'units':'degrees_north',
                'long_name':LATITUDE,
                'coordinates':None,
                'CoordinateAxisType':'Lat'
                }
            latitudes = self.allocate_coordinate(LATITUDE, DT.PRECISION, data_dimension=dims, metadata=metadata)
            latitudes[...] = coords[1]

            self._grid_has_coordinates = True


    def allocate(self,name,dtype, grid_data_dimension=None, initialize=0.0, metadata=None, store=True, only_if_msr=False):
        """
        Add a custom name for a new data type
        name - the name of the array in the grid data object
        dtype - the type of the elements in the array
        grid_data_dimension - the dimension of the elements in the grid (allows nbins/element)
        initialize - a value with with to initialize every element of the array, also used in zero_out
        """
        if ' ' in name:
            raise RuntimeError('Can not use a grid data name with white space in it!')
                
        if grid_data_dimension is None:
            dd = self.base_dimensions
        else:
            dd = grid_data_dimension.copy()
            dd.update(self.base_dimensions)
            
        dimensions = tuple(dim for dim in dd.itervalues())
        
        if not only_if_msr or mpi_msr:
            logger.info('Allocating real array %s' % name)
            array = numpy.zeros(dimensions,dtype=dtype)
            
            # make the coordinate axes too:
            self._make_lat_lon()
            
        else:
            logger.info('Dummy Allocation %s' % name)

            array = DummyNumpy(dimensions,dtype=dtype)
        
        if initialize is not 0.0:
            array[:] = initialize
            
        if store:
            self.insert(name, array, dd, initialize, metadata)
        return array
        
    def make_bin_data(self, name, nbins, bin_coefficient):
        '''
        Ensure that all bin data is the same and only created once
        '''
        logger.info('Calling make_bin_data: %s, %s, %s' % (name, nbins, bin_coefficient))

        if hasattr(self, name):
        
            dims = self._dimensions[name]
            current_bins = dims.get(name)
            if current_bins != nbins:
                raise PyStochGridDataError("Can not make a second bin data '%s' with different number of bins!" % name)
        
            metadata = self._metadata[name]
            if metadata['bin_coefficient'] != bin_coefficient:
                raise PyStochGridDataError("Can not make a second bin data '%s' with different bin coefficients!" % name)
                
            bin_values = self[name]

        else:

            #allocate space for the gridded result
            dims = OrderedDict()
            dims[name] = nbins 

            metadata = {
                'units':'m',
                'long_name':'lower bin edge values',
                'coordinates':None,
                'positive':'down',
                'CoordinateAxisType':'Height', # hack so it works in toolsUI
                'bin_coefficient':bin_coefficient,
                'bin_function':'quadratic'
                }
            bin_values = self.allocate_coordinate(name, DT.PRECISION, data_dimension=dims, metadata=metadata)
    
            for i in xrange(len(bin_values)):
                    bin_values[i] = (bin_coefficient * i)**2

        return dims, bin_values

    
    def make_filename_data(self, name, file_names):
        
        string_len = max([len(fname) for fname in file_names])
        
        dtype = "S1"
        
        dims = OrderedDict()
        dims[NSIMS] = len(file_names)
        dims['string'] = string_len +1

        metadata = {
            'units':'none',
            'long_name':'Simulation files processed for this analysis',
            'coordinates':None,
            'CoordinateAxisType':'SimStats'
            }
            
        name_array = self.allocate_coordinate(name, dtype, data_dimension=dims, metadata=metadata)

        for i in xrange(len(file_names)):
            for j, char in enumerate(file_names[i]):
                name_array[i,j] = char
            name_array[i,j+1] = '\n'
            
        return name_array
        
        
    def insert(self, name, array, grid_data_dimension, initialize, metadata):

        if hasattr(self,name):
            raise PyStochGridDataError("The array '%s' already exists!" % name)
            
        self.__setattr__(name,array)
        self._arrays.append(name)   
        
        self._initializations[name] = initialize
        
        self._metadata[name] = metadata or {}
        
        self._dimensions[name] = grid_data_dimension or OrderedDict()

        
        
    def zero_out(self):
        """
        zero out the current value in all arrays
        Reinitialize with the specified value
        """
        
        for name in self._arrays:
            self.__getattribute__(name)[:] = self._initializations.get(name,0.0)
        
        
    def array_dictionary(self, prefix=''):
        """
        Return a dictionary of arrays from the grid data object with prefixed names
        suitable for use in numexpr expressions.
        """
        c={}
        #return c.update([(prefix + k, a[k]) for k in self._arrays])    
        for k in self._arrays:
            c[prefix + k] = self[k]
        return c
        
    def array_names(self):
        return self._arrays

    def copy(self, result=None):
        """
        Copy all the arrays in this grid data into a new/other grid data object
        For testing purposes only. If you are using this in production think carefully.
        """
        
        if result is None:
            result = GridData(self._grid,defaults={})
    
        
        for (k,v) in self.array_dictionary().iteritems():
            result.insert(k,v.copy(), self._dimensions[k], self._initializations[k], self._metadata[k])
            
        return result
        
    
    def __getitem__(self, name):
        """
        Provide dictionary getter for programatic access to arrays
        """
        try:
            return self.__getattribute__(name)
        except AttributeError as AE:
            logger.exception(AE)    
            raise KeyError('Attribute error caught during key access to grid_data object by name "%s"' % name)  
        
        

