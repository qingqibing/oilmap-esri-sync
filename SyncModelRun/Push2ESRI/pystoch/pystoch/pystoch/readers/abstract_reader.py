#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file abstract_reader.py
@date 03/11/13
@description An abstract class for the particle readers
'''
from pystoch import util

class AbstractParticleReader(object):
    
    # a mapping of the spillet types associated with a given product (Surface, Subsurface, Shore...)
    product_spillet_map = {}
    
    
    
    def __init__(self,*args,**kwargs):
        """
        @fname is the name of the file to read from
        @blocksize is the number of particle records to read per block of data returned
        """
        # Ensure all constructors are called properly
        super(AbstractParticleReader, self).__init__()
    
        self.spillet_types = {}
        
        self.fname = args[0]
        
 
        
    def stream_record_blocks(self):
        """
        A generator function which yields blocks of particle records to the caller
        """
        raise NotImplementedError

    def get_temporal_extents(self):
        raise NotImplementedError('Implement time bounds for reader')
        
    def get_surface_extents(self):
        raise NotImplementedError('Implement time bounds for reader')

    def get_subsurface_extents(self):
        raise NotImplementedError('Implement time bounds for reader')
            
    def get_extents(self,ndims, spillets=None):
        """
        spillets is a list/tuple of the types of spillets to calculate the extent over
        #@todo Will crash if you mix spillets with 2d and 3d coordinates!
        """
        ext_co = util.extents_coroutine(ndims)
        
        if spillets is None:
            spillets = self.spillet_types.keys()
        
        for block in self.stream_record_blocks(spillets):
            extents = ext_co.send(block)
    
        return extents
    
        
    @classmethod
    def get_output_map(cls, product_keys):
        """
        return: product_read_map 
            Keys are product keys (Surface, Subsurface, Shoreline),
           Values are a list of spillet output types
        """
        result = {}
        for p_key in product_keys:
            # put a copy of the spillet names associated with the product key in the result dictionary
            result[p_key] = list(cls.product_spillet_map[p_key])
        
        return result    