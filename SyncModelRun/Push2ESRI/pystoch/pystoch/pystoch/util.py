#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file utils.py
@date 03/11/13
@description Utility module for functions and decorators
'''
import numpy
try:
    from collections import OrderedDict
except ImportError:
    from ordered_dictionary import OrderedDict

from datatypes import DT

from exceptions import PyStochParallelError

from pprint import pprint
import StringIO

import logging
logger = logging.getLogger('pystoch.util')

from parallel import *

from keywords import *

__all__ = [ 'random_sample',
            'coroutine',
            'stream_coroutine',
            'extents_coroutine',
            'union_extents',
            'pretty_print',
            ]


def pretty_print(obj):

    contents = "Pretty Print Failed :-("
    try:
        output = StringIO.StringIO()
        pprint(obj, output)
        contents = output.getvalue()
    finally:
        output.close()
    return contents
        
        
def random_sample(size=None,dtype=numpy.float64):
    """
    Replacement for numpy.random.random_sample which can provide random samples in the 
    interval [0..1) for float32 or float64. See https://github.com/numpy/numpy/issues/3155
    """
    type_max = 1 << numpy.finfo(dtype).nmant
    sample = numpy.empty(size, dtype=dtype)
    numpy.divide(numpy.random.randint(0, type_max, size=size), dtype(type_max), out = sample)
    if size is None:
        # return the scalar
        sample = sample[()]
    return sample


def coroutine(func):
    """
    Decorator function for coroutines to automatically call next so that they are in 
    a ready state when they are called
    """
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g
    return start



@coroutine
def stream_coroutine(target):
    result = None
    while True:      
        freader = (yield result)
        g = freader.stream_record_blocks()
        
        for block in g:
            result = target.send(block)

@coroutine
def list_coroutine(lst):
    while True:      
        res = (yield) 
        lst.append(res)


@coroutine
def extents_coroutine(ndims):
    
    result = DT.extents(ndims=ndims, prec=DT.DPRECISION)
    
    while True:      
            
        block = (yield result)
    
        #logger.info(block)
    
        # Each block from the reader is a dictionary containing one or more named sets of particles
        for key, value in block.iteritems():
    
            if key == METADATA:
                # Skip time
                continue

            if len(value)==0:
                continue

            particle_position = value['loc']            
    
            pmax = numpy.max(particle_position,axis=0)
            pmin = numpy.min(particle_position, axis=0)
            
            # Add a little margin to the actual value...
            result['ll'][0] = numpy.minimum(result['ll'][0], pmin - 0.001*abs(pmin))
            result['ur'][0] = numpy.maximum(result['ur'][0], pmax + 0.001*abs(pmax))


def union_extents(ext1, ext2, out=None):
    """
    Given two extents calculate the union of the bounding box
    """
    if out is None:
        out = DT.extents(ndims=ext1['ll'].shape[1],prec=ext1['ll'].dtype)
        
    out['ll'] = numpy.minimum(ext1['ll'],ext2['ll'])
    out['ur'] = numpy.maximum(ext1['ur'],ext2['ur'])
    
    return out
    
    
    
    




