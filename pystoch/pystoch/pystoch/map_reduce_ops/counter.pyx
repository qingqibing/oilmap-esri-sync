

import numpy as np
cimport numpy as np

ctypedef np.int32_t DTYPE_i32t
ctypedef np.int64_t DTYPE_i64t

#def c_counter(np.ndarray result, np.ndarray ind_pos):
def c_counter(np.ndarray[DTYPE_i32t, ndim=2] result, np.ndarray[DTYPE_i32t, ndim=2] ind_pos):
    
    #print("Hello from c_counter!")

    #cdef int xmax = result.shape[0]
    #cdef int ymax = result.shape[1]
    cdef int npos = ind_pos.shape[0]
    #cdef int ndims = ind_pos.shape[1]

    cdef int idx
    for idx in xrange(npos):
        result[ind_pos[idx,0], ind_pos[idx,1]] +=1


    return npos