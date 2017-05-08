

import numpy as np
cimport numpy as np

ctypedef np.int32_t DTYPE_i32t
ctypedef np.float32_t DTYPE_f32t
ctypedef np.float64_t DTYPE_f64t
ctypedef np.int64_t DTYPE_i64t

def c_grid_max(np.ndarray[DTYPE_f32t, ndim=2] result, np.ndarray[DTYPE_i32t, ndim=2] ind_pos, np.ndarray[DTYPE_f32t, ndim=1] value):
    
    #print("Hello from c_grid_max!")

    #cdef int xmax = result.shape[0]
    #cdef int ymax = result.shape[1]
    cdef int npos = ind_pos.shape[0]
    #cdef int ndims = ind_pos.shape[1]

    cdef int idx
    for idx in xrange(npos):
        result[ind_pos[idx,0], ind_pos[idx,1]] = max(result[ind_pos[idx,0], ind_pos[idx,1]], value[idx])


    return npos