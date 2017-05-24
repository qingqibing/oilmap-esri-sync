import numpy as np
import matplotlib
import matplotlib.pyplot as plt


from pystoch.readers.oilmdl_reader import OilModelDirectAccessReader
from pystoch.keywords import *

reader = OilModelDirectAccessReader('/Users/dstuebe/Documents/ASA Projects/13-092 Qatar Maersk/OilMdl_results/SCENARIO2_INST_SUMMER/SCENARIO2_INST_SUMMER_S/SCENARIO2_INST_SUMMER_s004')

matplotlib.rcParams['axes.unicode_minus'] = False
fig1 = plt.figure()
ax1 = fig1.add_subplot(111)


for output in reader.stream_record_blocks():
    
    
    block = output[OilModelDirectAccessReader.SURFACE_SPILLETS]
    
    etime = output[METADATA][TIME][ETIME]/3600.0
    
    data = (block['mass']/block['density'])/(np.pi*block['radius']**2) * 1000
    
    ax1.plot(etime.repeat(data.shape), data, '.')
    
    
    
ax1.set_title('Scneario 2 Sim 4')
plt.xlabel('time (hours)')
plt.ylabel('thickness (mmsc)')
plt.show()