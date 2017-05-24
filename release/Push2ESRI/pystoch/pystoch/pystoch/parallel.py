try:
    from mpi4py import MPI
    
    mpi_comm = MPI.COMM_WORLD
    mpi_size = mpi_comm.Get_size()
    mpi_rank = mpi_comm.Get_rank()
    mpi_par = mpi_size > 1
    mpi_msr = mpi_rank == 0
        
    if mpi_par:
        import sys
        sys_excepthook = sys.excepthook
        def mpi_excepthook(type, value, traceback): 
            print type, value
            sys_excepthook(type, value, traceback) 
            MPI.COMM_WORLD.Abort(1) 
        sys.excepthook = mpi_excepthook
        
        
except ImportError:
    
    MPI = None
    mpi_comm = None
    mpi_size = 1
    mpi_rank = 0
    mpi_par = False
    mpi_msr = True
    

__all__ = [ 'MPI',
            'mpi_comm',
            'mpi_size',
            'mpi_rank',
            'mpi_par',
            'mpi_msr',
            ]
    