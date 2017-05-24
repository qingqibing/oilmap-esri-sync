class PyStochError(Exception): 
    """
    Base class for all PyStoch Exceptions
    """
    pass

class PyStochIOError(PyStochError):
    """
    PyStoch IO Error Exception Class
    """
    
class PyStochWorkflowError(PyStochError):
    """
    PyStoch IO Error Exception Class
    """
    
class PyStochOperatorError(PyStochError):
    """
    PyStoch IO Error Exception Class
    """
    
class PyStochGridDataError(PyStochError): 
    """
    PyStoch GridData Error Exception Class
    """
    pass
    
class PyStochParallelError(PyStochError): 
    """
    PyStoch Parallel Error Exception Class
    """
    pass
    