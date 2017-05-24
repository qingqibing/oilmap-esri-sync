#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file shore_oil_stats_op.py
@date 03/11/13
@description Calculate shore oil stats (mass ashore, percent hit shore etc...)
'''

import numpy
import logging

from pystoch import util
from pystoch.exceptions import PyStochOperatorError
from pystoch.keywords import *

logger = logging.getLogger('pystoch.map_reduce_ops.shore_oil_stats_op')

# Make a list of product names

FIRST_CONTACT_LATITUDE = 'first_contact_latitude'
FIRST_CONTACT_LONGITUDE = 'first_contact_longitude'
TIME_TO_SHORE = 'time_to_shore'
MASS_OF_OIL_ONSHORE =  'mass_of_oil_onshore'



@util.coroutine
def shore_oil_stats_op(value_map, cell_area):


    try:

        while True:
            block, index_position, weight, metadata = (yield) # Standard arguments passed from the grid_mapper
            

            if (len(block) > 0): # There is shore oil...
            
                if value_map[TIME_TO_SHORE] == -1:
                    value_map[TIME_TO_SHORE] = metadata[TIME][ETIME]
    
                    value_map[FIRST_CONTACT_LATITUDE] = block['loc'][0][1]
            
                    value_map[FIRST_CONTACT_LONGITUDE] = block['loc'][0][0]
            
                value_map[MASS_OF_OIL_ONSHORE] += sum(block['mass'])
            
            
            
    except IndexError as ie:
    
         
        logger.info('block:\n%s' % block)
        logger.info('index_position:\n%s' % index_position)
        logger.info('weight:\n%s' % weight)
        
        logger.info('Result Array shape: %s' % list(result.shape))    
        logger.error('Hit an index exception in counterp_op coroutine')
        
        raise 