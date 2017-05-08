#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file readers.py
@date 03/11/13
@description A module which imports and provides a mapping to all known readers
'''

from collections import OrderedDict

import oilmdl_reader
import splmdl_reader

# use an ordered dict to express precedence
reader_map = OrderedDict()
reader_map[oilmdl_reader.reader_key] = oilmdl_reader.OilModelDirectAccessReader
reader_map[splmdl_reader.reader_key] = splmdl_reader.SplModelDirectAccessReader
        
        
        
