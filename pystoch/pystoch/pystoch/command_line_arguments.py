#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file get_command_line_arguments.py
@date 04/24/13
@description Command line parser to get the path and prefix for the data to process
'''

import os
from optparse import OptionParser
from exceptions import PyStochIOError

def get_command_line_arguments():

    parser = OptionParser()
    parser.add_option("-c", "--cfg", dest="cfgpath", help="Set the location of the config file", type="string", default=None)
    parser.add_option("-p", "--path", dest="path", help="Set the path to the trajectory model output", type="string", default=None)
    parser.add_option("-o", "--output", dest="outfile", help="Set the name of the netcdf analysis result", type="string", default=None)
    parser.add_option("-x", "--prefix", dest="prefix", help="Specify the prefix for the trajectory simulation", type="string", default=None)

    (options, args) = parser.parse_args()

    if options.path is None:
        raise PyStochIOError("No path to trajectory data was specified.")


    if options.prefix is None:
        raise PyStochIOError('No prefix specified for the trajectory simulation to analyze.')
        
    if options.outfile is None:
        options.outfile = options.prefix
        
    return options