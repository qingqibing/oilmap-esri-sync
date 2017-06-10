using System;
using System.Text;
using System.Data;
using System.Configuration;
using System.Web;
using System.Net;
//using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.HtmlControls;
using System.Diagnostics;
using System.IO;
using System.Timers;
using System.Collections.Generic;
using System.Collections;
using System.Drawing;
using ASAMAP.COMMON;
using System.Web.Script.Serialization;
using System.Web.Caching;
using LineObjAGOL;
using PolyObjAGOL;
using SpilletsObjAGOL;
using Aggregator;

/// <summary>
/// Summary description for OIlModelEngine
/// </summary>
public class OilModelEngine:ModelEngine
{
    private OilInputData _InputData;
    private Process _OilmodelProcess;
    private Timer _ProcessTimer;
    private string _TimeoutError;
    private DateTime _LastWrite;
    private PostEDS2AGOL _windAgg = new PostEDS2AGOL();
    private PostEDS2AGOL _currentAgg = new PostEDS2AGOL();

    [Serializable]
    public class Token
    {
        //response {"token" : "ShBh03DRIR1e1RbiNmoB-YfqPdMH31bKWY9BxlL5RcrSLRZTFhLw9RSGjbLE-faz-c2xxvq21-lSdSAobxRfEQdOcxAVbmJbm20O_GZHDuLnlJvXMSuOKuj7I23sa45M68Gi51ggAChdyjJgtOAsmg..","expires" : 1367777161054,"ssl" : false}
        public string token { get; set; }
        public long expires { get; set; }
    }

    [Serializable]
    public class webMapObject
    {
        //response {"token" : "ShBh03DRIR1e1RbiNmoB-YfqPdMH31bKWY9BxlL5RcrSLRZTFhLw9RSGjbLE-faz-c2xxvq21-lSdSAobxRfEQdOcxAVbmJbm20O_GZHDuLnlJvXMSuOKuj7I23sa45M68Gi51ggAChdyjJgtOAsmg..","expires" : 1367777161054,"ssl" : false}
        public string id { get; set; }
    }

    private static readonly string publishMode = ConfigurationManager.AppSettings["publishMode"];
    private static readonly string urlPortalRoot = ConfigurationManager.AppSettings["urlPortalRoot"];
    private static readonly string urlSampleWebMapJSON = ConfigurationManager.AppSettings["urlSampleWebMapJSON"];
    private static readonly string scenarioIDExpression = ConfigurationManager.AppSettings["scenarioIDExpression"];
    private static readonly string imgWebMapThumbnail = ConfigurationManager.AppSettings["imgWebMapThumbnail"];
    private static readonly string urlSampleMapService = ConfigurationManager.AppSettings["urlSampleMapService"];
    private static readonly string urlAGOProxyMapService = ConfigurationManager.AppSettings["urlAGOProxyMapService"];
    private static readonly string urlOilMapFeatureService = ConfigurationManager.AppSettings["urlOilMapFeatureService"];
    private static readonly string urlAGOAddItem = String.Concat(urlPortalRoot, ConfigurationManager.AppSettings["urlAGOAddItem"]);
    private static readonly string urlAGOShareItem = String.Concat(urlPortalRoot, ConfigurationManager.AppSettings["urlAGOShareItem"]);
    private static readonly string agoTokenService = String.Concat(urlPortalRoot, ConfigurationManager.AppSettings["agoTokenService"]);
    private static readonly string agoUser = ConfigurationManager.AppSettings["agoUser"];
    private static readonly string agoPassword = ConfigurationManager.AppSettings["agoPassword"];
    private static readonly string agsTokenService = ConfigurationManager.AppSettings["agsTokenService"];
    private static readonly string agsUser = ConfigurationManager.AppSettings["agsUser"];
    private static readonly string agsPassword = ConfigurationManager.AppSettings["agsPassword"];

    //input ddinp,
    private string ReadSPillData(string infile, ref LineObjJSON trjln, ref ArrayList oilobj, ref ArrayList oilcns, ref ArrayList thkns, int model_id, int chem_item)
    {
        string result = "OK";
        int nsteps = 0;
        
        OILMODEL.Oilidx[] oilidx = new OILMODEL.Oilidx[1];
        
        try
        {
            switch (model_id)
            {
                case 1:
                    infile = Path.ChangeExtension(infile, ".omp");
                    break;
                case 2:
                    infile = Path.ChangeExtension(infile, ".omp");
                    break;
                case 3:
                    infile = Path.ChangeExtension(infile, ".clu");
                    infile = infile.ToUpper().Replace("\\OUTDATA\\", "\\MODELOUT\\");
                    break;
            }

            //if (File.Exists(infile))
            //    result = READOMP(infile, ref oilidx);
            //else
            //{
            //    //result = infile + " doesnt exist";
            //    return result;
            //}

            if (result != "OK")
                return result;

            nsteps = oilidx.GetLength(0);

            switch (model_id)
            {
                case 1:
                    infile = Path.ChangeExtension(infile, ".oml");
                    break;
                case 2:
                    infile = Path.ChangeExtension(infile, ".oml");
                    break;
                case 3:
                    infile = Path.ChangeExtension(infile, ".ctr");
                    break;
            }

            //if (File.Exists(infile))
            //    result = READOML(infile, oilidx, ref trjln, ref oilobj);
            //else
            //{
            //    result = infile + " doesnt exist";
            //    return result;
            //}

            if (result != "OK")
                return result;

            if (model_id != 2)
            {
                switch (model_id)
                {
                    case 1:
                        {
                            infile = Path.ChangeExtension(infile, ".omc");

                            if (File.Exists(infile))
                                //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                result = "not sending info to agol";
                            else
                            {
                                result = infile + " doesnt exist";
                                return "OK for OML, OMP, but no OMC";
                            }

                            if (result != "OK")
                                return "OK for OML, OMP, but  no OMC";
                        }
                        break;
                    case 3:
                        {
                            switch (chem_item)  //different chemical scalar information
                            {
                                case 0:
                                    {
                                        infile = Path.ChangeExtension(infile, ".omc");

                                        if (File.Exists(infile))
                                            //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                            result = "not sending info to agol";

                                        else
                                        {
                                            result = infile + " doesnt exist";
                                            return "OK for OML, OMP, but no OMC";
                                        }

                                        if (result != "OK")
                                            return "OK for OML, OMP, but  no OMC";
                                    }
                                    break;
                                case 1:
                                    {
                                        infile = Path.ChangeExtension(infile, ".omc");

                                        if (File.Exists(infile))
                                            //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                            result = "not sending info to agol";
                                        else
                                        {
                                            result = infile + " doesnt exist";
                                            return "OK for OML, OMP, but no OMC";
                                        }

                                        if (result != "OK")
                                            return "OK for OML, OMP, but  no OMC";
                                    }
                                    break;
                                case 2:
                                    {
                                        infile = Path.ChangeExtension(infile, ".omc");

                                        if (File.Exists(infile))
                                            //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                            result = "not sending info to agol";
                                        else
                                        {
                                            result = infile + " doesnt exist";
                                            return "OK for OML, OMP, but no OMC";
                                        }

                                        if (result != "OK")
                                            return "OK for OML, OMP, but  no OMC";
                                    }
                                    break;
                                case 3:
                                    {
                                        infile = Path.ChangeExtension(infile, ".omc");

                                        if (File.Exists(infile))
                                            //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                            result = "not sending info to agol";
                                        else
                                        {
                                            result = infile + " doesnt exist";
                                            return "OK for OML, OMP, but no OMC";
                                        }

                                        if (result != "OK")
                                            return "OK for OML, OMP, but  no OMC";
                                    }
                                    break;
                                case 4:
                                    {
                                        infile = Path.ChangeExtension(infile, ".omc");

                                        if (File.Exists(infile))
                                            //result = READOMC(infile, nsteps, ref oilcns, ref thkns);
                                            result = "not sending info to agol";
                                        else
                                        {
                                            result = infile + " doesnt exist";
                                            return "OK for OML, OMP, but no OMC";
                                        }

                                        if (result != "OK")
                                            return "OK for OML, OMP, but  no OMC";
                                    }
                                    break;
                            }
                        }
                        break;
                }
            }
        }
        catch (Exception ex)
        {
            result = "ERROR: Main Model Read: " + ex.Message;
        }
        return result;
    }


    ///// <summary>
    ///// Read Oil Model Index 
    /// </summary>
    /// <param name="file">.inp file name </param>
    /// <param name="oilidx"></param>
    /// <returns></returns>
    private static string READOMP(string file, ref OILMODEL.Oilidx[] oilidx)
    {

        int trjver;
        int ntsteps = -1;
        long filebytes = -1;
        FileStream fs = null;
        BinaryReader reader = null;
        int pos = 0;
        try
        {
            fs = File.Open(file, FileMode.Open, FileAccess.Read, FileShare.Read);   //OMP file
            filebytes = fs.Length;

            if (filebytes < 4)
            {
                return "ERROR: Empty OMP file or missing contents";
            }

            reader = new BinaryReader(fs);

            trjver = reader.ReadInt32();  //Traj version indicator 
            if (trjver == 1002)
                ntsteps = Convert.ToInt32(filebytes / 12) - 1;
            else
            {
                fs.Close();
                fs.Dispose();

                return "ERROR: Oilmap Version is not supported.";
            }

            pos = 12;  //Jump three 4 bytes
            reader.BaseStream.Seek(pos, SeekOrigin.Begin);
            System.Array.Resize(ref oilidx, ntsteps);

            for (int i = 0; i < ntsteps; i++)
            {
                oilidx[i] = new OILMODEL.Oilidx(reader.ReadInt32(), reader.ReadInt32(), reader.ReadInt32());
            }
            reader.Close();
            fs.Close();
            fs.Dispose();

        }
        catch (Exception ex)
        {
            return "ERROR: ReadOMP: " + ex.Message;
        }
        finally
        {
            if (fs != null)
            {
                fs.Close();
            }
            if (reader != null)
            {
                reader.Close();
            }
        }

        return "OK";
    }

    private static string paddingDate(int num)
    {
        if (num < 10)
        {
            return "0" + num;
        }
        else
        {
            return num.ToString();
        }
    }

    /// <summary>
    /// Read Spillets
    /// </summary>
    /// <param name="file"></param>
    /// <param name="oilidx"></param>
    /// <param name="trjln"></param>
    /// <param name="oilobj"></param>
    /// <returns></returns>

    private string READOML(string file, OILMODEL.Oilidx[] oilidx, ref LineObjJSON trjln, ref ArrayList oilobj)
    {
        int totalcnt = 0;
        double totallat = 0;
        double totallon = 0;
        long filebytes = -1;
        FileStream fs_oml = null;
        BinaryReader reader1 = null;

        OILMODEL.oilobject oilspillet = new OILMODEL.oilobject();

        int ntsteps = oilidx.GetLength(0);
        try
        {
            //System.Array.Resize(ref trjlin, ntsteps);
            fs_oml = File.Open(file, FileMode.Open, FileAccess.Read, FileShare.Read);  //OML file, with spllits for each step

            filebytes = fs_oml.Length;
            if (filebytes < 4)
            {
                return "ERROR: Empty OML file or missing contents";
            }
            reader1 = new BinaryReader(fs_oml);

            /// All centroids for spillets
            List<List<double>> verticesList = new List<List<double>>(ntsteps);

            for (int i = 0; i < ntsteps; i++)
            {
                totallat = 0;
                totallon = 0;
                totalcnt = 0;

                //OILMODEL.oilobject[] oilobj1 = new OILMODEL.oilobject[1];
                //System.Array.Resize(ref oilobj1, oilidx[i].nrecs);
                int daynight = 1;  //Calculate if the location is day or night

                for (int j = 0; j < oilidx[i].nrecs; j++)
                {
                    oilspillet = new OILMODEL.oilobject(reader1.ReadSingle(), reader1.ReadSingle(), reader1.ReadSingle(),
                    reader1.ReadInt32(), reader1.ReadSingle(), reader1.ReadSingle(), reader1.ReadSingle(), reader1.ReadSingle(), reader1.ReadSingle(), reader1.ReadSingle(), daynight);

                    if (oilspillet.nwhere == 1) // || oilspillet.nwhere == 0 || oilspillet.nwhere == -1)
                    {
                        if (oilspillet.lon >= -180 && oilspillet.lon <= 180)
                        {
                            totallat = oilspillet.lat + totallat;
                            totallon = oilspillet.lon + totallon;
                            totalcnt = totalcnt + 1;

                            SpilletsObjAGOL.Attributes oilobj1Atts = new SpilletsObjAGOL.Attributes();
                            SpilletsObjAGOL.Geometry oilobj1Geom = new SpilletsObjAGOL.Geometry();
                            oilobj1Geom.spatialReference = new SpilletsObjAGOL.Spatialref();

                            DateTime spilletTime = new DateTime(1979, 12, 31, 0, 0, 0, 0);

                            int minutes = oilidx[i].time;
                            spilletTime = spilletTime.AddMinutes(minutes);

                            oilobj1Atts.DATETIME = spilletTime.Year.ToString() + "-" + paddingDate(spilletTime.Month) + "-" + paddingDate(spilletTime.Day) + " " + paddingDate(spilletTime.Hour) + ":" + paddingDate(spilletTime.Minute) + ":00";
                            oilobj1Atts.SCENARIO_ID = _InputData.fileName;
                            oilobj1Atts.HOURS = i.ToString();
                            oilobj1Geom.x = Math.Round(oilspillet.lon, 3);
                            oilobj1Geom.y = Math.Round(oilspillet.lat, 3);
                            SpilletsJSON oilobj1 = new SpilletsJSON();
                            oilobj1.geometry = oilobj1Geom;
                            oilobj1.attributes = oilobj1Atts;
                            oilobj.Add(oilobj1);
                        }
                    }
                }

                List<double> vertics = new List<double>(2);
                if (totalcnt > 0)
                    vertics.Add(Math.Round(totallon / totalcnt, 3));
                    vertics.Add(Math.Round(totallat / totalcnt,3));

                //if ((totalcnt == 0) && (i > 1))

                verticesList.Add(vertics); 
    
                //For Spillets Info
                if (oilobj.Count > 6500)
                {
                    InsertFeatures("1", new JavaScriptSerializer().Serialize(oilobj).ToString(), GetAGOToken());

                    //post2AGOL(oilobj, 1);
                    oilobj.Clear();
                }
            }
            //spillets post
            //post2AGOL(oilobj, 1);
            InsertFeatures("1", new JavaScriptSerializer().Serialize(oilobj).ToString(), GetAGOToken());

            List<List<List<double>>> pathTList = new List<List<List<double>>>(1);
            LineObjAGOL.Geometry pathT = new LineObjAGOL.Geometry();
            pathTList.Add(verticesList);
            pathT.spatialReference = new LineObjAGOL.Spatialref();
            pathT.paths = pathTList;
            trjln.geometry = pathT;
            reader1.Close();
            fs_oml.Close();
            fs_oml.Dispose();
        }
        catch (Exception ex)
        {
            return "ERROR: Read OML Trajectory Line: " + ex.Message;
        }
        finally
        {
            if (reader1 != null)
            {
                reader1.Close();
            }
            if (fs_oml != null)
            {
                fs_oml.Close();
            }
        }
        return "OK";
    }
    /// <summary>
    /// Read Concentration information, not valid for back track model 
    /// </summary>
    /// <param name="file"></param>
    /// <param name="ntsteps"></param>
    /// <param name="oilcns"></param>
    /// <param name="thkns"></param>
    /// <returns></returns>
    private string READOMC(string file, int ntsteps, ref ArrayList oilcns, ref ArrayList thkns)
    {
        int cpos = 0;
        int fpos = 0;
        int stepsize = 0;
        long filebytes = -1;  // edna 
        FileStream fs_omc = null;
        BinaryReader reader2 = null;

        OILMODEL.oilThickness oilthk = new OILMODEL.oilThickness();
        try
        {
            fs_omc = File.Open(file, FileMode.Open, FileAccess.Read, FileShare.Read);  //OMC Thickness, file, with spllits for each step

            filebytes = fs_omc.Length;
            filebytes = fs_omc.Length;
            if (filebytes < 4)
            {
                return "ERROR: Empty OMC file or missing contents";
            }

            reader2 = new BinaryReader(fs_omc);

            Int16 a = 0;
            Int16 ncrecs = 0;
            fpos = 0;
            ArrayList thincknessGridAGOL = new ArrayList { };
            
            for (int iii = 0; iii < ntsteps; iii++)
            {
                cpos = fpos;

                reader2.BaseStream.Seek(cpos, SeekOrigin.Begin);
                ncrecs = reader2.ReadInt16();

                OILMODEL.contobj[] cntobj1 = new OILMODEL.contobj[1];
                System.Array.Resize(ref cntobj1, ncrecs);
                
                oilthk = new OILMODEL.oilThickness(a, reader2.ReadInt16(), reader2.ReadInt16(), reader2.ReadInt16(), reader2.ReadSingle(),
                     reader2.ReadSingle(), reader2.ReadSingle(), reader2.ReadSingle(), reader2.ReadInt32(), reader2.ReadSingle());
                
                DateTime thicknessTime = new DateTime(1979, 12, 31, 0, 0, 0, 0);

                int minutes = oilthk.sTime;
                thicknessTime = thicknessTime.AddMinutes(minutes);
                                               
                for (int i = 0; i < ncrecs; i++){
                    cntobj1[i] = new OILMODEL.contobj(reader2.ReadInt16(), reader2.ReadInt16(), reader2.ReadSingle());

                    if (cntobj1[i].mass > .00004)
                    {
                        PolyObjAGOL.Attributes oilthickAtts = new PolyObjAGOL.Attributes();
                        PolyObjAGOL.Geometry oilobj1Geom = new PolyObjAGOL.Geometry();

                        oilthickAtts.DATETIME = thicknessTime.Year.ToString() + "-" + paddingDate(thicknessTime.Month) + "-" + paddingDate(thicknessTime.Day) + " " + paddingDate(thicknessTime.Hour) + ":" + paddingDate(thicknessTime.Minute) + ":00";
                        oilthickAtts.SCENARIO_ID = _InputData.fileName;
                        oilthickAtts.THICK_MM = Math.Round(cntobj1[i].mass, 6);

                        List<List<List<double>>> ringGroup = new List<List<List<double>>>(1);
                        List<List<double>> ringSet = new List<List<double>>(5);

                        //Vertices based on XP...
                        //double y1 = Math.Round(oilthk.olatoil + cntobj1[i].i * oilthk.dlatoil, 7);//oy+i*dy
                        //double x1 = Math.Round(oilthk.olonoil + cntobj1[i].j * oilthk.dlonoil + oilthk.dlonoil, 7); //ox+j*dx + dx
                        //double y2 = Math.Round(oilthk.olatoil + cntobj1[i].i * oilthk.dlatoil + oilthk.dlatoil, 7);//oy+i*dy + dy
                        //double x2 = Math.Round(oilthk.olonoil + cntobj1[i].j * oilthk.dlonoil, 7); //ox+j*dx

                        double x1 = Math.Round(oilthk.olonoil + ((cntobj1[i].i - 1) * oilthk.dlonoil), 6);
                        double y1 = Math.Round(oilthk.olatoil + ((cntobj1[i].j - 1) * oilthk.dlatoil), 6);
                        double x2 = Math.Round(oilthk.olonoil + (cntobj1[i].i * oilthk.dlonoil), 6);
                        double y2 = Math.Round(oilthk.olatoil + (cntobj1[i].j * oilthk.dlatoil), 6);

                        List<double> ringVertic1 = new List<double> { x1, y1 };
                        ringSet.Add(ringVertic1);
                        List<double> ringVertic4 = new List<double> { x2, y1 };
                        ringSet.Add(ringVertic4);
                        List<double> ringVertic3 = new List<double> { x2, y2 };
                        ringSet.Add(ringVertic3);
                        List<double> ringVertic2 = new List<double> { x1, y2 };
                        ringSet.Add(ringVertic2);
                        List<double> ringVertic5 = new List<double> { x1, y1 };
                        ringSet.Add(ringVertic5);

                        ringGroup.Add(ringSet);

                        oilobj1Geom.rings = ringGroup;
                        oilobj1Geom.spatialReference = new PolyObjAGOL.Spatialref();
                        PolyObjJSON oneGridCell = new PolyObjJSON();
                        oneGridCell.attributes = oilthickAtts;
                        oneGridCell.geometry = oilobj1Geom;
                        thincknessGridAGOL.Add(oneGridCell);

                        //parse out groups of data
                        if (thincknessGridAGOL.Count > 950)
                        {
                            InsertFeatures("2", new JavaScriptSerializer().Serialize(thincknessGridAGOL).ToString(), GetAGOToken());
                            //post2AGOL(thincknessGridAGOL, 2);
                            thincknessGridAGOL.Clear();
                        }
                    }
                }

                //parse out groups of data
                if (thincknessGridAGOL.Count > 950)
                {
                    InsertFeatures("2", new JavaScriptSerializer().Serialize(thincknessGridAGOL).ToString(), GetAGOToken());
                    //post2AGOL(thincknessGridAGOL, 2);
                    thincknessGridAGOL.Clear();
                }

                stepsize = 4 * 8 + ncrecs * 8;
                fpos = cpos + stepsize;
            }
            //post thickness polygons
            //post2AGOL(thincknessGridAGOL, 2);
            InsertFeatures("2", new JavaScriptSerializer().Serialize(thincknessGridAGOL).ToString(), GetAGOToken());
            reader2.Close();
            fs_omc.Close();
            fs_omc.Dispose();
        }
        catch (Exception ex)
        {
            return "ERROR: ReadOMC: " + ex.Message;
        }
        finally
        {
            if (reader2 != null)
            {
                reader2.Close();
            }
            if (fs_omc != null)
            {
                fs_omc.Close();
            }
        }
        return "OK";
    }

	public OilModelEngine(OilInputData inputData, double timeout)
	{
        _InputData = inputData;
        _TimeoutError = "";
        _OilmodelProcess = new Process();
        _ProcessTimer = new Timer();
        _ProcessTimer.Elapsed += _ProcessTimer_Elapsed;
        _ProcessTimer.Interval = timeout;
	}

    void _ProcessTimer_Elapsed(object sender, ElapsedEventArgs e)
    {
        if (_OilmodelProcess != null && !_OilmodelProcess.HasExited)
        {
            bool testFile = false;
            string outputFile = _InputData.outputPath + "\\" + _InputData.fileName + ".OML";
            if (File.Exists(outputFile))
            {
                testFile = true;
                if (_LastWrite != null)
                {
                    if (File.GetLastWriteTime(outputFile) == _LastWrite)
                        testFile = false;
                }
                _LastWrite = File.GetLastWriteTime(outputFile);
            }
            else
                testFile = true;

            if (!(testFile))
            {
                _TimeoutError = "ERROR: Oilmodel.exe has timed out";
                _OilmodelProcess.Kill();
                _ProcessTimer.Stop();
            }
        }
    }
    internal string runModel()
    {
        if (Path.GetExtension(_InputData.coastLineFile.ToUpper()) == ".SHP")
        {
            //Check SHP file to make sure spill point isn't on land.
            PointF incPoint = new PointF((float)_InputData.spillLon, (float)_InputData.spillLat);
            ShapeFile myFile = new ShapeFile();
            myFile.LoadShapeFile(_InputData.coastLineFile);
            bool isPointOnLand = false;
            if (myFile.ShapeType == ShapeFileType.SHAPE_TYPE_POLYGONS)
            {
                foreach (Polygon myPoly in myFile.Polygons)
                {
                    if (Utils.PointInPolygon(incPoint, myPoly))
                    {
                        isPointOnLand = true;
                        break;
                    }
                }
            }

            if (isPointOnLand)
            {
                return "Spill point is on land. Choose another site.";
            }
        }

        //Set the file names
        string origInpFile = _InputData.inpPath + "\\" + _InputData.inpFileName;
        string inpFile = _InputData.inpPath + "\\" + _InputData.fileName + ".inp";
        //Copy Files
        File.Copy(origInpFile, inpFile, true);

        if (File.Exists(Path.GetDirectoryName(_InputData.inpPath) + "\\Fates\\tempdbf.dbf"))
            File.Delete(Path.GetDirectoryName(_InputData.inpPath) + "\\Fates\\tempdbf.dbf");
        
        //Set up the INP file
        WritePrivateProfileString("OILMAPW", "Scenario", _InputData.scenario, inpFile);
        WritePrivateProfileString("OILMAPW", "Spill Lon", _InputData.spillLon.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Spill Lat", _InputData.spillLat.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Grid File", Path.GetFileName(_InputData.coastLineFile), inpFile);
        WritePrivateProfileString("OILMAPW", "Splon1", _InputData.splon1, inpFile);
        WritePrivateProfileString("OILMAPW", "Splat1", _InputData.splat1, inpFile);
        WritePrivateProfileString("OILMAPW", "Start Year", _InputData.start.Year.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Start Month", _InputData.start.Month.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Start Day", _InputData.start.Day.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Start Hour", _InputData.start.Hour.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Start Minute", _InputData.start.Minute.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "SpillTime1", _InputData.spillTime1, inpFile);
        WritePrivateProfileString("OILMAPW", "Amount1", _InputData.SpillAmount.ToString(), inpFile);  //xp added 3/28/2011
        WritePrivateProfileString("OILMAPW", "OilUnit1", _InputData.SpillUnits.ToString(), inpFile);  //xp added 3/28/2011
        WritePrivateProfileString("OILMAPW", "Simulation Length", _InputData.simulationLength.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Ideltat", _InputData.modelStep.ToString(), inpFile);  //xp modified
        WritePrivateProfileString("OILMAPW", "out_intvl", _InputData.outputInterval.ToString(), inpFile);  //xp modified
        WritePrivateProfileString("OILMAPW", "Evaporation On", _InputData.evaporationOn.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Entrainment On", _InputData.entrainOn.ToString(), inpFile);

        if (_InputData.currentFile != "")
            WritePrivateProfileString("OILMAPW", "Current File", Path.GetFileName(_InputData.currentFile), inpFile);
        else
            WritePrivateProfileString("OILMAPW", "Current File", "_NO_DATA.DIR", inpFile);

        if (_InputData.windsFile != "")
        {
            WritePrivateProfileString("OILMAPW", "Number Of Wind Files", "1", inpFile);
            WritePrivateProfileString("OILMAPW", "WindFile1", Path.GetFileName(_InputData.windsFile), inpFile);
        }
        else
            WritePrivateProfileString("OILMAPW", "Number Of Wind Files", "0", inpFile);

        WritePrivateProfileString("OILMAPW", "Oil Name", _InputData.oilType, inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Database", "0", inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Density", _InputData.oilDensity.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Viscosity", _InputData.oilDensity.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Tension", _InputData.oilSurfaceTension.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil MinThick", _InputData.oilMinimumThickness.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil InitialBP", _InputData.oilInitialBoilingPoint.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil EvapA", _InputData.oilEvapConstantA.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil EvapB", _InputData.oilEvapConstantB.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Gradient", _InputData.oilGradient.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Amount Spilled", _InputData.SpillAmount.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Oil Units", _InputData.SpillUnits.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Release Duration", _InputData.spillDuration.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Duration1", _InputData.spillDuration.ToString(), inpFile);
        WritePrivateProfileString("OILMAPW", "Grid File", Path.GetFileName(_InputData.coastLineFile), inpFile);

        WritePrivateProfileString("OILMAPW", "EcopWinds", _InputData.ecopWinds, inpFile);
        WritePrivateProfileString("OILMAPW", "EcopCurrents", _InputData.ecopCurrents, inpFile);

        WritePrivateProfileString("OILMAPW", "Water Temp", _InputData.WaterTemp.ToString(), inpFile);

        if (_InputData.CurrMag != -999)
        {
            WritePrivateProfileString("OILMAPW", "UseConstantCurrent", "1", inpFile);
            WritePrivateProfileString("OILMAPW", "ConstantCurrentSpeed", _InputData.CurrMag.ToString(), inpFile);
            WritePrivateProfileString("OILMAPW", "ConstantCurrentUnit", "3", inpFile);
            WritePrivateProfileString("OILMAPW", "ConstantCurrentDirection", _InputData.CurrDir.ToString(), inpFile);
        }
        else
        {
            WritePrivateProfileString("OILMAPW", "UseContantCurrent", "0", inpFile);
        }

        string outInpFile = Path.GetDirectoryName(_InputData.inpPath) + "\\outdata\\" + _InputData.fileName + ".inp";
        File.Copy(inpFile, outInpFile);

        //Try to launch the oilmodel exe
        bool prcResult = false;
        try
        {
            string exePath = _InputData.exePath + "\\oilmodel.exe";
            if (File.Exists(exePath)) //make sure the exe is there
                _OilmodelProcess.StartInfo.FileName = String.Format("\"{0}\"", exePath);
            else
                return "ERROR: oilmodel.exe was not found";
            if (!File.Exists(inpFile))
                return "ERROR: inp file not found";

            _OilmodelProcess.StartInfo.CreateNoWindow = false;
            _OilmodelProcess.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
            _OilmodelProcess.StartInfo.ErrorDialog = false;
            _OilmodelProcess.StartInfo.Arguments = String.Format("\"{0}\"", inpFile);
            prcResult = _OilmodelProcess.Start();

            _ProcessTimer.Start();
            while (!_OilmodelProcess.HasExited)
            {
                if (!_OilmodelProcess.Responding)
                    _OilmodelProcess.Kill();
            }            
            _ProcessTimer.Stop();
           
            string myFile = Path.ChangeExtension(outInpFile, ".OML");

            if (!(File.Exists(myFile)))
            {
                prcResult = _OilmodelProcess.Start();

                _ProcessTimer.Start();
                while (!_OilmodelProcess.HasExited)
                {
                    if (!_OilmodelProcess.Responding)
                        _OilmodelProcess.Kill();
                }
                _ProcessTimer.Stop();
            }

            _OilmodelProcess.Dispose();

            if (!(File.Exists(myFile)))
                return "ERROR: Model did not run successfully.";

        }
        catch (Exception ex)
        {
            return "ERROR: " + ex.Message;
        }
        
        //string outputSpill = "";
        //LineObjJSON trajSpill = new LineObjJSON { };
        //ArrayList oilObjSpill = new ArrayList();
        //ArrayList oilcnsSpill = new ArrayList();
        //ArrayList thicknessSpill = new ArrayList();

        //if (_TimeoutError.Contains("ERROR:"))
        //    return _TimeoutError;
        //else
        //    //This will write out the thickness stuff
        //    outputSpill = ReadSPillData(outInpFile, ref trajSpill, ref oilObjSpill, ref oilcnsSpill, ref thicknessSpill, 1, 1);

        //    //This will Post trackline and Spillets info
        //    createTrackline(trajSpill);
        //    //Create EPOc/Unix time
        var timeStart = (_InputData.start - new DateTime(1970, 1, 1, 0, 0, 0));
        var timeEnd = (_InputData.end - new DateTime(1970, 1, 1, 0, 0, 0));

        //    //This will create WebMap to be retured
        string webmapIDJSON;
        webmapIDJSON = CreateWebMap(agoUser, _InputData.fileName, _InputData.caseName, timeStart.TotalSeconds.ToString(), timeEnd.TotalSeconds.ToString(), (_InputData.bBox.west + "," + _InputData.bBox.south + "," + _InputData.bBox.east + "," + _InputData.bBox.north), "",_InputData.description);
        webMapObject JSONObj = new JavaScriptSerializer().Deserialize<webMapObject>(webmapIDJSON);
        ShareItem(agoUser, JSONObj.id, _InputData.every1, "true", _InputData.groupID, "");

        return "model complete";
        //    return webmapIDJSON;
        //    //_InputData.fileName;  
        //    //return Path.GetFileNameWithoutExtension(_InputData.fileName); 
    }
    
    public void post2AGOL(Object DataObj,int serviceNumber)
    {
        string postLineData = "layerID=" + serviceNumber + "&features=" + new JavaScriptSerializer().Serialize(DataObj);
        byte[] byteArray;
        byteArray = Encoding.UTF8.GetBytes(postLineData);
        //InsertFeatures(serviceNumber.ToString(), new JavaScriptSerializer().Serialize(DataObj).ToString(), GetAGSToken());

        //Construct Post request
        HttpWebRequest request = HttpWebRequest.Create(ConfigurationManager.AppSettings["AGOLProxyInsert"]) as HttpWebRequest;
        request.Method = "POST";
        request.ContentType = "application/x-www-form-urlencoded";
        request.ContentLength = byteArray.Length;
        
        ////request.BeginGetRequestStream(new AsyncCallback(GetRequestStreamCallback), request);
        using (Stream streamWriter = request.GetRequestStream())
        {
            streamWriter.Write(byteArray, 0, byteArray.Length);
            streamWriter.Close();
        }
            
    }
    private void createTrackline(LineObjJSON tracklineData)
    {
        //create JSON object from trrackline
        LineObjAGOL.Attributes table = new LineObjAGOL.Attributes();
        string[] scenerioDateFormat = _InputData.spillTime1.Split(' ');
        //2013-10-16 11:00:00
        table.DATIMETIME = scenerioDateFormat[0] + '-' + scenerioDateFormat[1] + '-' + scenerioDateFormat[2] + ' ' + scenerioDateFormat[3] + ":00:00";
        table.SCENARIO_ID = _InputData.fileName;
        tracklineData.attributes = table;
        ArrayList finalTrack = new ArrayList();
        finalTrack.Add(tracklineData);

        InsertFeatures("0", new JavaScriptSerializer().Serialize(finalTrack).ToString(), GetAGOToken());
        
        //Stream postStream = request.EndGetRequestStream(asynchronousResult); \\for async
        //create JSON
        //string postLineData = "layerID=0&features=" + new JavaScriptSerializer().Serialize(finalTrack);
        //byte[] byteArray;
        //byteArray = Encoding.UTF8.GetBytes(postLineData);

        ////Construct Post request
        //HttpWebRequest request = HttpWebRequest.Create(ConfigurationManager.AppSettings["AGOLProxyInsert"]) as HttpWebRequest;
        //request.Method = "POST";
        //request.ContentType = "application/x-www-form-urlencoded";
        //request.ContentLength = byteArray.Length;
        
        //using (Stream streamWriter = request.GetRequestStream())
        //{
        //    streamWriter.Write(byteArray, 0, byteArray.Length);
        //    streamWriter.Close();
        //}
        //post WINDS and CURRENTS
        _currentAgg.ProcessEDS2AGOL(_InputData.currentFile, _InputData.exePath, "current");
        _windAgg.ProcessEDS2AGOL(_InputData.windsFile, _InputData.exePath, "wind");
    }

    public static string CreateWebMap(
        string username,
        string scenarioID,
        string title,
        string startTime,
        string endTime,
        string extent,
        string tokenIn,
        string descriptionText
        )
    {
        string token = tokenIn;
        if (String.IsNullOrEmpty(token))
        {
            //IF NO AGOTOKEN SENT IN, CREATE ONE
            token = GetAGOToken();
            if (string.IsNullOrEmpty(token))
            {
                throw new WebException("No AGO token available; Tried to generate token but failed.", WebExceptionStatus.TrustFailure);
            }
        }
        string urlAGOAddItemUser = string.Format(urlAGOAddItem, username);

        var sampleJsonWebmap = urlSampleWebMapJSON;
        if (string.IsNullOrEmpty(token))
        {

        }
        else
        {
            sampleJsonWebmap += string.Format("&token={0}", token);
        }

        string sampleWebMapJSON = DoPostForString(sampleJsonWebmap, "");

        if (sampleWebMapJSON.ToLower().Contains("\"error\":"))
        {
            return sampleWebMapJSON;
        }

        //BUG: When reading in JSON, the + signs in ImageData are converted to spaces, so URL encode them!!!
        sampleWebMapJSON = sampleWebMapJSON.Replace("+", "%2b");

        string lowerSampleWebMapJSON = sampleWebMapJSON.ToLower();
        //"timeSlider":{"properties":{"startTime":1378987200000,"endTime":1379246400000,"thumbCount":2,"thumbMovingRate":2000,"timeStopInterval":{"interval":59,"units":"esriTimeUnitsMinutes"}}}
        //replace scenario_id, starttime, endtime
        //":{"startTime":1362096000000,"endTime":1362272460973,"thumbCount":2
        //objective:find beginning index of "startTime":
        int idxStartTime = sampleWebMapJSON.ToLower().IndexOf("\"starttime");
        if (idxStartTime < 0)
        {
            throw new Exception("startTime not found in web map");
        }
        //objective:find beginning index of ,"thumbcount
        int idxThumbCount = sampleWebMapJSON.ToLower().IndexOf(",\"thumbcount");
        if (idxThumbCount < 0)
        {
            throw new Exception("thumbCount not found in web map");
        }
        string sampleTimeRange = sampleWebMapJSON.Substring(idxStartTime, idxThumbCount - idxStartTime);

        //convert seconds to milliseconds
        string newTimeRange = string.Format("\"startTime\":{0},\"endTime\":{1}", startTime + "000", endTime + "000");

        string newWebMapJSON = sampleWebMapJSON.Replace(sampleTimeRange, newTimeRange);

        //REPLACE SCENARIO ID
        string newScenarioIDExpression = string.Format("SCENARIO = '{0}'", scenarioID);
        newWebMapJSON = newWebMapJSON.Replace(scenarioIDExpression, newScenarioIDExpression);

        //REPLACE MAPSERVICE URL
        if (publishMode.Equals("ags"))
        {
            newWebMapJSON = newWebMapJSON.Replace(urlSampleMapService, urlAGOProxyMapService);
        }

        //REPLACE time stuff (now hardcoded to 59 minutes; replace with interval parameter)
        newWebMapJSON = newWebMapJSON.Replace("\"thumbCount\":2,\"thumbMovingRate\":2000,\"timeStopInterval\":{\"interval\":1,\"units\":\"esriTimeUnitsHours\"", "\"thumbCount\":2,\"thumbMovingRate\":2000,\"timeStopInterval\":{\"interval\":59,\"units\":\"esriTimeUnitsMinutes\"");
        
        //item
        string postData = string.Format("item=OilMap_{0}", System.Guid.NewGuid().ToString());

        //title
        postData += string.Format("&title={0}", title);

        //tags (TODO: get tags from client)
        postData += "&tags=OilMap";

        //snippet (TODO: get snippet from client)
        postData += string.Format("&snippet={0}", descriptionText);

        //extent
        if (!(string.IsNullOrEmpty(extent)))
        {
            postData += string.Format("&extent={0}", extent);
        }
        //postData += string.Format("&subtitle={0}", "adf"); 
        //text
        postData += string.Format("&text={0}", newWebMapJSON);

        //type
        postData += "&type=Web Map";

        //typeKeywords
        postData += "&typeKeywords=Web Map, OilMap,COP,HSE, ArcGIS Online";

        //thumbnailURL
        postData += string.Format("&thumbnailURL={0}", imgWebMapThumbnail);

        //format
        postData += "&f=json";

        //token
        postData += string.Format("&token={0}", token);

        return DoPostForString(urlAGOAddItemUser, postData);
    }

    public static string ShareItem(
        string username,
        string itemID,
        string everyone,
        string org,
        string groups,
        string tokenIn
        )
    {
        string token = tokenIn;
        if (String.IsNullOrEmpty(token))
        {
            //IF NO AGOTOKEN SENT IN, CREATE ONE
            token = GetAGOToken();
            if (string.IsNullOrEmpty(token))
            {
                throw new WebException("No AGO token available; Tried to generate token but failed.", WebExceptionStatus.TrustFailure);
            }
        }

        //https://www.arcgis.com/sharing/rest/content/users/jsmith/items/b512083cd1b64e2da1d3f66dbb135956/share
        //everyone=false
        //org=true
        //groups=4774c1c2b79046f285b2e86e5a20319e,cc5f73ab367544d6b954d82cc9c6dab7
        string urlAGOShareItem2 = string.Format(urlAGOShareItem, username, itemID);

        //everyone
        string postData = string.Format("everyone={0}", everyone);

        //org
        postData += string.Format("&org={0}", org);

        //groups
        if (!(string.IsNullOrEmpty(groups)))
        {
            postData += string.Format("&groups={0}", groups);
        }

        //format
        postData += "&f=json";

        //token
        postData += string.Format("&token={0}", token);

        return DoPostForString(urlAGOShareItem2, postData);
    }
    public static String GetAGSToken()
    {
        //testing
        string myToken = HttpRuntime.Cache["AGS_Token"] as string;
        if (string.IsNullOrEmpty(myToken))
        {
            myToken = GenerateAGSToken();
        }

        return myToken;
    }

    public static void ReportRemovedAGSTokenCallback(String key, object value,
        System.Web.Caching.CacheItemRemovedReason removedReason)
    {
        GenerateAGSToken();
    }

    public static string GenerateAGSToken()
    {
        //expiration=524160 (364 days)
        string postData = string.Format("f=json&username={0}&password={1}&client=requestip&expiration=524160", agsUser, agsPassword);

        string agsTokenData = DoPostForString(agsTokenService, postData);
        //{"token":"C4_fVBfIE8ULhZXrMuvFkwJ-i-u2E-XozErt8fhOqfy-3SHpeeoQStBDQN_NNtH4","expires":1382387566490}

        JavaScriptSerializer js = new JavaScriptSerializer();

        //Token oAuth2Token = js.Deserialize<Token>(responseData);
        Token agsToken = js.Deserialize<Token>(agsTokenData);

        //set cache item to expire 2 minutes before token expiration (usually 2 hours)
        //expiration=524160 (364 days)
        HttpRuntime.Cache.Insert(
            "AGS_Token",
            agsToken.token,
            null,
            Cache.NoAbsoluteExpiration,
            new TimeSpan(363, 23, 58, 0),
            CacheItemPriority.Default,
            new CacheItemRemovedCallback(ReportRemovedAGSTokenCallback));

        return agsToken.token;
    }

    public static String GetAGOToken()
    {
        //testing
        string myToken = HttpRuntime.Cache["AGO_Token"] as string;
        if (string.IsNullOrEmpty(myToken))
        {
            myToken = GenerateAGOToken();
        }

        return myToken;
    }

    public static void ReportRemovedAGOTokenCallback(String key, object value,
        System.Web.Caching.CacheItemRemovedReason removedReason)
    {
        GenerateAGOToken();
    }

    public static string GenerateAGOToken()
    {
        string postData = string.Format("username={0}&password={1}&referer=https://www.arcgis.com&expiration=524160", agoUser, agoPassword);

        string agoTokenData = DoPostForString(agoTokenService, postData);

        if (agoTokenData.ToLower().Contains("error"))
        {
            //_log.ErrorFormat("Error Retrieving Token: POSTDATA: {0} / RESPONSEDATA: {1}", postData, agoTokenData);
            return "";
        }

        JavaScriptSerializer js = new JavaScriptSerializer();

        Token agoToken = js.Deserialize<Token>(agoTokenData);

        //set cache item to expire 2 minutes before token expiration (usually 2 hours)
        HttpRuntime.Cache.Insert(
            "AGO_Token",
            agoToken.token,
            null,
            Cache.NoAbsoluteExpiration,
            new TimeSpan(23, 58, 0),
            CacheItemPriority.Default,
            new CacheItemRemovedCallback(ReportRemovedAGOTokenCallback));

        return agoToken.token;
    }

    public static string DoPostForString(string url, string postData)
    {
        // create the POST request
        HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
        webRequest.Method = "POST";
        webRequest.ContentType = "application/x-www-form-urlencoded";
        webRequest.ContentLength = postData.Length;

        // POST the data
        using (StreamWriter requestWriter2 = new StreamWriter(webRequest.GetRequestStream()))
        {
            requestWriter2.Write(postData);
        }

        //  This actually does the request and gets the response back
        HttpWebResponse resp = (HttpWebResponse)webRequest.GetResponse();

        string responseData = string.Empty;

        using (StreamReader responseReader = new StreamReader(webRequest.GetResponse().GetResponseStream()))
        {
            // dumps the HTML from the response into a string variable
            responseData = responseReader.ReadToEnd();
        }

        return responseData;
    }

    //this is for more asyn
    public void DoPostForStringInsert(string url, string postData)
    {
        // create the POST request
        HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
        webRequest.Method = "POST";
        webRequest.ContentType = "application/x-www-form-urlencoded";
        webRequest.ContentLength = postData.Length;

        // POST the data
        using (StreamWriter requestWriter2 = new StreamWriter(webRequest.GetRequestStream()))
        {
            requestWriter2.Write(postData);
        }
        

        //  This actually does the request and gets the response back
        //HttpWebResponse resp = (HttpWebResponse)webRequest.GetResponse();
        
        //string responseData = string.Empty;

        //using (StreamReader responseReader = new StreamReader(webRequest.GetResponse().GetResponseStream()))
        //{
        //    // dumps the HTML from the response into a string variable
        //    responseData = responseReader.ReadToEnd();
        //}

        //return responseData;
    }
    

    //insert features (layer ID, feature JSON)
    public void InsertFeatures(string layerID, string features, string agoToken)
    {
        string token = "";
        //get fs URL from config
        if (publishMode.Equals("ago"))
        {
            if (String.IsNullOrEmpty(agoToken))
            {
                //TEST: IF NO AGOTOKEN SENT IN, CREATE ONE
                token = GetAGOToken();
                if (string.IsNullOrEmpty(token))
                {
                    throw new WebException("No AGO token available; Tried to generate token but failed.", WebExceptionStatus.TrustFailure);
                }
            }
            else
            {
                token = agoToken;
            }
        }
        else
        {
            //get ags token
            string agsToken = GetAGSToken();
            if (string.IsNullOrEmpty(agsToken))
            {
                throw new WebException("No ArcGIS Server token available", WebExceptionStatus.TrustFailure);
            }
            token = agsToken;
        }

        string responseString = "";
        string postUrl = string.Format("{0}/{1}/addFeatures?token={2}", urlOilMapFeatureService, layerID,token);
        //string postUrl = string.Format("{0}/{1}/addFeatures?", urlOilMapFeatureService, layerID);
        string postData = string.Format("f=json&features={0}", features);

        //call insert features on fs
        try
        {
            //responseString = DoPostForString(string.Concat(postUrl, token), postData);
            //DoPostForStringInsert(string.Concat(postUrl, token), postData);
            DoPostForStringInsert(postUrl, postData);
            //WHILE EXPLORING BUG OF INVALID TOKENS, ASSUMING ALL ERRORS ARE TOKEN RELATED AND FOR NOW, 
            //REGENERATING TOKEN REGARDLESS OF UNDERLYING CAUSE; SEND REST BACK TO CLIENT
            if (responseString.ToLower().IndexOf("error") > -1)
            {
               // _log.Error("Caught error in response: " + responseString);

                //token in cache is invalid... regenerate and store in cache
                if (publishMode.Equals("ago"))
                {
                    //use AGO admin credentials to generate new token
                    token = GenerateAGOToken();
                }
                else
                {
                    token = GenerateAGSToken();
                }
                //_log.Error("Caught invalid token error; generated new token: " + token);

                //try again
                //responseString = DoPostForString(string.Concat(postUrl, token), postData);
                DoPostForStringInsert(string.Concat(postUrl, token), postData);
            }
        }
        catch (Exception ex)
        {
            responseString = "error"; // LogExceptionReturnJSON(500, ex.Message, ex.StackTrace);
        }
        //return responseString;
    }
}