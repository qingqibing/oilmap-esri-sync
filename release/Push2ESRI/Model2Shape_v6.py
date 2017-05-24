'''
Created on Apr 27, 2017

@author: JFontenault
'''

import datetime
startTime = datetime.datetime.now()

import arcview
import arcpy
import sys, os, struct#, numpy

#sys.path.append(r"C:\Library\Python\pystoch")
from pystoch.readers.oilmdl_om_reader import OilModelDirectAccessOMReader as OMDAR

print "Elapsed time after import="+str(datetime.datetime.now() - startTime)

sr = arcpy.SpatialReference("WGS 1984")
    

def CalculateDateTime(iInitSeconds, iElapsedSec):
    dtBase = datetime.datetime(1979,12,31,00,00,00)
    d = datetime.timedelta(seconds=iInitSeconds + iElapsedSec)

    dtTimeStep = dtBase + d
    return dtTimeStep
   

def CreateFCs_v3(sFGDB,sScenarioName,modType):
    import shutil
    
    template = os.path.join(sys.path[0],"template.gdb")
    if os.path.exists(sFGDB):
        try:
            shutil.rmtree(sFGDB)
        except:
            print "ERROR - Unable to replace geodatabase."
            sys.exit()
    
    shutil.copytree(template, sFGDB)
    return os.path.join(sFGDB,"spillets"), os.path.join(sFGDB,"trackline"), os.path.join(sFGDB,"thickness")


def Get_OMC_StartPos(sOMC_Path, ntcsteps):
    ts_start_pos = []
    
    f = open(sOMC_Path,"rb")
    ii = 1
    while ii  <= ntcsteps:
        cpos = int(f.tell())
        ts_start_pos.append(cpos)
        
        if ii == 1:
            nVersion = struct.unpack('h', f.read(2))[0]
            nrecs = 0
            ncrecs4 = nrecs
        else:
            if nVersion == 0:
                nrecs = struct.unpack('h', f.read(2))[0]
                ncrecs4 = nrecs
            else:
                ncrecs4 = struct.unpack('l', f.read(4))[0]
        
        stepsize = (4 * 8) + (ncrecs4 * 8)
        fpos = cpos + stepsize
    
        f.seek(fpos)
    
        ii += 1
    
    f.close()
    
    return ts_start_pos
    
    
def ReadOilmap2D(sGeoLocPath, sScenarioName, sFGDB, modType):
    
    splt, trk, thk = CreateFCs_v3(sFGDB,sScenarioName,modType)
    print "Elapsed time after creating geodatabase = "+str(datetime.datetime.now() - startTime)
    
    #pystoch code to read oilmap 2d output files.
    reader = OMDAR(sGeoLocPath + os.path.sep + "OUTDATA" + os.path.sep + sScenarioName)
        
    with arcpy.da.Editor(sFGDB) as edit:
        splt_cur = arcpy.da.InsertCursor(splt,['SHAPE@','DATETIME','MASS','RADIUS','THICKNESS','STATUS'])        
        trk_cur = arcpy.da.InsertCursor(trk,['SHAPE@'])
        thk_cur = arcpy.da.InsertCursor(thk,['SHAPE@','DATETIME','THICKNESS_MM'])
        
        Array = arcpy.Array()    
        TimeSteps = []
        
        t = 0    
        for block in reader.stream_record_blocks():
            #Get spillet date time.
            if t == 0:
                iInitSeconds = int(block['metadata']['time']['delta_time']) - int(block['metadata']['time']['elapsed_time'])
                iElapsedSec = 0
            else:
                iElapsedSec = int(block['metadata']['time']['elapsed_time']) - int(block['metadata']['time']['delta_time'])
                
            dtTimeStep = CalculateDateTime(int(iInitSeconds), int(iElapsedSec))
            TimeSteps.append(dtTimeStep)
         
            lons = [] #list for each time step to avg for track points
            lats = []
            
            for spillet in block['oil spillets'][1:]:
                lon = float(spillet[0][0])
                lons.append(lon)
                lat = float(spillet[0][1])
                lats.append(lat)
                status = int(spillet[2])
                mass = float(spillet[3])
                radius = float(spillet[4])
                thickness = float(spillet[5])
                #visc = float(spillet[6])
                #watercont = float(spillet[7])
    
                pnt = arcpy.Point()
                pnt.X = lon
                pnt.Y = lat
                #pnt.Z = 
                splt_cur.insertRow([pnt,dtTimeStep,mass,radius,thickness,status])
                           
            
            lon_avg = sum(lons)/float(len(lons))
            lat_avg = sum(lats)/float(len(lats))
            
            pnt = arcpy.Point(lon_avg, lat_avg)                        
            Array.add(pnt)        
        
            t+=1
        
        trackline = arcpy.Polyline(Array)
        trk_cur.insertRow([trackline])
        Array.removeAll()
        print "Elapsed time after creating spillets and track = "+str(datetime.datetime.now() - startTime)

        #get the starting byte position in the OMC for each time step
        sOMC_Path = sGeoLocPath + os.path.sep + "OUTDATA" + os.path.sep + sScenarioName + ".OMC"
        ts_start_pos = Get_OMC_StartPos(sOMC_Path, len(reader._record_data))
           
    
        with open(sOMC_Path,"rb") as f:
            nVersion = struct.unpack('h', f.read(2))[0]
                    
            for iRec in range(0,len(reader._record_data)):            
                
                fpos = ts_start_pos[iRec]
                f.seek(fpos)
        
                if nVersion == 0:
                    ncrecs4 = struct.unpack('h', f.read(2))[0]
                    ncvals = struct.unpack('h', f.read(2))[0]
                else:
                    ncrecs4 = struct.unpack('l', f.read(4))[0]
        
                imaxoil = struct.unpack('h', f.read(2))[0]
                jmaxoil = struct.unpack('h', f.read(2))[0]
                olonoil = struct.unpack('f', f.read(4))[0]
                olatoil = struct.unpack('f', f.read(4))[0]
                dlonoil = struct.unpack('f', f.read(4))[0]
                dlatoil = struct.unpack('f', f.read(4))[0]
                sTime = struct.unpack('l', f.read(4))[0]
                rval = struct.unpack('f', f.read(4))[0]
        
                grid_cell_data = []
                for n in range(0,ncrecs4 -1):
                    i = struct.unpack('h', f.read(2))[0]
                    j = struct.unpack('h', f.read(2))[0]
                    thickness = struct.unpack('f', f.read(4))[0]
        
                    grid_cell_data.append([i,j,thickness])
                    
                for n in range(0,ncrecs4 -1):
                    i = grid_cell_data[n][0]
                    j = grid_cell_data[n][1]
                    
                    lon1 = olonoil + ((i - 1) * dlonoil)
                    lat1 = olatoil + ((j - 1) * dlatoil)
                    lon2 = olonoil + ((i) * dlonoil)
                    lat2 = olatoil + ((j) * dlatoil)
                                        
                    coordList = [[lon1,lat1],[lon1,lat2],[lon2,lat2],[lon2,lat1],[lon1,lat1]]        
        
                    arrayPoly = arcpy.Array()        
                    #pntObj = arcpy.Point()
                    
                    for coordPair in coordList:
                        arrayPoly.add(arcpy.Point(coordPair[0],coordPair[1]))                    
                    cell = arcpy.Polygon(arrayPoly,sr)                    
                    
                    thk_cur.insertRow([cell,TimeSteps[iRec],thickness])                    
    
        del splt_cur
        del trk_cur
        del thk_cur
        
        print "Elapsed time after creating thickness grid = "+str(datetime.datetime.now() - startTime)


def Run(sScenarioFile, sOutputPath, modType):
    sGeoLocPath = os.path.split(os.path.split(sScenarioFile)[0])[0]
    sScenarioName = os.path.splitext(os.path.split(sScenarioFile)[1])[0]   
    
    sFGDB = os.path.join(sOutputPath,sScenarioName+".gdb")

    ReadOilmap2D(sGeoLocPath, sScenarioName, sFGDB, modType)
    
    print "Elapsed time after completion = "+str(datetime.datetime.now() - startTime)   
    print "Done!"
 
    
#####################################################    
#####################################################


if __name__ == "__main__":
    Run(sys.argv[1], sys.argv[2], "OM2d")

