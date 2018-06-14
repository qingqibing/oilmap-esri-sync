import datetime
startTime = datetime.datetime.now()

#import arcview
import arcpy

import sys, os, struct

import numpy

import configparser

from datatypes import DT

SMP_RECORD_SIZE = 12
SML_RECORD_SIZE = 40

SARMDL_SMP_FILE_TYPE = numpy.dtype([('rec_position', numpy.int32, 1),
                        ('sim_time', numpy.int32, 1) ,
                        ('n_oil_recs', numpy.int32, 1),
                        ])

SARMDL_SML_FILE_SAR_PARTICLE = numpy.dtype([
                        ('loc', DT.POINTSP2D, 1),               #lon, lat (degrees)
                        ('none',DT.SPRECISION,1),               #mass (MT)
                        ('nwhere',numpy.int32,1),               #? onshore or on water?
                        ('mass',DT.SPRECISION,1),               #mass (MT)
                        ('radius',DT.SPRECISION,1),             #radius (M)
                        ('thickness',DT.SPRECISION,1),          #
                        ('visco',DT.SPRECISION,1),              #
                        ('fwc',DT.SPRECISION,1),                #fraction of water content (None)
                        ('flashpt',DT.SPRECISION,1),            #
                        ])

sr = arcpy.SpatialReference(os.path.join(arcpy.GetInstallInfo()["InstallDir"],r"Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj"))

def Run(sScenarioFile, sOutputPath):
    sScenarioName, sGeoLocPath = ReadScenarioFile(sScenarioFile)
    sFGDB = os.path.join(sOutputPath,sScenarioName+".gdb")

    ReadSarmap(sGeoLocPath, sScenarioName, sFGDB)
    
    print sFGDB

def ReadScenarioFile(sScenarioFile):
    sGeoLocPath = os.path.split(os.path.split(sScenarioFile)[0])[0]
    sScenarioName = os.path.splitext(os.path.split(sScenarioFile)[1])[0]
    return sScenarioName, sGeoLocPath
    print "Elapsed time after import = "+str(datetime.datetime.now() - startTime)

def CalculateDateTime(elapsed_minutes):
    dtBase = datetime.datetime(1979,12,31,00,00,00)
    day = elapsed_minutes // (24 * 60)
    elapsed_minutes = elapsed_minutes % (24 * 60)
    hour = elapsed_minutes // 60
    elapsed_minutes %= 60
    minute = elapsed_minutes // 60
    d = datetime.timedelta(days=day, hours=hour, minutes=minute)

    dtTimeStep = dtBase + d
    return dtTimeStep

def CreateFCs(sFGDB,sScenarioName,SarMode):
    import shutil
    file_name = 'IAMSAR.gdb' if SarMode == '0' else 'MONTECARLO.gdb'
    template = os.path.join(os.getcwd(), file_name)

    try:
        shutil.rmtree(sFGDB)
    except:
        sFGDB.replace(sScenarioName+".gdb",sScenarioName+"_2.gdb",)
    shutil.copytree(template, sFGDB)

    return os.path.join(sFGDB,"PARTICLES"), os.path.join(sFGDB,"TRACKLINE"), os.path.join(sFGDB,"ABCDBOX"), os.path.join(sFGDB, "ABCDPOINTS"), os.path.join(sFGDB,"SEARCHAREA")


def PrepFCs(sSDEconn):
    sDatabase = "db_qdrdy"
    sUser = "adm_w9b4n"
    sUser2 = "hsu_kepzo"
    sPassword = "fykB99ChCEk="

    if os.path.exists(sSDEconn) == False:
        arcpy.CreateDatabaseConnection_management(os.path.split(sSDEconn)[0], os.path.split(sSDEconn)[1],
                                                  "POSTGRESQL", "localhost,9876", "DATABASE_AUTH", sUser, sPassword,
                                                  "SAVE_USERNAME", sDatabase)    

    # change these tables according to postgres tables
    return os.path.join(sSDEconn,".".join([sDatabase,sUser2,"PARTICLES"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"TRACKLINE"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"ABCDBOX"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"ABCDPOINTS"])), os.path.join(sSDEconn,".".join([sDatabase,sUser2,"SEARCHAREA"]))

def ReadSarmap(sGeoLocPath, sScenarioName, sFGDB):
    
    reader = SarmapReader(sGeoLocPath + os.path.sep + "OUTDATA" + os.path.sep + sScenarioName)
    SarMode = reader.GetSarMode()
    #splt, trk, abcd, abcdpt, area = CreateFCs(sFGDB, sScenarioName, SarMode)
    sSDEpath = r"C:\oilmap\Push2ESRI\database.sde"
    splt, trk, abcd_table, abcdpt, area = PrepFCs(sSDEpath)
    time_stamp = reader.GetSRPSetting('TimeStamp')
        
    lons = [] #list for each time step to avg for track points
    lats = []

    trkline = arcpy.Array()
    start_time = None
    end_time = None
    
    for timestep in xrange(0, reader.time_steps):
        d_time = CalculateDateTime(reader._record_data['sim_time'][timestep])
        if (timestep == 0):
            start_time = d_time
        elif (timestep == reader.time_steps - 1):
            end_time = d_time
        
        spillet_data = reader._load_timestep(timestep)
        lons[:] = []
        lats[:] = []
        abcd = arcpy.Array()
        xmin = 9999
        ymin = 9999
        xmax = -9999
        ymax = -9999

        areapts = arcpy.Array()
        vertex = ['A', 'B', 'C', 'D']
        curr_vertex = 0
        for spillet in spillet_data[1:]:
            if spillet['nwhere'] <= 10:
                lon = float(spillet['loc'][0])
                lons.append(lon)
                lat = float(spillet['loc'][1])
                lats.append(lat)
                particle_type = int(spillet[2])
                particle_description = reader.GetSRPSetting('SAR Object' if particle_type == 1 else 'SAR Object_' + str(particle_type))
                    
                pnt = arcpy.Point()
                pnt.X = lon
                pnt.Y = lat
                splt_cur = arcpy.da.InsertCursor(splt,['SHAPE@','DATETIME','SCENARIO','TYPE'])
                splt_cur.insertRow([pnt,d_time,sScenarioName,particle_description])
                del splt_cur
                areapts.add(pnt)

                xmin = min(xmin, lon)
                ymin = min(ymin, lat)
                xmax = max(xmax, lon)
                ymax = max(ymax, lat)
            elif spillet['nwhere'] == 24:
                lon = float(spillet['loc'][0])
                lat = float(spillet['loc'][1])
                abcdpnt = arcpy.Point(lon, lat)
                abcd.add(abcdpnt)
                abcdpt_cur = arcpy.da.InsertCursor(abcdpt,['SHAPE@','DATETIME','SCENARIO','VERTEX'])
                abcdpt_cur.insertRow([abcdpnt,d_time,sScenarioName,vertex[curr_vertex]])
                del abcdpt_cur
                curr_vertex += 1

        if (SarMode != '0'):
            areapoly = arcpy.Multipoint(areapts)
            convex = areapoly.convexHull()
            area_cur = arcpy.da.InsertCursor(area,['SHAPE@','SCENARIO','DATETIME'])
            area_cur.insertRow([convex, sScenarioName, d_time])
            del area_cur
                
        lon_avg = (xmin + xmax) / 2
        lat_avg = (ymin + ymax) / 2
        
        trkline.add(pnt)

        abcdbox = arcpy.Polygon(abcd)
        abcd_cur = arcpy.da.InsertCursor(abcd_table,['SHAPE@','SCENARIO','DATETIME'])
        abcd_cur.insertRow([abcdbox, sScenarioName, d_time])
        del abcd_cur

    interval_hrs = int(reader.GetSRPSetting('Ideltat')) / 60
    original_case = reader.GetSRPSetting('OriginalCase')
    site_lon = float(reader.GetSRPSetting('Spill Lon'))
    site_lat = float(reader.GetSRPSetting('Spill Lat'))
    description = reader.GetSRPSetting('Description')
    trackline = arcpy.Polyline(trkline)
    trk_cur = arcpy.da.InsertCursor(trk,['SHAPE@', 'START', 'END_', 'INTERVAL_HRS', 'SCENARIO', 'SCENARIO_ID', 'SITELON', 'SITELAT', 'DESCRIPTION', 'CASENAME'])
    trk_cur.insertRow([trackline, start_time, end_time, interval_hrs, sScenarioName, sScenarioName, site_lon, site_lat, description, original_case])
    del trk_cur

class SarmapReader(object):

    def __init__(self,*args, **kwargs):
        """
        @fname is the name of the file to read from
        """
        # Ensure all constructors are called properly
        super(SarmapReader, self).__init__()

        self.fname = args[0]
        self._load_record_data()
        
    def _load_record_data(self):

        file_name = self.fname + '.smp'
        size = os.path.getsize(file_name)
        self.time_steps = (size / SMP_RECORD_SIZE) - 1

        record_data = None
        with open(file_name,'rb') as smp_file:
            smp_file.seek(1*SMP_RECORD_SIZE)
            record_data = numpy.fromfile(smp_file,dtype=SARMDL_SMP_FILE_TYPE,count=-1)

        record_data['rec_position'] -= 1
                    
        self._record_data = record_data

    def _load_timestep(self, timestep):
        spillet_data = None
        file_name = self.fname + '.sml'
        with open(file_name,'rb') as sml_file:
            sml_file.seek(self._record_data['rec_position'][timestep] * SML_RECORD_SIZE)
            nspillets = self._record_data['n_oil_recs'][timestep]
            spillet_data = numpy.fromfile(sml_file,dtype=SARMDL_SML_FILE_SAR_PARTICLE,count=nspillets)
            
        return spillet_data

    def GetSarMode(self):
        return self.ReadINIFile(self.fname + '.srp', 'OILMAPW', 'SarMode')

    def GetSRPSetting(self, setting):
        return self.ReadINIFile(self.fname + '.srp', 'OILMAPW', setting)

    def ReadINIFile(self, file_name, section, setting):
        try:
            config = configparser.ConfigParser()
            config.read(file_name)
            return config.get(section, setting)
        except:
            return ''
        
#####################################################


if __name__ == "__main__":

    help_text = "Sar2FGDB.py <Path to Scenario file> <Output Path>"

    if len(sys.argv) < 2:
        print help_text
    else:        
        if "-help" in sys.argv[1] or "-h" in sys.argv[1]:
            print help_text

        else:
            if len(sys.argv) < 3:
                print help_text
                print len(sys.argv)
            else:
                sScenarioFile = sys.argv[1]
                sOutputPath = sys.argv[2]

                Run(sScenarioFile, sOutputPath)
