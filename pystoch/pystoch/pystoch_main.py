#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file pystoch.py
@date 03/11/13
@description Main program to calculate probability grids for stochastic oil model results.

Max/Linux Command Line Examples (from the pystoch directory):
./pystoch_main.py -p ./trajectory_data/simap/3D_TEST1 -x 3D_TEST1_S -o result
./pystoch_main.py --path ./trajectory_data/oilmap/3D_TEST1 --prefix 3D_TEST1_s -o result
./pystoch_main.py --path ./trajectory_data/oilmap/2D_TEST1,./trajectory_data/oilmap/2D_TEST2 --prefix 2D_TEST1_s -o result
mpiexec -n 3 ./pystoch_main.py --path ./temp/kara_sea_aws_java/MODELOUT_4b -x Blowout1_1_H_s -o result

Windows Command Line Examples (from the pystoch directory):
C:\Python27\python.exe pystoch_main.py -p trajectory_data\simap\3D_TEST1 -x 3D_TEST1_S -o result
C:\Python27\python.exe pystoch_main.py -p temp\kara_sea_aws_java\MODELOUT_4b -x Blowout1_1_H_s -o result
C:\Python27\Lib\site-packages\mpi4py\bin\mpiexec.exe -n 3 C:\Python27\python.exe pystoch_main.py -p temp\kara_sea_aws_jav
a\MODELOUT_4b -x Blowout1_1_H_s -o result

++ Profiling:
python -m cProfile -o restats ./pystoch_main.py -p ./temp/kara_sea_aws_java/MODELOUT_4b/ -x Blowout1_1_H_s -o profile
>>> import pstats
>>> p = pstats.Stats('restats')
>>> p.strip_dirs().sort_stats(-1)
>>> p.sort_stats('time').print_stats(20)


Reading: http://www.dabeaz.com/coroutines/index.html

## Note - mpi stuff ends up here on windows: C:\Python27\lib\site-packages\mpi4py\bin

'''
import os
import numpy
import logging
from pystoch import log
logger = logging.getLogger('pystoch.pystoch')

from pystoch.workflow import WorkFlow
from pystoch.output.netcdf_out import netcdf_out
from pystoch.datatypes import DT
from pystoch.command_line_arguments import get_command_line_arguments
from pystoch.config import Config 
from pystoch.util import *
from pystoch.parallel import *


def main():
    logger.info('Starting main program')
    
    # Get system command line arguments 
    options = get_command_line_arguments()
    
    if options.cfgpath is not None:
        config = Config(options.cfgpath)
    else:
        for loc in os.curdir, \
                os.path.expanduser(os.path.join('~','.pystoch')), \
                os.environ.get("PYSTOCH_CONF_DIR",''):
            
            cfg_file = os.path.join(loc,'config.yaml')
            if os.path.exists(cfg_file):
                config = Config(cfg_file)
                break
    
    DT(ndims=2,precision=numpy.float32,location_units='LatLon')
    
    wf = WorkFlow()
    
    # Uses the Config file rather than passing arguments
    wf.select_grid_method() 
 

    wf.select_trajectory_files(options.path, options.prefix, None)

    # Uses the Config file rather than passing arguments
    wf.setup_products()
    logger.info('Pystoch setup complete - running now...')

    wf.run()

    logger.info('Pystoch run complete - writing output')

    if mpi_msr:
        for name, gd in wf._grid_data.iteritems():
            logger.info('Writing output for %s products' % name)

            netcdf_out(options.outfile + '_' + name + '.nc', options.prefix, wf.nsims, name, gd)
        
    logger.info('Pystoch run complete')

if __name__ == '__main__':
    main()
