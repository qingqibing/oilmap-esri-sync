using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.IO;
using System.Net;
using System.Globalization;
using System.Runtime.InteropServices;
using System.Xml;
using System.Diagnostics;
using Microsoft.Win32;


public partial class _Default : System.Web.UI.Page
{
    #region Private Members
    //Engines

    /// <summary>
    /// Aggregator Engine
    /// Handles the aggregation of wind and current files
    /// </summary>
    private AggregatorEngine _AggEngine;
    /// <summary>
    /// Model processor takes input data and runs the model
    /// </summary>
    private ModelProcessor _ModelProcessor;

    //Model Variables
    private string _FileName;

    //QueryString Values
    private string _sWebPath;
    private string _sCaseName;
    private ModelType _eModelType;
    private string _sLocation;
    private string _sCurrentsPrefix;
    private string _sWindsPrefix;
    private DateTime _StartDate;
    private DateTime _EndDate;
    private int _Duration;
    private int _SimLength;
    private LatLon _IncidentSite;
    private BoundingBox _AOI;
    private int _Winds;
    private int _Currents;
    private string _EcopWinds;
    private string _EcopCurrents;
    private double _WindMag;
    private double _WindDir;
    private double _CurrMag;
    private double _CurrDir;
    private bool _bIsRivers;
    private bool _ModelMethod;
    private int _OilUnits;
    private int _SpillAmount;
    private double _WaterTemp;
    public string _ClientKey;
    public bool _AddToDB;
    public bool _EvapOn;
    public bool _EntrainOn;
    private string _groupIDShare;
    private string _scriptID;
    private string _description;
    private string _ShareEveryone;

    //XP added
    private double _AirTemp = 15;
    private int _ModelStep;
    private int _OutputInterval;
    private string _PostGISconn;
    private string _User_id;

    //Oil Specific
    private string _OilType;
    
    //Chem Specific
    private string _ChemType;

    //Output
    private string _OutputFile;

    private const int m_cNowcasting = -2;
    private const int m_cConstant = -1;
    private const int m_cLocal = 0;
    private const int m_cNoData = -999;

    public enum Platform
    {
        X86,
        X64,
        Unknown
    }

    internal const ushort PROCESSOR_ARCHITECTURE_INTEL = 0;
    internal const ushort PROCESSOR_ARCHITECTURE_IA64 = 6;
    internal const ushort PROCESSOR_ARCHITECTURE_AMD64 = 9;
    internal const ushort PROCESSOR_ARCHITECTURE_UNKNOWN = 0xFFFF;

    [DllImport("kernel32.dll")]
    internal static extern void GetNativeSystemInfo(ref SYSTEM_INFO lpSystemInfo);

    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);

    [DllImport("psapi.dll")]
    static extern uint GetModuleFileNameEx(IntPtr hProcess, IntPtr hModule, [Out] System.Text.StringBuilder lpBaseName, [In] [MarshalAs(UnmanagedType.U4)] int nSize);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CloseHandle(IntPtr hObject);

    [StructLayout(LayoutKind.Sequential)]
    internal struct SYSTEM_INFO
    {
        public ushort wProcessorArchitecture;
        public ushort wReserved;
        public uint dwPageSize;
        public IntPtr lpMinimumApplicationAddress;
        public IntPtr lpMaximumApplicationAddress;
        public UIntPtr dwActiveProcessorMask;
        public uint dwNumberOfProcessors;
        public uint dwProcessorType;
        public uint dwAllocationGranularity;
        public ushort wProcessorLevel;
        public ushort wProcessorRevision;
    };

    #endregion
    
    protected void Page_Load(object sender, EventArgs e)
    {
        //Path Settings
        if (Request.QueryString.Count == 0)
            Response.Redirect("RunModel.aspx?CaseName=SAMPLE_TEST3&ClientKey=W00ds1de337&ModelType=OILSPILL&StartDate=20170511T12:00:00&simLength=24&WaterTemp=72.6F&IncLat=33.856999&IncLon=-118.541794&Winds=390&Currents=765&EcopWinds=GFS_WINDS&EcopCurrents=HYCOM_global_Navy_currents&Duration=6&Location=WORLD&&Volume=1000&group=7f22adb83ed7431f824df84a41a7f038&every1share=true&OilType=Heavy%20Crude%20Oil&OilUnits=5&FullPath=true&scriptid=Model2Shape&description=test");
        _sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        _OutputFile = "ERROR: an unknown error has occured in Page_Load";
        
        double timeout = Convert.ToDouble(System.Configuration.ConfigurationManager.AppSettings["ProccessTimeout"]);

        //Parse the Query String
        string qsProcessed = processQueryString();
        if(qsProcessed != "")
        {
            Response.Write(qsProcessed);
            return;
        }

        if (!(Directory.Exists(_sWebPath + "\\ModelData\\LogFile")))
            Directory.CreateDirectory(_sWebPath + "\\ModelData\\LogFile");

        using (StreamWriter sw = new StreamWriter(_sWebPath + "\\ModelData\\LogFile\\LogFile.txt", true))
        {
            sw.WriteLine(String.Format("{0},{1},{2}", DateTime.Now.ToString(), HttpContext.Current.Request.ServerVariables["REMOTE_ADDR"], Request.QueryString.ToString()));
        }

        string sOutputPath = "\\ModelData\\" + _sLocation;
        CheckOutputPath(_sWebPath + sOutputPath);

        string sPrefixFile = _sWebPath + sOutputPath + "\\Winds\\Prefix.txt";
        _sWindsPrefix = "";
        if (File.Exists(sPrefixFile))
            _sWindsPrefix = File.ReadAllText(sPrefixFile);  //System.Configuration.ConfigurationManager.AppSettings["WindFilePrefix"];

        sPrefixFile = _sWebPath + sOutputPath + "\\Currents\\CurrentsPrefix.txt";
        _sCurrentsPrefix = "";
        if (File.Exists(sPrefixFile))
            _sCurrentsPrefix = File.ReadAllText(sPrefixFile); //System.Configuration.ConfigurationManager.AppSettings["CurrentFilePrefix"];

        if (_bIsRivers)
        {
            sPrefixFile = _sWebPath + sOutputPath + "\\Currents\\RiverPrefix.txt";
            if (File.Exists(sPrefixFile))
                _sCurrentsPrefix = File.ReadAllText(sPrefixFile); //System.Configuration.ConfigurationManager.AppSettings["RiverCurrentFilePrefix"];
        }
        
        //Set up the aggregator
        EDSProcessor myProcessor = new EDSProcessor();

        string windsStat = "";

        if (_Winds == m_cLocal)
        {
            //Process the winds
            _AggEngine = new AggregatorEngine(_Winds, _StartDate, _EndDate, _AOI, _sWebPath, _sWebPath + sOutputPath + "\\WINDS\\", _bIsRivers);
            windsStat = _AggEngine.getWinds(_sWindsPrefix, _FileName);
            if (windsStat.Contains("ERROR"))
            {
                Response.Write(windsStat + " WINDS");
                return;
            }
        }
        else if (_Winds == m_cConstant)
        {
            windsStat = _sWebPath + sOutputPath + "\\WINDS\\" + _FileName + ".WNE";
            CreateWNEFile(windsStat, _WindMag, _WindDir);
        }
        else if (_Winds != m_cNoData) //EDS Winds
        {
            string sFilename = myProcessor.GetDataFile(_ClientKey, _Winds, _StartDate, _EndDate, _AOI);
            string sResult = myProcessor.GetStatus(sFilename);
            if (sResult == "COMPLETE")
            {
                string sOutFilename = _sWebPath + sOutputPath + "\\winds\\" + _FileName + ".NC";
                myProcessor.DownloadDataFile(sOutFilename, sFilename);
                windsStat = sOutFilename;
            }
            else
                windsStat = sResult;

            if (!(File.Exists(windsStat)))
                windsStat = "";
        }
        
        _AggEngine = null;

        //Process the currents
        string currStat = "";
        if (_Currents == m_cLocal)
        {
            if (_sCurrentsPrefix.ToUpper().Contains("STATIC"))
            {
                string[] sSplit = _sCurrentsPrefix.Split(new char[] { '-' });
                currStat = _sWebPath + sOutputPath + "\\Currents\\" + sSplit[1];
            }
            else
            {
                string currentsDataPath = _sWebPath;
                _AggEngine = new AggregatorEngine(_Currents, _StartDate, _EndDate, _AOI, _sWebPath, _sWebPath + sOutputPath + "\\Currents\\", _bIsRivers);
                currStat = _AggEngine.getCurrents(_sCurrentsPrefix, _FileName);
                if (currStat.Contains("ERROR"))
                {
                    Response.Write(currStat + " CURRENTS");
                    return;
                }
            }
        }
        else if (_Currents == m_cConstant)
        {
            currStat = "";
        }
        else if (_Currents != m_cNoData)
        {
            string sFilename = myProcessor.GetDataFile(_ClientKey, _Currents, _StartDate, _EndDate, _AOI);
            string sResult = myProcessor.GetStatus(sFilename);
            if (sResult == "COMPLETE")
            {
                string sOutFilename = _sWebPath + sOutputPath + "\\currents\\" + _FileName + ".NC";
                myProcessor.DownloadDataFile(sOutFilename, sFilename);
                currStat = sOutFilename;
            }
            else
                currStat = sResult;

            if (!(File.Exists(currStat)))
                currStat = "";
        }

        //Run the model
        _ModelProcessor = new ModelProcessor(_eModelType, timeout);
        if (_eModelType == ModelType.OilModel)
        {
            OilInputData oilInput = new OilInputData(_sWebPath, _sLocation);
            oilInput.bBox = _AOI;
            oilInput.caseName = _sCaseName;
            oilInput.incidentSite = _IncidentSite;
            oilInput.start = _StartDate;
            oilInput.end = _EndDate;
            oilInput.currentFile = currStat;
            oilInput.windsFile = windsStat;
            oilInput.ecopCurrents = _EcopCurrents;
            oilInput.ecopWinds = _EcopWinds;
            oilInput.fileName = _FileName;
            oilInput.spillDuration = _Duration;
            oilInput.SpillAmount = _SpillAmount;
            oilInput.SpillUnits = _OilUnits;
            oilInput.WaterTemp = _WaterTemp;
            oilInput.evaporationOn = _EvapOn ? 0 : -1;
            oilInput.entrainOn = _EntrainOn ? 0 : -1;
            // xp added
            oilInput.outputInterval = _OutputInterval;
            oilInput.modelStep = _ModelStep;
            oilInput.groupID = _groupIDShare;
            oilInput.every1 = _ShareEveryone;
            oilInput.description = _description;

            if (_ModelMethod) //fast
                oilInput.timeStep = 60;
            else //comprehensive
                oilInput.timeStep = 10;

            if (_Currents == m_cConstant)
            {
                oilInput.CurrMag = _CurrMag;
                oilInput.CurrDir = _CurrDir;
            }
            else
            {
                oilInput.CurrMag = -999;
                oilInput.CurrDir = -999;
            }

            oilInput.oilType = _OilType;
            /*if ((_Currents > 0) || (_Winds > 0))
            {
                oilInput.coastLineFile = Path.GetDirectoryName(oilInput.coastLineFile) + "\\LANDPOLY.BDM";
            }*/
            _OutputFile = _ModelProcessor.runOilModel(oilInput);
        }

        if (_eModelType == ModelType.ChemModel)
        {
            ChemInputData chemInput = new ChemInputData(_sWebPath, _sLocation);
            chemInput.bBox = _AOI;
            chemInput.caseName = _sCaseName;
            chemInput.incidentSite = _IncidentSite;
            chemInput.start = _StartDate;
            chemInput.end = _EndDate;
            chemInput.currentFile = currStat;
            chemInput.windsFile = windsStat;
            chemInput.fileName = _FileName;
            chemInput.chemType = _ChemType;
            chemInput.spillDuration = _Duration;
            chemInput.ModelMethod = _ModelMethod;
            /*if ((_Currents > 0) || (_Winds > 0))
                chemInput.coastLineFile = Path.GetDirectoryName(chemInput.coastLineFile) + "\\LANDPOLY.BDM";*/
            _OutputFile = _ModelProcessor.runChemModel(chemInput);
        }

        //Rout the output to the user
        if (_OutputFile == "")
            Response.Write("ERROR: An error occurred while running the model.");
        else if (_OutputFile.Contains("ERROR:"))
            Response.Write(_OutputFile);
        else
        {
            if (Request.QueryString["FullPath"] != null)
                if (Request.QueryString["FullPath"] == "true")
                    
                    Response.Write("\\\\" + Environment.MachineName + "\\" + _sWebPath.Remove(0, 3) + sOutputPath + "\\Outdata\\" + _FileName + ".INP");
                else
                    Response.Write(_OutputFile);
            else
                //Response.Write("\\\\" + Environment.MachineName + "\\" + _sWebPath.Remove(0, 3) + sOutputPath + "\\Outdata\\" + _OutputFile + ".INP");
                Response.Write(_OutputFile);

            //if (_AddToDB)
              //  AddScenarioToDatabase();
        }
        
        //testing with hardcoded version
        //string testCommand = @"F:\groups\rps_data\code\ds_oilmapweb\SyncModelRun\Push2ESRI\Model2Shape_v6.py " + @"F:\groups\rps_data\code\ds_oilmapweb\SyncModelRun\ModelData\WORLD\Outdata\SAMPLE_TEST_109_87799.inp F:\groups\rps_data\code\ds_oilmapweb\SyncModelRun\ModelData";
        
        //convert the oilmap format to geodatabase
        string fileNameINP = _sWebPath + "\\" + sOutputPath + "\\Outdata\\" + _FileName + ".INP";

        //_sCaseName
        //_StartDate
        //_SpillAmount
        //_OilType
        //_OilUnits
        //_SimLength

        TimeSpan t = _StartDate - new DateTime(1970, 1, 1);
        int secondsSinceEpoch = (int)t.TotalSeconds;

        string pyCommandInput = _sWebPath + @"\Push2ESRI\"+ _scriptID + ".py " + fileNameINP + " "+ _sCaseName + " " + secondsSinceEpoch + " " + _SimLength+ " " + _SpillAmount+ " " + _OilUnits+ " \"" + _OilType+ "\"" + " \"" + _description + "\"";


        string sPythonPath = "";
        string sArcVersion = "10.3";

        Platform myPlatform = GetPlatform();
        switch (myPlatform)
        {
            case Platform.X64:
                sPythonPath = (string)Registry.GetValue("HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\ESRI\\Python" + sArcVersion, "PythonDir", "");
                break;
            default:
                sPythonPath = (string)Registry.GetValue("HKEY_LOCAL_MACHINE\\SOFTWARE\\ESRI\\Python" + sArcVersion, "PythonDir", "");
                break;
        }

        //this may be in a different location so best to check all enviormental variables are correct
        string pyLoc = "\"" + sPythonPath + "ArcGIS" + sArcVersion + "\\python.exe\"";
        //string pyLoc = @"C:\Python27\ArcGISx6410.5\python.exe";  //for deploy on server

        Push2ESRI(pyLoc, pyCommandInput);
    }

    private void Push2ESRI(string pyLocation, string sScenarioINP)
    {
        //string sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        Process modelProcess = new Process();
        modelProcess.StartInfo.FileName = pyLocation;
        modelProcess.StartInfo.CreateNoWindow = false;
        modelProcess.StartInfo.UseShellExecute = false;
        modelProcess.StartInfo.RedirectStandardOutput = true;
        modelProcess.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
        modelProcess.StartInfo.ErrorDialog = false;
        modelProcess.StartInfo.Arguments = sScenarioINP;

        modelProcess.Start();

        System.IO.StreamReader sr = modelProcess.StandardOutput;
        string tmp;
        while ((tmp = modelProcess.StandardOutput.ReadLine()) != null)
        {
            Response.Write("\n"+tmp);
        };

        //this will create the webmap id
        //OilModelEngine.CreateWebMap()

        //this will share the item with others in the group or orgainization 
        //OilModelEngine.ShareItem()

        modelProcess.WaitForExit();
    }

    public static Platform GetPlatform()
    {
        SYSTEM_INFO sysInfo = new SYSTEM_INFO();
        GetNativeSystemInfo(ref sysInfo);

        switch (sysInfo.wProcessorArchitecture)
        {
            case PROCESSOR_ARCHITECTURE_AMD64:
                return Platform.X64;

            case PROCESSOR_ARCHITECTURE_INTEL:
                return Platform.X86;

            default:
                return Platform.Unknown;
        }
    }

    private void process_ErrorDataReceived(object sender, DataReceivedEventArgs e)
    {
        Console.WriteLine(e.Data);
    }

    private void AddScenarioToDatabase()
    {
        XmlDocument oDoc = new XmlDocument();
        XmlElement oRootNode = oDoc.CreateElement("Scenario");
        
        XmlElement oNode = oDoc.CreateElement("CaseName");
        oNode.InnerText = Path.GetFileNameWithoutExtension(_OutputFile);
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("StartDate");
        oNode.InnerText = _StartDate.ToString("yyyyMMddTHH:mm:ss");
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Duration");
        oNode.InnerText = _SimLength.ToString();
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Lat");
        oNode.InnerText = _IncidentSite.lat.ToString();
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Lon");
        oNode.InnerText = _IncidentSite.lon.ToString();
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("WaterTemp");
        oNode.InnerText = ((_WaterTemp * (9/5)) + 32).ToString();
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Path");
        oNode.InnerText = "\\\\" + Environment.MachineName + "\\" + _sWebPath.Remove(0, 3) + "\\ModelData\\" + _sLocation + "\\Outdata\\" + _OutputFile + ".INP";
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Location");
        oNode.InnerText = _sLocation;
        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("Environments");
        XmlElement oNode2 = oDoc.CreateElement("Environment");
        XmlElement oNode3 = oDoc.CreateElement("SourceName");
        switch (_Winds)
        {
            case -999:
                oNode3.InnerText = "NONE";
                break;
            case -2:
                oNode3.InnerText = "NOWCASTING";
                break;
            case -1:
                oNode3.InnerText = "MANUAL";
                break;
            case -3:
                oNode3.InnerText = "CDE";
                break;
            default:
                oNode3.InnerText = "EDS";
                break;
        }

        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Type");
        oNode3.InnerText = "W";
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Speed");
        oNode3.InnerText = _WindMag.ToString();
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Direction");
        if (Request.QueryString["WindDir"] != null)
            oNode3.InnerText = Request.QueryString["WindDir"];
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("EnvType");
        oNode3.InnerText = _Winds.ToString();
        oNode2.AppendChild(oNode3);

        oNode.AppendChild(oNode2);

        oNode2 = oDoc.CreateElement("Environment");
        oNode3 = oDoc.CreateElement("SourceName");
        switch (_Winds)
        {
            case -999:
                oNode3.InnerText = "NONE";
                break;
            case -2:
                oNode3.InnerText = "NOWCASTING";
                break;
            case -1:
                oNode3.InnerText = "MANUAL";
                break;
            case -3:
                oNode3.InnerText = "CDE";
                break;
            default:
                oNode3.InnerText = "EDS";
                break;
        }

        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Type");
        oNode3.InnerText = "C";
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Speed");
        oNode3.InnerText = _CurrMag.ToString();
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("Direction");
        if (Request.QueryString["CurrDir"] != null)
            oNode3.InnerText = Request.QueryString["CurrDir"];
        oNode2.AppendChild(oNode3);

        oNode3 = oDoc.CreateElement("EnvType");
        oNode3.InnerText = _Currents.ToString();
        oNode2.AppendChild(oNode3);

        oNode.AppendChild(oNode2);

        oRootNode.AppendChild(oNode);

        oNode = oDoc.CreateElement("OilInfo");

        oNode2 = oDoc.CreateElement("OilType");
        oNode2.InnerText = _OilType;
        oNode.AppendChild(oNode2);

        oNode2 = oDoc.CreateElement("Amount");
        oNode2.InnerText = _SpillAmount.ToString();
        oNode.AppendChild(oNode2);

        oNode2 = oDoc.CreateElement("ReleaseDuration");
        oNode2.InnerText = _Duration.ToString();
        oNode.AppendChild(oNode2);

        oNode2 = oDoc.CreateElement("AmountUnits");
        switch (_OilUnits)
        {
            case 1:
                oNode2.InnerText = "Liters";
                break;
            case 2:
                oNode2.InnerText = "Gallons";
                break;
            case 3:
                oNode2.InnerText = "Cubic Meters";
                break;
            case 4:
                oNode2.InnerText = "Tonnes";
                break;
            case 5:
                oNode2.InnerText = "Barrels";
                break;
            case 6:
                oNode2.InnerText = "Pounds";
                break;
            case 7:
                oNode2.InnerText = "Kilograms";
                break;
        }
        oNode.AppendChild(oNode2);

        oRootNode.AppendChild(oNode);

        oDoc.AppendChild(oRootNode);
        
        //dsOilmap.dsOILMAP myDsOilmap = new dsOilmap.dsOILMAP();
        //myDsOilmap.CreateScenario(_ClientKey, oDoc.OuterXml);

        //Response.Write(myDsOilmap.GetScenarios(_ClientKey));
        
    }

    private void CheckOutputPath(string sOutputPath)
    {
        if (!(Directory.Exists(sOutputPath)))
        {
            Directory.CreateDirectory(sOutputPath);
            Directory.CreateDirectory(sOutputPath + "\\Coast");
            Directory.CreateDirectory(sOutputPath + "\\Currents");
            Directory.CreateDirectory(sOutputPath + "\\Fates");
            Directory.CreateDirectory(sOutputPath + "\\Oil");
            Directory.CreateDirectory(sOutputPath + "\\Outdata");
            Directory.CreateDirectory(sOutputPath + "\\Rundata");
            Directory.CreateDirectory(sOutputPath + "\\Winds");

            string sNewPath = Path.GetDirectoryName(sOutputPath);

            if (File.Exists(sNewPath + "\\BaseFiles\\oildata.lst"))
                File.Copy(sNewPath + "\\BaseFiles\\oildata.lst", sOutputPath + "\\Oil\\oildata.lst");

            if (File.Exists(sNewPath + "\\BaseFiles\\oilmap_basemap.shp"))
                File.Copy(sNewPath + "\\BaseFiles\\oilmap_basemap.shp", sOutputPath + "\\Coast\\oilmap_basemap.shp");

            if (File.Exists(sNewPath + "\\BaseFiles\\Default.inp"))
                File.Copy(sNewPath + "\\BaseFiles\\Default.inp", sOutputPath + "\\Rundata\\Default.inp");

            if (File.Exists(sNewPath + "\\BaseFiles\\shr_char.def"))
                File.Copy(sNewPath + "\\BaseFiles\\shr_char.def", sOutputPath + "\\Coast\\shr_char.def");
        }
    }

    private void CreateWNEFile(string sFilename, double iMagnitude, double dDirection)
    {
        short iU, iV;
        iU = (short)((iMagnitude * 51.4444444) * Math.Cos((90 - dDirection) * (Math.PI / 180))); //convert to cm/s first
        iV = (short)((iMagnitude * 51.4444444) * Math.Sin((90 - dDirection) * (Math.PI / 180)));

        using (BinaryWriter binWriter = new BinaryWriter(File.Open(sFilename, FileMode.Create)))
        {
            DateTime baseDate = new DateTime(1979, 12, 31); 
            DateTime myTime = _StartDate;
            while (myTime <= _EndDate)
            {
                TimeSpan mySpan = myTime.Subtract(baseDate);
                int myLongTime = (int)mySpan.TotalMinutes;
                binWriter.Write(myLongTime);
                binWriter.Write(iU);
                binWriter.Write(iV);
                myTime = myTime.AddHours(1);
            }
        }

        string sWNLFile = Path.ChangeExtension(sFilename, ".WNL");
        using (StreamWriter outfile = new StreamWriter(sWNLFile))
        {
            outfile.WriteLine(_IncidentSite.lon.ToString() + " " + _IncidentSite.lat.ToString());
            outfile.WriteLine("");
        }

    }

    private string processQueryString()
    {
        string retval = "";
        _sCaseName = "";
        if (Request.QueryString["CaseName"] != null)
            _sCaseName = Request.QueryString["CaseName"];
        if (_sCaseName == "")
            retval = "ERROR: CaseName cannot be null\r\n";

        
        Random randomGen = new Random();
        DateTime dNow = DateTime.Now;
        string sNow = dNow.Millisecond.ToString();
        _FileName = _sCaseName + "_" + sNow + "_" + randomGen.Next(10000, 99999);

        string sModelType = "";
        if (Request.QueryString["ModelType"] != null)
            sModelType = Request.QueryString["ModelType"];

        _ShareEveryone = "false";
        if (Request.QueryString["every1share"] != null)
            _ShareEveryone = Request.QueryString["every1share"];

        switch(sModelType.ToUpper())
        {
            case "OILSPILL":
                _eModelType = ModelType.OilModel;
                break;
            case "CHEMSPILL":
                _eModelType = ModelType.ChemModel;
                break;
            default:
                retval += "ERROR: Unrecognized Model Type: " + sModelType + "\r\n";
                break;
        }

        string[] sDateFormats = new string[] {"yyyyMMddTHH:mm:ss", "yyyyMMddTHH:mm", 
                                            "MM/dd/yyyyTHH:mm:ss", "MM/dd/yyyyTHH:mm",
                                            "dd/MM/yyyyTHH:mm:ss", "dd/MM/yyyyTHH:mm"};

        if (Request.QueryString["StartDate"] != null)
        {
            if (!(DateTime.TryParseExact(Request.QueryString["StartDate"], sDateFormats, new CultureInfo("en-US"), System.Globalization.DateTimeStyles.None, out _StartDate)))
            {
                retval += "ERROR: StartDate is invalid: " + Request.QueryString["StartDate"] + "\r\n";
                retval += "Needs to be in one of the following formats:\r\n" + sDateFormats[0] + "r\n" +
                                                                               sDateFormats[1] + "\r\n" +
                                                                               sDateFormats[2] + "\r\n" +
                                                                               sDateFormats[3] + "\r\n" +
                                                                               sDateFormats[4] + "\r\n" +
                                                                               sDateFormats[5] + "\r\n";
            }
        }
        else
            retval += "ERROR: Start Date is missing.\r\n";

        _SpillAmount = 0;
        if (Request.QueryString["Volume"] != null)
            _SpillAmount = int.Parse(Request.QueryString["Volume"]);

        _OilUnits = 4; //default to Tonnes
        if (Request.QueryString["OilUnits"] != null)
            _OilUnits = int.Parse(Request.QueryString["OilUnits"]);

        _Duration = 0;
        if (Request.QueryString["Duration"] != null)
            _Duration = int.Parse(Request.QueryString["Duration"]);

        _SimLength = 24; //default to one day
        if (Request.QueryString["SimLength"] != null)
            _SimLength = int.Parse(Request.QueryString["SimLength"]);

        _EndDate = _StartDate.AddHours(_SimLength);

        _sLocation = "";
        if (Request.QueryString["Location"] != null)
            _sLocation = Request.QueryString["Location"];

        double lat = 0;
        if (Request.QueryString["IncLat"] != null)
            lat = Convert.ToDouble(Request.QueryString["IncLat"]);
        
        double lon = 0;
        if (Request.QueryString["IncLon"] != null)
            lon = Convert.ToDouble(Request.QueryString["IncLon"]);
        _IncidentSite = new LatLon(lat, lon);

        _AOI = CalculateAOI(_IncidentSite, _SimLength-6); // new BoundingBox(Request.QueryString["BBox"]);              

        _Winds = -999; //default to no winds
        if (Request.QueryString["Winds"] != null)
            _Winds = int.Parse(Request.QueryString["Winds"]);

        _Currents = -999; //default to no currents
        if (Request.QueryString["Currents"] != null)
            _Currents = int.Parse(Request.QueryString["Currents"]);

        _EcopWinds = "";
        if (Request.QueryString["EcopWinds"] != null)
            _EcopWinds = Request.QueryString["EcopWinds"];

        _EcopCurrents = "";
        if (Request.QueryString["EcopCurrents"] != null)
            _EcopCurrents = Request.QueryString["EcopCurrents"];

        _WindMag = 0;
        if (Request.QueryString["WindMag"] != null)
            _WindMag = Convert.ToDouble(Request.QueryString["WindMag"]);

        _WindDir = 0;
        if (Request.QueryString["WindDir"] != null)
        {
            string myDir = Request.QueryString["WindDir"];
            _WindDir = GetDirectionFromString(myDir) + 180; //to get into direction from
            if (_WindDir > 360)
                _WindDir -= 360;
        }

        _ModelStep = 60; //Default 60 mins   xp added
        if (Request.QueryString["ModelStep"] != null)
            _ModelStep = int.Parse(Request.QueryString["ModelStep"]);

        _OutputInterval = 60;  //default 60 mins  xp added
        if (Request.QueryString["OutputInterval"] != null)
            _OutputInterval = int.Parse(Request.QueryString["OutputInterval"]);

        _CurrMag = 0;
        if (Request.QueryString["CurrMag"] != null)
            _CurrMag = Convert.ToDouble(Request.QueryString["CurrMag"]);

        _groupIDShare= "62f6db44ba6d42a7b66334db5f0f0fe2";
        if (Request.QueryString["group"] != null)
            _groupIDShare = Request.QueryString["group"];

        _scriptID = "Model2Shape";
        if (Request.QueryString["scriptid"] != null)
            _scriptID = Request.QueryString["scriptid"];

        _description = "";
        if (Request.QueryString["description"] != null)
            _description = Request.QueryString["description"];

        _ShareEveryone = "false";
        if (Request.QueryString["every1share"] != null)
            _ShareEveryone = Request.QueryString["every1share"];

        _CurrDir = 0;
        if (Request.QueryString["CurrDir"] != null)
        {
            string myDir = Request.QueryString["CurrDir"];
            _CurrDir = GetDirectionFromString(myDir);
        }

        _OilType = "Diesel"; //default to Diesel
        if (Request.QueryString["OilType"] != null)
            _OilType = Request.QueryString["OilType"];

        _OilType = _OilType.Replace("%23", "#");

        _EvapOn = (_OilType.ToUpper() == "CONSERVATIVE TRACER");
        _EntrainOn = (_OilType.ToUpper() == "CONSERVATIVE TRACER");

        //_ChemType = "Benzene"; //default to benzene
        //if (Request.QueryString["ChemID"] != null)
        //    _ChemType = Request.QueryString["ChemID"];

        _bIsRivers = false;
        if (Request.QueryString["River"] != null)
            _bIsRivers = Convert.ToBoolean(Request.QueryString["River"]);

        _ModelMethod = true; //default to Fast method
        if (Request.QueryString["Speed"] != null)
            _ModelMethod = (Request.QueryString["Speed"].ToUpper() == "FAST");

        string sWaterTemp = "15C";
        if (Request.QueryString["WaterTemp"] != null)
            sWaterTemp = Request.QueryString["WaterTemp"];

        _WaterTemp = double.Parse(sWaterTemp.Substring(0, sWaterTemp.Length - 1));
        if (sWaterTemp.Substring(sWaterTemp.Length - 1, 1) == "F")
            _WaterTemp = (_WaterTemp - (double)32) * (double)(5.0 / 9.0);

        _ClientKey = "";
        if (Request.QueryString["ClientKey"] != null)
            _ClientKey = Request.QueryString["ClientKey"];

        _AddToDB = false;
        if (Request.QueryString["AddToDatabase"] != null)
            _AddToDB = bool.Parse(Request.QueryString["AddToDatabase"]);
        
        return retval;
    }

    private double GetDirectionFromString(string sDirection)
    {
        double Result = 0;
        switch (sDirection.ToUpper())
        {
            case "N":
                Result = 0;
                break;
            case "NNE":
                Result = 22.5;
                break;
            case "NE":
                Result = 45;
                break;
            case "ENE":
                Result = 67.5;
                break;
            case "E":
                Result = 90;
                break;
            case "ESE":
                Result = 112.5;
                break;
            case "SE":
                Result = 135;
                break;
            case "SSE":
                Result = 157.5;
                break;
            case "S":
                Result = 180;
                break;
            case "SSW":
                Result = 202.5;
                break;
            case "SW":
                Result = 225;
                break;
            case "WSW":
                Result = 247.5;
                break;
            case "W":
                Result = 270;
                break;
            case "WNW":
                Result = 292.5;
                break;
            case "NW":
                Result = 315;
                break;
            case "NNW":
                Result = 337.5;
                break;
        }
        return Result;
    }

    private BoundingBox CalculateAOI(LatLon pIncidentSite, double dSpillDuration)
    {
        BoundingBox Result = new BoundingBox();
        double dMidLat = pIncidentSite.lat;
        double dLongitude, dLatitude;
        Meters2LonLat(3000, dMidLat, out dLongitude, out dLatitude);
        double xDiff = dSpillDuration * dLongitude;
        //Trying to Shrink the Data!!
        if (xDiff < 0.25)
            xDiff = 0.25;
        double yDiff = dSpillDuration * dLatitude;
        if (yDiff < 0.25)
            yDiff = 0.25;
        //xDiff = .30;
        //yDiff = .30;
        Result.west = pIncidentSite.lon - xDiff;
        Result.east = pIncidentSite.lon + xDiff;
        Result.north = pIncidentSite.lat + yDiff;
        Result.south = pIncidentSite.lat - yDiff;

        return Result;
    }

    private void Meters2LonLat(double dMeters, double dMidLat, out double dLongitude, out double dLatitude)
    {
        const double ERADIUS = 6371100;
        double meters_lat, meters_lng;

        meters_lat = 2 * Math.PI * ERADIUS / 360;
        meters_lng = meters_lat * Math.Cos(dMidLat * (Math.PI / 180));

        dLongitude = dMeters / meters_lng;
        dLatitude = dMeters / meters_lat;
    }
}
