#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file distribution_reduce.py
@date 05/15/13
@description A configuration place holder till I have time to implement a real config
'''

import yaml
import sys
import dis

from singleton import Singleton
from util import pretty_print

__config_locked__ = False 

def config_lock(f):
    def locked(*args, **kwargs):
        if __config_locked__:
            raise AttributeError('Can not modify a locked config object')
        return f(*args, **kwargs)
    return locked

class DotNotationGetItem(object):
    """ Drive the behavior for DotList and DotDict lookups by dot notation, JSON-style. """

    def _convert(self, val):
        """ Convert the type if necessary and return if a conversion happened. """
        
        if isinstance(val, (DotDict, DotList)):
            return val, False
        
        if isinstance(val, dict):
            return DotDict(val), True
        elif isinstance(val, list):
            return DotList(val), True
        elif hasattr(val, '__iter__'):
            # can't get a set in a config object only list and dict
            # really should check on the way in (set) rather than during get...?
            raise AttributeError('Unexpected object type %s in DotNotationGetItem class can not be converted!' % val.__class__)
        else:
            return val, False

    @config_lock
    def __setitem__(self, key, val):
         if isinstance(self, list): 
            return list.__setitem__(self,key, val)
         if isinstance(self, dict): 
            return dict.__setitem__(self,key, val)
         
    @config_lock
    def __delitem__(self,key):
        if isinstance(self, list): 
            return list.__delitem__(self,key)
        if isinstance(self, dict): 
            return dict.__delitem__(self,key)
         
class DotList(DotNotationGetItem, list):
    """ Partner class for DotDict; see that for docs. Both are needed to fully support JSON/YAML blocks. """

    def __iter__(self):
        """ Monkey-patch the "next" iterator method to return modified versions. This will be slow. """
        #it = super(DotList, self).__iter__()
        #it_next = getattr(it, 'next')
        #setattr(it, 'next', lambda: it_next(it))
        #return it
        for val in super(DotList, self).__iter__():
            val, converted = self._convert(val)
            yield val

    def __getitem__(self, key):
        val = list.__getitem__(self, key)
        val, converted = self._convert(val)
        
        if converted: 
            list.__setitem__(self,key, val)

        return val   


    @config_lock        
    def append(self, x):
        return list.append(self,x)

    @config_lock        
    def extend(self, x):
        return list.extend(self,x)

    @config_lock        
    def insert(self, i, x):
        return list.insert(self, i, x)
        
    @config_lock        
    def pop(self, index=None):
        return list.pop(self,index)

    @config_lock        
    def remove(self, x):
        return list.remove(self,x)

    @config_lock        
    def reverse(self):
        return list.reverse(self)



class DotDict(DotNotationGetItem, dict):
    """
    Subclass of dict that will recursively look up attributes with dot notation.
    This is primarily for working with JSON-style data in a cleaner way like javascript.
    Note that this will instantiate a number of child DotDicts when you first access attributes;
    do not use in performance-critical parts of your code.
    """

    def __dir__(self):
        return self.__dict__.keys() + self.keys()

    def __getattr__(self, key):
        """ Make attempts to lookup by nonexistent attributes also attempt key lookups. """
        if self.has_key(key):
            return self[key]
        frame = sys._getframe(1)
        if '\x00%c' % dis.opmap['STORE_ATTR'] in frame.f_code.co_code:
            self[key] = DotDict()
            return self[key]

        raise AttributeError("Key '%s' not found in:\n%s" % (key, pretty_print(self)))

    @config_lock
    def __setattr__(self,key,value):
        if key in dir(dict):
            raise AttributeError('%s conflicts with builtin.' % key)
        if isinstance(value, dict):
            self[key] = DotDict(value)
        else:
            self[key] = value

    def __getitem__(self, key):
        try:
            val = dict.__getitem__(self, key)
        except KeyError:
            raise KeyError("""key '%s' not in DotDictionary keys: %s""" % (key, self.keys()))
        val, converted = self._convert(val)
        
        if converted: 
            dict.__setitem__(self,key, val)

        return val   

    def __contains__(self, item):
        return hasattr(self, item)
        

    @config_lock        
    def clear(self):
        return dict.clear(self)

    @config_lock        
    def pop(self,k,d=None):
        return dict.pop(self,k,d)

    @config_lock        
    def popitem(self):
        return dict.popitem(self)

    @config_lock        
    def update(self, *args, **kwargs):
        return dict.update(self,  *args, **kwargs)


class Config(DotDict):
    __metaclass__ = Singleton

    def __init__(self,fname=None):
    
        if fname is not None:
            with open(fname,'r') as f:
                yaml_dict = yaml.load(f)
        
            super(DotNotationGetItem, self).__init__(yaml_dict)
        
            self._lock()

    def _lock(self):
        # why do I need to declare this global here but not in the config_lock function
        global __config_locked__        
        __config_locked__ = True


    def _unlock(self):
        global __config_locked__        
        __config_locked__ = False

def get_config():
    return Config()

