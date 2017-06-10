'''
Created on Apr 27, 2017

@author: JFontenault
'''

try:
    import arcview
except:
    try:
        import arcinfo
    except:
        try:
            import arceditor
        except:
            pass        

import arcpy

import sys, os, struct, numpy
import datetime

from pystoch.readers.oilmdl_om_reader import OilModelDirectAccessOMReader as OMDAR
from pystoch.datatypes import DT

DT(ndims=2,precision=numpy.float32,location_units='LatLon')
sr = arcpy.SpatialReference(os.path.join(arcpy.GetInstallInfo()["InstallDir"],r"Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj"))

def ReadScenarioFile(sScenarioFile):
    sGeoLocPath = os.path.split(os.path.split(sScenarioFile)[0])[0]
    
    oScenFile = open(sScenarioFile,"r")
    scenLines = oScenFile.readlines()

    for i in range(0,len(scenLines)):
        key = scenLines[i].split("=")[0]

        if key == "Scenario":
            sScenarioName = scenLines[i].split("=")[1].strip()
       
    oScenFile.close()
    
    return sScenarioName, sGeoLocPath
    

def CalculateDateTime(iInitSeconds, iElapsedSec):
    dtBase = datetime.datetime(1979,12,31,00,00,00)
    d = datetime.timedelta(seconds=iInitSeconds + iElapsedSec)

    dtTimeStep = dtBase + d
    #sTimeStep = dtTimeStep.strftime("%Y-%m-%d %H:%M:%S")
    return dtTimeStep
   

def CreateFCs(sFGDB,sScenarioName,modType):

    if arcpy.Exists(sFGDB) == True:
        arcpy.Delete_management(sFGDB)    
    arcpy.CreateFileGDB_management(os.path.split(sFGDB)[0],sScenarioName)
    
    arcpy.CreateFeatureclass_management("in_memory","temp_spillet","POINT","","","",sr)
    temp_spillet = os.path.join("in_memory","temp_spillet")
    arcpy.AddField_management(temp_spillet, "DATETIME", "DATE")
    arcpy.AddField_management(temp_spillet, "MASS", "DOUBLE", 19, 5)
    arcpy.AddField_management(temp_spillet, "RADIUS", "DOUBLE", 19, 5)
    arcpy.AddField_management(temp_spillet, "THICKNESS", "DOUBLE", 19, 5)
    arcpy.AddField_management(temp_spillet, "VISCOSITY", "DOUBLE", 19, 5)
    arcpy.AddField_management(temp_spillet, "WATERCONTENT", "DOUBLE", 19, 5)
    arcpy.AddField_management(temp_spillet, "STATUS", "SHORT")
    
    arcpy.CreateFeatureclass_management("in_memory","temp_trkpt","POINT","","","",sr)
    temp_trkpt = os.path.join("in_memory","temp_trkpt")
    arcpy.AddField_management(temp_trkpt, "DATETIME", "DATE")
    
    arcpy.CreateFeatureclass_management("in_memory","temp_trkline","POLYLINE","","","",sr)
    temp_trkline = os.path.join("in_memory","temp_trkline")
    
    arcpy.CreateFeatureclass_management("in_memory","temp_grid","POLYGON","","","",sr)
    temp_grid = os.path.join("in_memory","temp_grid")
    arcpy.AddField_management(temp_grid, "DATETIME", "DATE")
    arcpy.AddField_management(temp_grid, "THICKNESS_MM", "DOUBLE", 19, 5)
    
    
    arcpy.CreateFeatureclass_management(sFGDB,sScenarioName,"POINT",temp_spillet,"","",sr)
    arcpy.CreateFeatureclass_management(sFGDB,sScenarioName + "_track","POINT",temp_trkpt,"","",sr)
    arcpy.CreateFeatureclass_management(sFGDB,sScenarioName + "_trackline","POLYLINE",temp_trkline,"","",sr)
    arcpy.CreateFeatureclass_management(sFGDB,sScenarioName + "_thickness","POLYGON",temp_grid,"","",sr)

    arcpy.Delete_management(temp_spillet)
    arcpy.Delete_management(temp_trkpt)
    arcpy.Delete_management(temp_trkline)
    arcpy.Delete_management(temp_grid)
    
    return os.path.join(sFGDB,sScenarioName), os.path.join(sFGDB,sScenarioName + "_track"), os.path.join(sFGDB,sScenarioName + "_trackline"), os.path.join(sFGDB,sScenarioName + "_thickness")


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
        
    #print "  Writing Spillets and Track..."
    sys.stdout.write("  Writing Spillets and Track: %d%%   \r" % (0) )
    sys.stdout.flush()
    
    #pystoch code to read oilmap 2d output files.
    reader = OMDAR(sGeoLocPath + os.path.sep + "OUTDATA" + os.path.sep + sScenarioName)
    
    splt, trkpt, trk, thk = CreateFCs(sFGDB,sScenarioName,modType)
        
    with arcpy.da.Editor(sFGDB) as edit:
        splt_cur = arcpy.da.InsertCursor(splt,['SHAPE@','DATETIME','MASS','RADIUS','THICKNESS','VISCOSITY','WATERCONTENT','STATUS'])
        trkpt_cur = arcpy.da.InsertCursor(trkpt,['SHAPE@','DATETIME'])
        trk_cur = arcpy.da.InsertCursor(trk,['SHAPE@'])
        thk_cur = arcpy.da.InsertCursor(thk,['SHAPE@','DATETIME','THICKNESS_MM'])
        
        Array = arcpy.Array()    
        TimeSteps = []
        
        t = 0    
        for block in reader.stream_record_blocks():
            sys.stdout.write("  Writing Spillets and Track: %d%%   \r" % (float(t)/float(len(reader._record_data))*100) )
            sys.stdout.flush()
    
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
                visc = float(spillet[6])
                watercont = float(spillet[7])
    
                pnt = arcpy.Point()
                pnt.X = lon
                pnt.Y = lat
                #pnt.Z = 
                splt_cur.insertRow([pnt,dtTimeStep,mass,radius,thickness,visc,watercont,status])
                           
            
            lon_avg = sum(lons)/float(len(lons))
            lat_avg = sum(lats)/float(len(lats))
            
            pnt = arcpy.Point(lon_avg, lat_avg)
            trkpt_cur.insertRow([pnt,dtTimeStep])
            
            Array.add(pnt)        
        
            t+=1
        
        trackline = arcpy.Polyline(Array)
        trk_cur.insertRow([trackline])
        Array.removeAll()
       
        
        sys.stdout.write("  Writing Spillets and Track: %d%%   \n" % (100) )
        sys.stdout.flush()
        
        
        ##Thickness grid based on OMC file
        #print "  Writing Thickness Grid..."
        sys.stdout.write("  Writing Thickness Grid: %d%%   \r" % (0) )
        sys.stdout.flush()
          
        #get the starting byte position in the OMC for each time step
        sOMC_Path = sGeoLocPath + os.path.sep + "OUTDATA" + os.path.sep + sScenarioName + ".OMC"
        ts_start_pos = Get_OMC_StartPos(sOMC_Path, len(reader._record_data))
           
    
        with open(sOMC_Path,"rb") as f:
            nVersion = struct.unpack('h', f.read(2))[0]
                    
            for iRec in range(0,len(reader._record_data)):            
                sys.stdout.write("  Writing Thickness Grid: %d%%   \r" % (float(iRec)/float(len(reader._record_data))*100) )
                sys.stdout.flush()
                
                fpos = ts_start_pos[iRec]
                f.seek(fpos)
        
                if nVersion == 0:
                    ncrecs4 = struct.unpack('h', f.read(2))[0]
                    ncvals = struct.unpack('h', f.read(2))[0]
                else:
                    ncrecs4 = struct.unpack('l', f.read(4))[0]
                #print ncrecs4
        
                imaxoil = struct.unpack('h', f.read(2))[0]
                jmaxoil = struct.unpack('h', f.read(2))[0]
                olonoil = struct.unpack('f', f.read(4))[0]
                olatoil = struct.unpack('f', f.read(4))[0]
                dlonoil = struct.unpack('f', f.read(4))[0]
                dlatoil = struct.unpack('f', f.read(4))[0]
                sTime = struct.unpack('l', f.read(4))[0]
                rval = struct.unpack('f', f.read(4))[0]
        
                flonoil = olonoil + (imaxoil * dlonoil)
                flatoil = olatoil + (jmaxoil * dlatoil)
        
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
                    pntObj = arcpy.Point()
                    
                    for coordPair in coordList:
                        arrayPoly.add(arcpy.Point(coordPair[0],coordPair[1]))                    
                    cell = arcpy.Polygon(arrayPoly,sr)                    
                    
                    thk_cur.insertRow([cell,TimeSteps[iRec],thickness])                    
    
        del splt_cur
        del trkpt_cur
        del trk_cur
        del thk_cur
        
        sys.stdout.write("  Writing Thickness Grid: %d%%   \n" % (100) )
        sys.stdout.flush()


def Run(sScenarioFile, sOutputPath, modType):
    sScenarioName, sGeoLocPath = ReadScenarioFile(sScenarioFile)
    
    sFGDB = os.path.join(sOutputPath,sScenarioName+".gdb")

    ReadOilmap2D(sGeoLocPath, sScenarioName, sFGDB, modType)
    
    print "  Done!"
    
    
    
    
    
#####################################################


if __name__ == "__main__":

    help_text = "Model2Shape_v3.py <Path to Scenario file> <Output Path> <options>\n     -m <model type>: 'OM2d' = Oilmap 2d Trajectory, (more coming...)"

    if len(sys.argv) < 2:
        print help_text
    else:        
        if "-help" in sys.argv[1] or "-h" in sys.argv[1]:
            print help_text

        else:
            if len(sys.argv) < 5:
                print help_text
            else:
                sScenarioFile = sys.argv[1]
                sOutputPath = sys.argv[2]
                
                if '-m' in sys.argv:
                    modType = sys.argv[sys.argv.index("-m") + 1]
                else:
                    modType = "OM2d"

                Run(sScenarioFile, sOutputPath, modType)


        
    
#C:\Library\Python\Model2File\src\test.py C:\OILMAPAV10\Loc_Data\GBR\Rundata\GBR_OIL6.INP C:\Library\Python\Model2File -m OM2d
