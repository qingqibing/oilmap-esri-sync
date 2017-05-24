#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file run_job.py
@date 08/6/13
@description A wrapper method to launch the pystoch. A work around to deal with errors
running mpiexec in windows from java process builder.
'''


import subprocess
import sys
if __name__ == '__main__':

    args = sys.argv[1:]
    
    p = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
    
    p.wait()
    
    