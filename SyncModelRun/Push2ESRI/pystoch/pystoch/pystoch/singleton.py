#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file singleton.py
@date 05/23/13
@description A singleton meta 
'''


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]