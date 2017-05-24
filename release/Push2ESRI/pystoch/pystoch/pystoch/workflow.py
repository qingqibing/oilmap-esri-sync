#!/usr/bin/env python
'''
@author David Stuebe <dstuebe@asasscience.com>
@file workflow_builder.py
@date 03/11/13
@description Core business logic to build the workflow for the specified inputs and desired products
'''

import os
import numpy
from collections import OrderedDict

import fiona
from shapely.geometry import Polygon

import logging
logger = logging.getLogger('pystoch.workflow')

# Import maps of readers, gridding functions and Products
from readers.readers import reader_map
from pystoch.gridding_functions.grid_functions import gridding_functions_map
from pystoch.gridding_functions.shape_functions import shape_functions_map
from products.products import subsurface_gridded_products_map, surface_gridded_products_map, shore_gridded_products_map
from products.products import subsurface_shape_products_map, surface_shape_products_map, shore_shape_products_map

from pystoch.config import Config 
from grid_data import GridData
from grids import Grid
from datatypes import DT
from exceptions import PyStochWorkflowError
from exceptions import PyStochParallelError
from util import *
from keywords import *
from parallel import *
from time import sleep

from pystoch.map_reduce_ops.clean_array import clean_array

        
class WorkFlow(object):


    def __init__(self):
        super(WorkFlow, self).__init__()
    
        self._gridder_map = {} # a dictionary of the gridder coroutines by product type
        self._reducer_map = {} # a dictionary of the reduction operators by product type
        self._cleaner_map = {} # a dictionary of cleaner/reset operations by product type
        
        self._file_readers          = None # a list or tuple one for each particle file
        self.trajectory_file_class  = None # the class for the reader

        self._grids                 = None # a dict
        self._grid_data             = None # a dict
        self._grid_function         = None # a function
        
        self._shapes                = None # dictionary of polygons for each product type
        self._shape_function        = None # a function
        self._shape_file            = None
        
        self._grid_type             = None
        self._grid_spacing          = None
        self._grid_dimensions       = None
        self._grid_file             = None

        self._global_file_names = []

    @property
    def nsims(self):
        return len(self._file_readers)
        
    @property
    def global_nsims(self):
        if mpi_par:
            if mpi_msr:
                return len(self._global_file_names)
            else:
                raise PyStochParallelError('You can not know about global stuff unless you are the master processor')
        else:
            return self.nsims
        
    @property
    def file_names(self):
        if mpi_par:
            host_name = MPI.Get_processor_name()
            return [":".join([host_name, x.fname]) for x in self._file_readers]
        else:
            return [x.fname for x in self._file_readers]
        
        
    @property
    def global_file_names(self):
        if mpi_par:
            if mpi_msr:
                return self._global_file_names
            else:
                raise PyStochParallelError('You can not know about global stuff unless you are the master processor')
        else:
            return self.file_names
        
    
        
        
    def select_trajectory_files(self, paths, prefix, constraints):
        """
        Create a reader for each file and read metadata. Filter subject to constraints
        This is the first step in setting up a workflow
        """
        if self._file_readers is not None: 
            raise PyStochWorkflowError('Trajectory Files already selected')
            
        reader_class = None
        
        path_list = paths.split(',')
        # split(',') can never be empty - will at least contain ['']
        files_by_path = {path:[] for path in path_list}
        
        for path in path_list:
                         
            if os.path.isdir(path):                    
                file_paths, r_class = self._read_path(path, prefix)
                files_by_path[path] = file_paths # a list of files in each path
                if reader_class is None: reader_class = r_class
                if reader_class != r_class:
                    raise PyStochWorkflowError('Returned different reader types from selected paths - Yikes!')
            
            else:
                if not mpi_par:
                    raise PyStochWorkflowError("""The specified path '%s' does not exist! """ % path)
        
        # Use utility method to partition the workload to the workers and determine which files are yours to read
        file_readers = self.partition_workload(files_by_path, reader_class, constraints)
        
        self._file_readers = file_readers

        self.trajectory_file_class = reader_class
        
    def _read_path(self, path, prefix):
    
        # do work on the file system to find the trajectory files
        directory_contents = os.listdir(path)
        if len(directory_contents) == 0:
            raise PyStochWorkflowError("The path '%s' contains no files!" % path)
        
        # Return a list of all the files in the directory in lower case
        files = [fname for fname in directory_contents if fname.lower().startswith(prefix.lower())]
        if len(files) == 0:
            raise PyStochWorkflowError("The path '%s' contains no file with the prefix %s!" % (path, prefix))
        
        # make a set of the extensions found
        extensions = {fname.rsplit(os.path.extsep,1)[-1].lower() for fname in files if os.path.extsep in fname}      
        # rsplit is funny here - why [-1]? (it works...)
        if len(extensions) == 0:
            raise PyStochWorkflowError("No file extensions found for path '%s' and prefix '%s'" % (path, prefix))
        
        # get the class for the reader
        reader = None
        reader_extensions = None
        for k,r in reader_map.iteritems():
        
            if k.issubset(extensions):
                reader = r
                reader_extensions = k
                
        
        if reader is None:
            raise PyStochWorkflowError('Failed to find a reader for files with extions: \n%s' % extensions)
        
        # make a set of the files that we need to read and strip off the extensions
        files_to_read = {os.path.splitext(fname)[0] for fname in files if fname.lower().endswith(tuple(reader_extensions))}      

        paths_no_extension = [os.path.join(path,fname) for fname in files_to_read]
        
        # Make sure all the files really exist:
        for fname in paths_no_extension:
            for ext in reader_extensions:
                full_name = fname + os.path.extsep + ext
                if not os.path.isfile(full_name):
                    raise PyStochWorkflowError("The file '%s' appears to be missing!" % full_name)
                
        
        return paths_no_extension, reader
        
    def partition_workload(self, files_by_path, reader_class, constraints):
        """
        Give a dictionary of files and a dictionary of workers sort out who does what!
        """
    
        if not mpi_par:
            flist = []
            for files in files_by_path.itervalues():
                flist += files
            file_readers = [reader_class(fname) for fname in flist]
        
            return file_readers

        #### Decide what to do if it is parallel!

        host_name = MPI.Get_processor_name()

        gathered_hosts = mpi_comm.gather(host_name,root=0)
        gathered_files_by_path = mpi_comm.gather(files_by_path, root=0)
        files_by_worker = None
    
        if mpi_msr:
            # look at what files each worker has and decide which they should open
        
            hosts = list(set(gathered_hosts))

            # Determine whether we are running on a single machine
            single_host = len(hosts) == 1
        
            # make a look up for the workers on each host
            workers_by_host = {host:[] for host in hosts}            
            paths_by_host = {host:set() for host in hosts}
            files_by_host = {host:set() for host in hosts}
            
            path_set = set(files_by_path.keys())
            
            for worker_number, host in enumerate((gathered_hosts)):
                if worker_number == 0:
                    continue # skip the master!
                
                workers_by_host[host].append(worker_number)
                local_files_by_path = gathered_files_by_path[worker_number]
                for path, files in local_files_by_path.iteritems():
                    if len(files) > 0:
                        paths_by_host[host].add(path)
                        files_by_host[host].update(files)
                        
                        path_set.discard(path)
                        
            if len(path_set) >0:
                raise PyStochParallelError('Unused path(s) specified in input: "%s"' % path_set)
                        
            for host, path_set in paths_by_host.iteritems():
                if len(path_set) == 0:
                    raise PyStochParallelError('The host "%s" has no valid input file paths!' % host)
            
            logger.info('workers_by_host: \n%s' % pretty_print(workers_by_host))
            logger.info('paths_by_host: \n%s' % pretty_print(paths_by_host))
            logger.info('files_by_host: \n%s' % pretty_print(files_by_host))
        
            
            for host, fnames in files_by_host.iteritems():
                self._global_file_names += [":".join([host, fname]) for fname in fnames]
            
        
            files_by_worker = [[] for i in range(mpi_size)]
            for host in hosts:
                workers = list(workers_by_host[host])
                files = sorted(list(files_by_host[host]))
            
                nfiles = len(files)
                nworkers = len(workers)
                remainder = nfiles%nworkers
                for worker in workers:
                    if remainder > 0:
                        odd_man = 1
                        remainder -= 1
                    else: 
                        odd_man = 0
                    
                    nfiles_for_worker = nfiles/nworkers + odd_man

                    files_by_worker[worker] = [files.pop() for i in range(nfiles_for_worker)]
            
        
        my_files = mpi_comm.scatter(files_by_worker, root=0)
        file_readers = [reader_class(fname) for fname in my_files]
        
        logger.info('Worker # %s got %s files' % (mpi_rank, len(my_files)))
        
        return file_readers
    
        
        
        
    def select_grid_method(self):
        """
        Select the grid method and type. Specify the grid spacing and grid dimension as needed.

        Dangerous to use fixed grid with real data - may create a very large grid!
        wf.select_grid_method(Grid.FIXED,'bin gridding',grid_spacing=(.001,.001,300))
        """
        config = Config()
        
        grid_config = config[GRID]
        
        
        grid_dimensions = grid_config.get(DIMENSIONS)
        grid_spacing    = grid_config.get(SPACING)
        grid_file       = grid_config.get(FILE)
        
        method_name = grid_config.get(METHOD)
        self._grid_function = gridding_functions_map.get(method_name)
        
        if self._grid_function is None:
            # Allow for only doing polygon processing
            return
        
        self._grid_spacing      = grid_spacing
        self._grid_dimensions   = grid_dimensions
        self._grid_file         = grid_file



        if grid_dimensions is not None:
            self._grid_type = Grid.FLOATING
            if grid_spacing is not None or grid_file is not None:
                raise PyStochWorkflowError("Invalid grid configuration: %s. Specify one of %s, %s or %s." % (grid_config, DIMENSIONS, FILE, SPACING))
            
            #nd = len(grid_dimensions)
            #if nd != DT.NDIMS:
            #    raise PyStochWorkflowError("Invalid grid configuration: %s. 'dimensions' must be length %s" % (grid_config, DT.NDIMS))
            
            for val in grid_dimensions:
                if not isinstance(val,int):
                    raise PyStochWorkflowError("Invalid grid configuration: %s. %s must be integers!" % (grid_config, DIMENSIONS))
            
        if grid_spacing is not None:
            self._grid_type = Grid.FIXED
            
            if grid_dimensions is not None or grid_file is not None:
                raise PyStochWorkflowError("Invalid grid configuration: %s. Specify one of %s, %s or %s." % (grid_config, DIMENSIONS, FILE, SPACING))
            
            #nd = len(grid_spacing)
            #if nd != DT.NDIMS:
            #    raise PyStochWorkflowError("Invalid grid configuration: %s. 'spacing' must be length %s" % (grid_config, DT.NDIMS))
            
            for val in grid_spacing:
                if not isinstance(val,float):
                    raise PyStochWorkflowError("Invalid grid configuration: %s. %s must be floats!" % (grid_config, SPACING))
            
            
        if grid_file is not None:
            self._grid_type = Grid.FILE
            # can't have also selected either of the other two...
            
            if not os.path.isfile(grid_file):
                raise PyStochWorkflowError("Invalid grid configuration: %s. The file '%s' does not exist!" % (grid_config, grid_file))            
            
        if self._grid_type is None:
            raise PyStochWorkflowError("Invalid grid configuration: %s. Specify one of %s, %s or %s." % (grid_config, DIMENSIONS, FILE, SPACING))
               
        
    def select_shape_function(self, shape_config):
        
        fname = shape_config.get(METHOD)
        self._shape_function =shape_functions_map.get(fname)
        
        self._shape_file = shape_config.get(File)
        
        
    def setup_products(self):
        """
        Select the data products that should be produced by the workflow and validate that
        the trajectory files have the correct spillet types to do the calculation
        
        """
        
        config = Config()

        logger.info('Setting up Products')
        
        # Surface
        surface = config.get(SURFACE,{})
        logger.info('Surface:\n%s' % surface)
        
        p = surface.get(GRIDDED_PRODUCTS,{})
        logger.info('Surface Gridded Products:\n%s' % p)
        surface_gridded_products = p.keys()
        
        p = surface.get(SHAPE_PRODUCTS,{})
        logger.info('Surface Shape Products:\n%s' % p)
        surface_shape_products = p.keys()
        
        # Subsurface
        subsurface = config.get(SUBSURFACE,{})
        
        p = subsurface.get(GRIDDED_PRODUCTS,{})
        logger.info('Suburface Gridded Products:\n%s' % p)
        subsurface_gridded_products = p.keys()
        
        p = subsurface.get(SHAPE_PRODUCTS,{})
        logger.info('Suburface Shape Products:\n%s' % p)
        subsurface_shape_products = p.keys()
        
        # Shore
        shore = config.get(SHORE,{})
        
        p = shore.get(GRIDDED_PRODUCTS,{})
        logger.info('Shore Gridded Products:\n%s' % p)
        shore_gridded_products = p.keys()
        
        p = shore.get(SHAPE_PRODUCTS,{})
        logger.info('Shore Shape Products:\n%s' % p)
        shore_shape_products = p.keys()

        
        
        if self._grid_function is None and self._shape_function is None:
            raise PyStochWorkflowError('Must select a grid or shape method before calling setup_products')
        
        if self._file_readers is None:
            raise PyStochWorkflowError('Must select_trajectory_files before calling setup_products')
        
        
        if self._grids is not None or self._grid_data is not None or self._shapes is not None:
            raise PyStochWorkflowError('Can not call setup_products more than once!')
        self._shapes = {}
        self._grids = {}
        self._grid_data = {}

        if self._grid_function is not None:
            extents = self._get_extents_from_readers()
    
        if self._shape_function is not None:
            self._get_shapes()
        
        product_metadata= {}
        product_metadata[PRODUCT_TYPE] = None
        if mpi_msr:
            product_metadata[NSIMS] = self.global_nsims
            product_metadata[FILE_NAMES] = self.global_file_names
        else:
            product_metadata[NSIMS] = self.nsims
            product_metadata[FILE_NAMES] = self.file_names
        
        
        product_set = False
        if surface_gridded_products is not None and len(surface_gridded_products) >0:
            if not isinstance(surface_gridded_products,(tuple,list,set)):
                raise PyStochWorkflowError('Surface Gridded Products argument must be a list: recieved "%s"' % surface_gridded_products)
            
            # create the surface grid and grid data
            grid = self._create_grid(2, extents)   
            self._grids[SURFACE] = grid
            grid_data = GridData(grid,defaults={})
            self._grid_data[SURFACE] = grid_data
                    
            self._create_filename_variable(grid_data)
                    
            ops_list = [] # a list of coroutine operators which are used by grid mapper function. Arguments are: block, index_position and weight.
            reduce_list = [] # elements are tuples. The first object is a coroutine, the remaining objects are its arguments.
            cleaner_list = [] # a list of coroutine operators which are used by products to clean up after each run is processed
            
            product_metadata[PRODUCT_TYPE] = SURFACE        
            
            # Process actual products and setup workflow!
            for product_name in surface_gridded_products:
                try:
                    product_adder =  surface_gridded_products_map[product_name]
                except KeyError as ke:
                    raise PyStochWorkflowError("Invalid surface gridded product name selected: '%s', please choose from: %s" % (product_name, surface_gridded_products_map.keys()))
                
                try:
                    product_adder(ops_list, reduce_list, cleaner_list, grid_data, product_metadata)
                except TypeError as te:
                    logger.error('Exception raised by Surface product_adder for product named: %s' % product_name)
                    raise
                    
            # initialize the gridding coroutine with the grid to use and the operations to perform
            self._gridder_map[SURFACE] = self._grid_function(grid,ops_list) # the grid function distributes the data to each mapper operation
            self._reducer_map[SURFACE] = reduce_list
            self._cleaner_map[SURFACE] = cleaner_list
            
            product_set = True
        
        if subsurface_gridded_products is not None and len(subsurface_gridded_products) > 0: 
            if not isinstance(subsurface_gridded_products,(tuple,list,set)):
                raise PyStochWorkflowError('Subsurface Gridded Products argument must be a list: recieved "%s"' % subsurface_gridded_products)
            
            # create the subsurface grid and grid data
            grid = self._create_grid(2, extents)
            self._grids[SUBSURFACE] = grid
            grid_data = GridData(grid,defaults={})
            self._grid_data[SUBSURFACE] = grid_data
                
            self._create_filename_variable(grid_data)

            ops_list = [] # a list of coroutine operators which are used by grid mapper function. Arguments are: block, index_position and weight.
            reduce_list = [] # elements are tuples. The first object is a coroutine, the remaining objects are its arguments.
            cleaner_list = [] # a list of coroutine operators which are used by products to clean up after each run is processed
   
            product_metadata[PRODUCT_TYPE] = SUBSURFACE        

                    
            # Process actual products and setup workflow!
            for product_name in subsurface_gridded_products:
                try:
                    product_adder =  subsurface_gridded_products_map[product_name]
                except KeyError as ke:
                    raise PyStochWorkflowError("Invalid subsurface product name selected: '%s', please choose from: %s" % (product_name, subsurface_gridded_products_map.keys()))
                try:
                    product_adder(ops_list, reduce_list, cleaner_list, grid_data, product_metadata)
                except TypeError as te:
                    logger.error('Exception raised by SubSurface product_adder for product named: %s' % product_name)
                    raise

            # initialize the gridding coroutine with the grid to use and the operations to perform
            self._gridder_map[SUBSURFACE] = self._grid_function(grid,ops_list)
            self._reducer_map[SUBSURFACE] = reduce_list
            self._cleaner_map[SUBSURFACE] = cleaner_list

            product_set = True
    
        if shore_gridded_products is not None and len(shore_gridded_products) > 0: 
            if not isinstance(shore_gridded_products,(tuple,list,set)):
                raise PyStochWorkflowError('Shore Gridded Products argument must be a list: recieved "%s"' % shore_gridded_products)
            
            # create the subsurface grid and grid data
            grid = self._create_grid(2, extents)
            self._grids[SHORE] = grid
            grid_data = GridData(grid,defaults={})
            self._grid_data[SHORE] = grid_data
                
            self._create_filename_variable(grid_data)

                
            ops_list = [] # a list of coroutine operators which are used by grid mapper function. Arguments are: block, index_position and weight.
            reduce_list = [] # elements are tuples. The first object is a coroutine, the remaining objects are its arguments.
            cleaner_list = [] # a list of coroutine operators which are used by products to clean up after each run is processed

            product_metadata[PRODUCT_TYPE] = SHORE        

        
            # Process actual products and setup workflow!
            for product_name in shore_gridded_products:
                try:
                    product_adder =  shore_gridded_products_map[product_name]
                except KeyError as ke:
                    raise PyStochWorkflowError("Invalid shore product name selected: '%s', please choose from: %s" % (product_name, shore_gridded_products_map.keys()))
                try:
                    product_adder(ops_list, reduce_list, cleaner_list, grid_data, product_metadata)
                except TypeError as te:
                    logger.error('Exception raised by Shore product_adder for product named: %s' % product_name)
                    raise

            # initialize the gridding coroutine with the grid to use and the operations to perform
            self._gridder_map[SHORE] = self._grid_function(grid,ops_list)
            self._reducer_map[SHORE] = reduce_list
            self._cleaner_map[SHORE] = cleaner_list

            product_set = True


        if not product_set:
            raise PyStochWorkflowError('Must set at least one product!')
            
            
        # Only happens for parallel workers
        if not mpi_msr:
        
            # Replace the reduce coroutine with an mpi_send coroutine!
            @coroutine        
            def mpi_send(to=0):
                while True:  
                    data = (yield)
                    slist = []
                    nplist = []
                    for item in data[1:]:
                        if not isinstance(item, numpy.ndarray):
                            slist.append(item)
                        else:
                            slist.append('NUMPY')
                            nplist.append(item)
                    
                    mpi_comm.send(slist, dest=to, tag=data[0])
        
                    for array in nplist:
                        mpi_comm.Send(array, dest=to, tag=1000)
        
            co = mpi_send()
        
            for product_type in self._reducer_map.iterkeys():
                          
                
                reduction_list = self._reducer_map[product_type]
                            
                new_list = []
                for cnt, reduction in enumerate(reduction_list):
                    # a reduction is a tuple. The first element is a coroutine, the rest are its arguments
                    reduction_coroutine = reduction[0]

                    new_list.append( (co, cnt, product_type) + reduction[1:] )

                self._reducer_map[product_type] = new_list


    def run(self):
        logger.info('Starting workflow run')

        if mpi_par:
            if mpi_msr:
                self._controller_run()
            else:
                self._worker_run()  

        else:
             self._worker_run()  
        
        self._worker_finalize()

        
    def _controller_run(self):
        
        total_reduce_ops = self.global_nsims * sum([len(rlist) for rlist in self._reducer_map.itervalues()])
        
        cnt = 0
        while cnt < total_reduce_ops:
            
            
            # note - copy paste error in interface keyword should be source not dest!
            request = mpi_comm.irecv(dest=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            
            while True:
                status = MPI.Status()
                test,rlist = request.test(status)
                if test:
                    break
                sleep(0.1)                    
            
            logger.info('Received message from worker# %s, tag# %s, cnt = %s' % (status.source, status.tag, cnt))
            
            product_type = rlist[0]
            
            reduction_list = self._reducer_map[product_type]
            msr_tuple =  reduction_list[status.tag]           
            co = msr_tuple[0]
            
            for ind, item in enumerate(msr_tuple):
                if isinstance(item, numpy.ndarray):
                    mpi_comm.Recv(item, status.source, tag=1000)
                    rlist[ind] = item
            
            
            co.send(rlist[1:])
        
            cnt +=1
        
        
    def _worker_run(self):
        product_keys = self._gridder_map.keys()
        
        product_reader_map = self.trajectory_file_class.get_output_map(product_keys)
        # product_read_map: Keys are product keys (Surface, Subsurface, Shoreline),
        #                   Values are a list of spillet output types
    
        required_spillet_types = set()
        for required_types in product_reader_map.values():
             required_spillet_types.update(required_types)
        
        reduction_metadata = {}
        reduction_metadata[NSIMS] = self.nsims
        
        co_clean = clean_array()
        
        for fnum, (file_reader, file_name) in enumerate(zip(self._file_readers, self.file_names)):
        
            reduction_metadata[FILE_NAME] = file_name
        
            logger.info('Procesing file number %s of %s' % (fnum +1, self.nsims))
            logger.debug("File name: '%s'" % file_reader.fname)
            # read only the spillet types which are needed for the selected products
            for particle_block in file_reader.stream_record_blocks(output_definition=required_spillet_types):
                
                #Particle_block is a dictionary: Key - spillet type, Value - array or particles
                
                metadata = particle_block[METADATA]
                
                for product_key in product_keys:
                    # for each product pass certain spillet types to the correct grid map coroutine
                    
                    for spillet_key in product_reader_map[product_key]:                    
                        self._gridder_map[product_key].send((particle_block[spillet_key], metadata))
                    
        
            # at the end of each file, apply the reduction process:
            for product_type, reduction_list in self._reducer_map.iteritems():
                            
                for reduction in reduction_list:
                    # a reduction is a tuple. The first element is a coroutine, the rest are its arguments
                    reduction_coroutine = reduction[0]
                    reduction_args = reduction[1:] + (reduction_metadata,)
                    reduction_coroutine.send(reduction_args)


            for product_type, cleaner_list in self._cleaner_map.iteritems():
                        
                for args in cleaner_list:
                    co_clean.send(args)
            


    def _worker_finalize(self):

        for product_type, reduction_list in self._reducer_map.iteritems():
            for reduction in reduction_list:
                reduction[0].close() 
            
        
        
    def _create_grid(self, grid_dimension, spatial_extents):
        """
        create the grid objects and grid data that are required to execute the workflow
        """
        
        if grid_dimension is not 2 and grid_dimension is not 3:
            raise PyStochWorkflowError("Grid dimension must be 2 or 3: Recieved '%s'" % grid_dimension) 

        if self._grid_type is Grid.FIXED:
            grid = Grid.create_fixed(extents=spatial_extents, grid_spacing=self._grid_spacing[:grid_dimension])
        elif self._grid_type is Grid.FLOATING:
            grid = Grid.create_floating(extents=spatial_extents, grid_dimensions=self._grid_dimensions[:grid_dimension])
        elif self._grid_type is Grid.FILE:
            grid = Grid.create_from_file(self._grid_file)
            
        return grid
            
    def _create_filename_variable(self, grid_data):
        
        if mpi_msr:
            name_array = grid_data.make_filename_data(FILE_NAMES, self.global_file_names)
        else:
            name_array = grid_data.make_filename_data(FILE_NAMES, self.file_names)

        
    def _get_extents_from_readers(self):
            
        # must get the surface extents
        extents = DT.extents(ndims=2,prec=DT.DPRECISION)
        default_extents = extents.copy()
        logger.info('Getting extents')

        
        
        if mpi_par:
            if not mpi_msr:
                for reader in self._file_readers:                
                    union_extents(extents,reader.get_extents(2), out=extents)
        
            gathered_extents = mpi_comm.gather(extents, root=0)
            
            if mpi_msr:
                for ext in gathered_extents:
                    union_extents(extents,ext, out=extents)

            extents = mpi_comm.bcast(extents, root=0)
            
        else:
            for reader in self._file_readers:                
                union_extents(extents,reader.get_extents(2), out=extents)
            

        if extents == default_extents:
            raise PyStochWorkflowError('The selected files appear to have no valid data')
        
        logger.info("Extents: %s" % extents)
        
        return extents
    
    
    def _get_shapes(self):
    
        shapes = OrderedDict()
        with fiona.open(self._shape_file, 'r') as f:
            
            for geobj in f:
     
                shape = None
                geo = geobj['geometry']
                if geo['type'] is 'Polygon':
                    shape = Polygon(*geo['coordinates'])

                shape.properties = geobj['properties']
                 
                shapes[geobj['id']] = shape
                 
        self._shapes[SURFACE] = shapes
        self._shapes[SHORE] = shapes
        self._shapes[SUBSURFACE] = shapes
                
                


