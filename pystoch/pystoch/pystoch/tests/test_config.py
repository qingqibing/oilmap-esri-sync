from nose.tools import *
import unittest

from pystoch import config
from pystoch.config import Config, DotDict
from pystoch.keywords import *
from pystoch.singleton import Singleton


class ConfigTest(unittest.TestCase):

    def setUp(self):
        """
        Tear down test
        """
        # hack to clean up singleton DT
        Singleton._instances.clear()
        config.__config_locked__ = False
        


    def test_load_from_file(self):
    
        cfg = Config('config.yaml')
        
        assert_in(GRID, cfg.keys())
        
        # it is locked by default when created from a file
        with assert_raises(AttributeError) as ae:
            cfg.foo = 5
                
        with assert_raises(AttributeError) as ae:
            del cfg[GRID]
            
        with assert_raises(AttributeError) as ae:
            delattr(cfg,GRID)
            
        with assert_raises(AttributeError) as ae:
            cfg[GRID] = 9
            
        assert_in(GRID, cfg.keys())
        
        assert_is_instance(cfg[GRID], DotDict)

        
    def test_create_config(self):
                
        cfg = Config()
        
        cfg.foo.bar.baz= 5
        assert_equal(cfg.foo.bar.baz, 5)
        
        cfg.foo.bar.bah = []
        cfg.foo.bar.bah.append(5)
        cfg.foo.bar.bah.append(5)
        cfg.foo.bar.bah.append({'a3':9})
        assert_equal(cfg.foo.bar.bah, [5,5,{'a3':9}])
        assert_equal(cfg.foo.bar.baz, 5)
        assert_equal(cfg.foo.bar.bah[2].a3, 9)
        
        # add check for valid attribute names?
        cfg.bad = {'foo bar':5}
        
        with assert_raises(AttributeError) as ae:
            cfg.foo.bar.buz = [5,5,{'a3',9}]

            # can't get a set in a config object only list and dict
            cfg.foo.bar.buz[2]
        
        #cfg['booo']['fooo'] = 8
        
        
        
    def test_lock(self):
    
        cfg = Config()
        
        cfg.foo.bar.baz= 5
        cfg.foo.bar.bah = [5,5,{'a3':9}]
        
        cfg._lock()
    
        with assert_raises(AttributeError) as ae:
            cfg.foo.bar.baz= 5
        
        with assert_raises(AttributeError) as ae:
            cfg.foo.bar.buzz = [4,]

        with assert_raises(AttributeError) as ae:
            cfg.foo.bar.bah.append(5)   
        
        with assert_raises(AttributeError) as ae:
            cfg.popitem()
            
        with assert_raises(AttributeError) as ae:
            cfg.clear()
    
    