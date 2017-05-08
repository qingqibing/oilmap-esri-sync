


#Pystoch
Pystoch is a stochastic oil spill analysis tool written in python. It is highly optimized and designed to be extensible with additional analysis products and methods. 

Products are defined at the user level. These are the analysis products that the user is interested in such as oil thickness, or minimum time to oil. The program is configured to produce various products for Surface, Subsurface and Shoreline oils. Each product is created by adding the analysis methods to the workflow. These are processed in a chain of operations applied to the spillets read from the trajectory file.



##Installation

###Required libraries:
* HDF5
* NetCDF4
    
###Required python packages:
* Numpy (install manually: pip install numpy)
* Cython
* Numexpr
* Nose
* NetCDF4
    
    
##Usage: 
###help:
    ./pystoch_main.py -h 
###Run:
    ./pystoch_main.py -p ./trajectory_data/simap/3D_TEST1 -x 3D_TEST1_S
    ./pystoch_main.py --path ./trajectory_data/oilmap/3D_TEST1 --prefix 3D_TEST1_s