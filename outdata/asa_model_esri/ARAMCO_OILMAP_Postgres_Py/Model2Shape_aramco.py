'''
Created on Apr 19, 2019
@author: JFontenault
'''

import datetime
startTime = datetime.datetime.now()

import arcpy
import sys, os, struct
from read_fmt import read_lu3, read_slk, read_tr3

sr = arcpy.SpatialReference("WGS 1984")    

def CalculateDateTime(dtBase, iElapsedHours):
    d = datetime.timedelta(hours=iElapsedHours)
    dtTimeStep = dtBase + d
    return dtTimeStep
   
def PrepFCs(sSDEconn):

    sDatabase = "db_7ifhn"
    sUser = "adm_ror3v"
    sUser2 = "hsu_3yd5x"
    sPassword = "xOO8usSd=bM="

    if os.path.exists(sSDEconn) == False:
        arcpy.CreateDatabaseConnection_management(os.path.split(sSDEconn)[0], os.path.split(sSDEconn)[1],"POSTGRESQL", "localhost,9876", "DATABASE_AUTH", sUser, sPassword,"SAVE_USERNAME", sDatabase)
    
    return os.path.join(sSDEconn,".".join([sDatabase,sUser2,"template_oilmap_SpillPoint"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"template_oilmap_ShoreOil"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"template_oilmap_Spillets"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"template_oilmap_Trackline"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"template_oilmap_Thickness"]))
    
    ##temp output location
    #return os.path.join(r"C:\Projects\ARAMCO_OILMAP_ArcGIS_Integration\SampleOutput.gdb","SpillPoint"),os.path.join(r"C:\Projects\ARAMCO_OILMAP_ArcGIS_Integration\SampleOutput.gdb","ShoreOil"), os.path.join(r"C:\Projects\ARAMCO_OILMAP_ArcGIS_Integration\SampleOutput.gdb","Spillets"), os.path.join(r"C:\Projects\ARAMCO_OILMAP_ArcGIS_Integration\SampleOutput.gdb","Trackline"), os.path.join(r"C:\Projects\ARAMCO_OILMAP_ArcGIS_Integration\SampleOutput.gdb","Thickness") 
    
def ReadOilmap2D(basePath, scenarioData, sScenarioID, sSDEconn):
    
    splPoint, shr, splt, trk, thk = PrepFCs(sSDEconn)
    print "Elapsed time after creating geodatabase = "+str(datetime.datetime.now() - startTime)
    
    #Release Point
    spl_cur = arcpy.da.InsertCursor(splPoint,['SHAPE@','SCENARIO','Lon','Lat','Duration','Volume','StartDate','OilName'])
    pnt = arcpy.Point()
    pnt.X = scenarioData["Spill Lon"]
    pnt.Y = scenarioData["Spill Lat"]
    spl_cur.insertRow([pnt,sScenarioID,scenarioData["Spill Lon"],scenarioData["Spill Lat"],scenarioData["Release Duration"],
                       scenarioData["Amount Spilled"],scenarioData["StartDate"],scenarioData["Oil Name"]])    
    del spl_cur
    print "Elapsed time after creating release point = "+str(datetime.datetime.now() - startTime)
    
    
    plu3 = basePath + ".LU3"
    with open(plu3, "rb") as rdata:
        rec = read_lu3(rdata)
        

    #SPILLETS AND TRACKLINE
    splt_cur = arcpy.da.InsertCursor(splt,['SHAPE@','DATETIME','Radius_Depth_M','Type','Mass_MT','Diameter_M','Visc_cP','WaterFraction_Perc','Age_Hrs','SCENARIO'])
    shr_cur = arcpy.da.InsertCursor(shr,['SHAPE@','DATETIME','ShoreType','ShoreArea_M2','ShoreLength_M','Visc_cP','ShoreMass_MT','SCENARIO'])
    
    Array = arcpy.Array()

    
    ptr3 = basePath + ".TR3"
    with open(ptr3, "rb") as rdata:
        tr3_spl, tr3_shr = read_tr3(rec, rdata)
        
        for t in tr3_spl:
            lons = [] #list for each time step to avg for track points
            lats = []
            
            dtTimeStep = CalculateDateTime(scenarioData["StartDate"], t[0])
            
            for _t in t[1]:                    
                
                pnt = arcpy.Point()
                pnt.X = _t[0]
                pnt.Y = _t[1]
                lons.append(_t[0])
                lats.append(_t[1])
                
                splt_cur.insertRow([pnt,dtTimeStep,_t[2],_t[5],_t[6],_t[7],_t[8],_t[9],_t[10],sScenarioID])
                    
            lon_avg = sum(lons)/float(len(lons))
            lat_avg = sum(lats)/float(len(lats))
            pnt = arcpy.Point(lon_avg, lat_avg)                        
            Array.add(pnt)
        
        del splt_cur    
            
        for t in tr3_shr:
            for _t in t[1]:
                    
                dtTimeStep = CalculateDateTime(scenarioData["StartDate"], t[0])  
          
                arrayLine = arcpy.Array()   
                arrayLine.add(arcpy.Point(_t[6],_t[7])) 
                arrayLine.add(arcpy.Point(_t[8],_t[9])) 
                shrLine = arcpy.Polyline(arrayLine,sr)
                
                shr_cur.insertRow([shrLine,dtTimeStep,_t[2],_t[3],_t[4],_t[5],_t[10],sScenarioID])   
        
        del shr_cur
        
        
    trk_cur = arcpy.da.InsertCursor(trk,['SHAPE@','SCENARIO'])
    trackline = arcpy.Polyline(Array)
    trk_cur.insertRow([trackline,sScenarioID])
    Array.removeAll()
    
    del trk_cur
    print "Elapsed time after creating spillets and track = "+str(datetime.datetime.now() - startTime)
 
 
 
    #GRIDDED OUTPUT
    thk_cur = arcpy.da.InsertCursor(thk,['SHAPE@','DATETIME','TotalMass_gM2','Thickness_M','SCENARIO'])
 
 
    pslk =  basePath + ".SLK"
    with open(pslk, "rb") as rdata:
        slk = read_slk(rec, rdata)
 
 
    for t in slk:
        dtTimeStep = CalculateDateTime(scenarioData["StartDate"], t[0])
         
        for _t in t[1][:-1]: #t[1] = all cells, _t = cell, skip last?
            #for i in range(len(_t)): #i = field index
             
            dTotalMass = _t[5]
            dThickM = _t[6]
                 
            lon1 = _t[3]
            lat1 = _t[4]
            lon2 = _t[3] + _t[1]
            lat2 = _t[4] + _t[2]
                                      
            coordList = [[lon1,lat1],[lon1,lat2],[lon2,lat2],[lon2,lat1],[lon1,lat1]]        
      
            arrayPoly = arcpy.Array()   
              
            for coordPair in coordList:
                arrayPoly.add(arcpy.Point(coordPair[0],coordPair[1]))                    
            cell = arcpy.Polygon(arrayPoly,sr)
                 
            thk_cur.insertRow([cell,dtTimeStep,dTotalMass,dThickM,sScenarioID])
             
    del thk_cur
     
    print "Elapsed time after creating thickness grid = "+str(datetime.datetime.now() - startTime)


def ReadScenario(sScenarioIN3):
    scenarioData = {"Scenario":None, #string
                    "Spill Lon":None, #float
                    "Spill Lat":None, #float
                    "Release Duration":None,
                    "Amount Spilled":None,
                    "Start Year":None,
                    "Start Month":None,
                    "Start Day":None,
                    "Start Hour":None,
                    "Start Minute":None,
                    "Oil Name":None, #string
                    "StartDate":None} #date
    
    
    fileIN3 = open(sScenarioIN3,'r')
    for line in fileIN3.readlines():
        valPair = line.split("=")
        if scenarioData.has_key(valPair[0]):
            if valPair[0] in ["Scenario","Oil Name"]: #string
                scenarioData[valPair[0]] = valPair[1].strip()
            elif valPair[0] in ["Spill Lon","Spill Lat"]: #float
                scenarioData[valPair[0]] = float(valPair[1])
            else:
                scenarioData[valPair[0]] = int(valPair[1])
                
    scenarioData["StartDate"] = datetime.datetime(scenarioData["Start Year"],scenarioData["Start Month"],scenarioData["Start Day"],scenarioData["Start Hour"],scenarioData["Start Minute"],00)
    
    fileIN3.close() ##### ADDED ##### 
    
    return scenarioData


def Run(sScenarioOutZipFile):
    ##### ADDED SECTION 1 #####
    import zipfile
    
    zip = zipfile.ZipFile(sScenarioOutZipFile, 'r')
    zip.extractall(os.path.split(sScenarioOutZipFile)[0])
    zip.close()
    
    sSDEpath = os.getcwd() + '\\database.sde';
    print os.getcwd()
    
     ##### END SECTION 1 #####
    for root, dirs, files in os.walk(os.path.split(sScenarioOutZipFile)[0]):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.splitext(fullpath)[1] == '.IN3':
                sIN3file = fullpath.replace('RUNDATA', 'MODELOUT')

    print sIN3file
    
    ##### UPDATED SECTION 2 #####
    scenarioData = ReadScenario(sIN3file)    
    basePath = os.path.splitext(sIN3file)[0]  
    ##### END SECTION 2 ##### 
    
    
    #To be sys.argv later
    sScenarioID = scenarioData["Scenario"] + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # sSDEpath = ""
     
    ReadOilmap2D(basePath, scenarioData, sScenarioID, sSDEpath)
    #print scenarioData
    
    
    ##### ADDED SECTION 3 #####
    for f in os.listdir(os.path.split(sScenarioOutZipFile)[0]):
        sFilePath = os.path.join(os.path.split(sScenarioOutZipFile)[0],f)
        #print sFilePath
        if sFilePath == sScenarioOutZipFile:
            pass
        elif os.path.splitext(sFilePath)[0].upper() == basePath.upper():
            os.remove(sFilePath)
    ##### END SECTION 3 #####
    
    
    print "Elapsed time for completion = "+str(datetime.datetime.now() - startTime)   
    print "Done!"
 
    
#####################################################    
#####################################################


if __name__ == "__main__":
    Run(sys.argv[1])
