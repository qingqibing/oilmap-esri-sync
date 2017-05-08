#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file datatypes.py
@date 03/11/13
@description Define some datatype used in this program
'''

import numpy
import logging

from singleton import Singleton

logger = logging.getLogger('pystoch.datatypes')



class DT(object):
    __metaclass__ = Singleton

    # these are truely static types used in other cases
    SPRECISION = numpy.float32
    DPRECISION = numpy.float64
    
    INT32 = numpy.int32
    INT64 = numpy.int64
    
    # Vectors are: Longitude, Latitude, (Height - positive upward!)
    
    VECTORDP2D= numpy.dtype((DPRECISION, 2))
    VECTORDP3D = numpy.dtype((DPRECISION, 3))

    VECTORSP2D= numpy.dtype((SPRECISION, 2))
    VECTORSP3D = numpy.dtype((SPRECISION, 3))

    # a point is a particular type of vector
    POINTSP2D = VECTORSP2D
    POINTSP3D = VECTORSP3D
    
    POINTDP2D = VECTORDP2D
    POINTDP3D = VECTORDP3D

    # Extents in Version -10
    VER10EXTENT2D = numpy.dtype((SPRECISION, 4))
    VER10EXTENT3D = numpy.dtype((SPRECISION, 6))


    def __init__(self, ndims=2, precision=numpy.float64, location_units='LatLon'):


        
        DT.PRECISION = precision
        DT.NDIMS = ndims
        DT.LOCATION_UNITS = location_units

        DT.VECTOR = numpy.dtype((DT.PRECISION, DT.NDIMS))
                
        DT.POINT = DT.VECTOR

        DT.IVECTOR = numpy.dtype((numpy.int32,DT.NDIMS))
        
        DT.POINT_INDEX = DT.IVECTOR

        DT.PARTICLE = numpy.dtype([('loc', DT.POINT, 1),
                                    ('prev_loc', DT.POINT, 1)
                                    ])
           
        # Keep this for backward compatibility with tests cases
        DT.EXTENTS = DT.extent_type()                         


        # Based on variables read in RunStoch and their type...
        DT.IDEAL_PARTICLE = numpy.dtype([('loc', DT.POINT, 1),
                                    ('prev_loc', DT.POINT, 1),
                                    ('mass',DT.SPRECISION,1),
                                    ('density',DT.SPRECISION,1),
                                    ('lifetime',DT.SPRECISION,1),
                                    ('radius',DT.SPRECISION,1),
                                    ])


    @staticmethod
    def extents(ndims=None, prec=None,ur_default=(-360,-90,-100000), ll_default=(360,90,100000)):
        """
        Create an extent array and return it based on the number of dimensions and the precision specified and initialize it
        """
        
        ext_type = DT.extent_type(ndims,prec)
        ext = numpy.zeros(1,ext_type)

        for i in xrange(ndims):
            ext['ur'][0][i] = ur_default[i]
            ext['ll'][0][i] = ll_default[i]
    
        return ext

    @staticmethod
    def extent_type(ndims=None, prec=None,):
        """
        Create an extent type and return it based on the number of dimensions and the precision specified
        """
        if ndims is None:
            ndims = DT.NDIMS
            
        if prec is None:
            prec = DT.PRECISION
        
        ext_type = numpy.dtype([('ll', numpy.dtype((prec,ndims),),1),('ur', numpy.dtype((prec,ndims),),1)])

        return ext_type



