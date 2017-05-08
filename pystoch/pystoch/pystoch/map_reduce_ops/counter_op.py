#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file counter_op.py
@date 03/11/13
@description A module containing a function for counting the number of spillets that have entered a grid cell
'''
import numpy
import logging

try:
    # Temporary hack till I get support setup for building/installing on windows
    import pyximport
    #pyximport.install(setup_args={"script_args":["--compiler=mingw32"],"include_dirs":numpy.get_include()}, reload_support=True)
    pyximport.install(setup_args={"include_dirs":numpy.get_include()}, reload_support=True)
    import counter
except:
    counter = None
    
try: 
    from scipy import sparse
except:
    sparse = None

from pystoch import util
from pystoch.exceptions import PyStochOperatorError

logger = logging.getLogger('pystoch.operators.counter_op')

# To forcible turn of cython counter, uncomment: counter = None
#counter = None
# To forcible turn of scipy coutner, uncomment: sparse = None
#sparse = None

# If both are set to None, it will default to the pure python implementation which is really slow!


@util.coroutine
def counter_op(result):

    if not isinstance(result, numpy.ndarray):
        raise PyStochOperatorError('Invalid result argument in count operation. Received type: %s' % type(result))

    try:
        if counter is not None:
            logger.info('In cython while loop for counting hits')
            while True:
                block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
            
                # Call cython implementation
                counter.c_counter(result, index_position)

        elif sparse is not None:
            logger.info('In scipy while loop for counting hits')
            while True:
                block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
            
                rank = index_position.shape[1]
                blen = index_position.shape[0]
                da = sparse.coo_matrix( (numpy.ones(blen),[index_position[:,i] for i in xrange(rank)] ), result.shape)
            
                result += da.A
            
        else:
            logger.info('In pure python while loop for counting hits :-(')
            while True:
                block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
                ## Works but slow...
                for i in xrange(index_position.shape[0]):
                    result[tuple(index_position[i,:])] += 1
            
            ### does not work
            #for x in numpy.nditer(result[[index_position[:,i] for i in xrange(index_position.shape[1])]], op_flags=['readwrite'],flags=['buffered']):
            #    x[...] +=1
            #result[[index_position[:,i] for i in xrange(index_position.shape[1])]] = x
            
            #for x in numpy.nditer(index_position, flags=['external_loop'], order='C'):
            #    print x
            #    result[x] += 1
            
            
            
    except IndexError as ie:
    
         
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in counterp_op coroutine')
        
        raise 
        
    except ValueError as ve:
        logger.info('Result dtype & shape: %s; %s' % (result.dtype, result.shape))
        logger.info("index_position: %s, %s" % (index_position.dtype, index_position.shape) )
        logger.info("Value error raised during call cython.c_counter - usually means one of the two arrays was of the wrong type or dimension")
        
        raise
