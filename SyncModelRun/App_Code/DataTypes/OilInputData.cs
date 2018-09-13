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
using System.Globalization;

/// <summary>
/// Summary description for OilInputData
/// </summary>
public class OilInputData:InputData
{
    #region Private Members
    //Paths
    private string _IniPath;
    private string _InpPath;
    private string _OutputLocation;
    private string _RunLocation;
    private string _WindLocation;
    private string _CurrentLocation;
    private string _EXEPath;
    private string _OilInfoLocation;

    //File Names
    private string _INPFileName;
    private string _INIFileName;

    //Oil Model Info
    private string _Scenario;
    private DateTime _SpillTime;

    private string _OilType;
    private double _OilDensity;
    private double _OilSurfaceTension;
    private double _OilViscosity;
    private double _OilEvapConstantA;
    private double _OilEvapConstantB;
    private double _OilInitialBoilingPoint;
    private double _OilMinimumThickness;
    private double _OilGradient;
    private int _OilAmount;
    private int _OilUnits;
    private double _SpillDuration;
    private double _DeltaT;
    private bool _ModelMethod;
    private string _groupId;
    private string _every1;
    private string _descript;

    private double _CurrMag;
    private double _CurrDir;

    private double _WindMag;
    private double _WindDir;

    private double _WaterTemp;

    //XP added 
    private int _OutputInterval;
    private int _ModelStep;  //should be same as DeltaT
    private string _PostGISconn;

    private int _EvapOn;
    private int _EntrainOn;
    #endregion

    #region Public Properties
    public int outputInterval
    {
        get { return _OutputInterval; }
        set { _OutputInterval = value; }
    }

    public int modelStep
    {
        get { return _ModelStep; }
        set { _ModelStep = value; }
    }

    public string postGISconn
    {
        get { return _PostGISconn; }
        set { _PostGISconn = value; }
    }
    //Paths (READ ONLY)
    public string exePath
    {
        get { return _EXEPath; }
    }
    public string iniPath
    {
        get { return _IniPath; }
    }
    public string inpPath
    {
        get { return _InpPath; }
    }
    public string outputPath
    {
        get { return _OutputLocation; }
    }
    public string runPath
    {
        get { return _RunLocation; }
    }
    public string windLocation
    {
        get { return _WindLocation; }
    }
    public string currentLocation
    {
        get { return _CurrentLocation; }
    }

    //FileNames
    public string inpFileName
    {
        get { return _INPFileName; }
        set { _INPFileName = value; }
    }
    public string iniFileName
    {
        get { return _INIFileName; }
        set { _INIFileName = value; }
    }

    //Oil Model Info
    public string scenario
    {
        get { return _Scenario; }
        set { _Scenario = value; }
    }
    public string groupID
    {
        get { return _groupId; }
        set { _groupId = value; }
    }
    public string every1
    {
        get { return _every1; }
        set { _every1 = value; }
    }
    public string description
    {
        get { return _descript; }
        set { _descript = value; }
    }
    public double spillLat
    {
        get { return _IncidentSite.lat; }
        set { _IncidentSite.lat = value; }
    }
    public double spillLon
    {
        get { return _IncidentSite.lon; }
        set { _IncidentSite.lon = value; }
    }
    public DateTime spillTime
    {
        get { return _SpillTime; }
        set { _SpillTime = value; }
    }
    public string spillTime1
    {
        get
        {
            return _StartDate.Year.ToString() + " " + _StartDate.Month.ToString() + " " + _StartDate.Day.ToString() + " " + _StartDate.Hour.ToString() + " " + _StartDate.Minute.ToString();
        }
    }
    public string splon1
    {
        get { return _IncidentSite.lon.ToString(CultureInfo.CreateSpecificCulture("en-US")); }
        set { _IncidentSite.lon = Convert.ToDouble(value); }
    }
    public string splat1
    {
        get { return _IncidentSite.lat.ToString(CultureInfo.CreateSpecificCulture("en-US")); }
        set { _IncidentSite.lat = Convert.ToDouble(value); }
    }
    public double timeStep
    {
        get { return _DeltaT; }
        set { _DeltaT = value; }
    }
    public double simulationLength
    {
        get
        {
            TimeSpan ts = new TimeSpan(_EndDate.Ticks - _StartDate.Ticks);
            return (double)ts.TotalHours;
        }
    }
    public string oilType
    {
        get { return _OilType; }
        set
        {
            _OilType = value;
            _OilDensity = GetOilDensity(1);
            _OilSurfaceTension = GetOilDensity(3);
            _OilViscosity= GetOilDensity(2);
            _OilEvapConstantA = GetOilDensity(7);
            _OilEvapConstantB=GetOilDensity(8);
            _OilInitialBoilingPoint=GetOilDensity(5);
            _OilMinimumThickness=GetOilDensity(9);
            _OilGradient = GetOilDensity(6);
        }
    }
    public double oilDensity
    {
        get { return _OilDensity; }
    }
    public double oilSurfaceTension
    {
        get { return _OilSurfaceTension; }
    }
    public double oilViscosity
    {
        get { return _OilViscosity; }
    }
    public double oilEvapConstantA
    {
        get { return _OilEvapConstantA; }
    }
    public double oilInitialBoilingPoint
    {
        get { return _OilInitialBoilingPoint; }
    }
    public double oilEvapConstantB
    {
        get { return _OilEvapConstantB; }
    }
    public double oilMinimumThickness
    {
        get { return _OilMinimumThickness; }
    }
    public double oilGradient
    {
        get { return _OilGradient; }
    }
    public double spillDuration
    {
        get { return _SpillDuration; }
        set { _SpillDuration = value; }
    }
    public int SpillAmount
    {
        get { return _OilAmount; }
        set { _OilAmount = value; }
    }
    public bool ModelMethod
    {
        get { return _ModelMethod; }
        set { _ModelMethod = value; }
    }
    public int SpillUnits
    {
        get { return _OilUnits; }
        set { _OilUnits = value; }
    }

    public double CurrMag
    {
        get { return _CurrMag; }
        set { _CurrMag = value; }
    }

    public double CurrDir
    {
        get { return _CurrDir; }
        set { _CurrDir = value; }
    }

    public double WindMag
    {
        get { return _WindMag; }
        set { _WindMag = value; }
    }

    public double WindDir
    {
        get { return _WindDir; }
        set { _WindDir = value; }
    }

    public double WaterTemp
    {
        get { return _WaterTemp; }
        set { _WaterTemp = value; }
    }

    public int evaporationOn
    {
        get { return _EvapOn; }
        set { _EvapOn = value; }
    }

    public int entrainOn
    {
        get { return _EntrainOn; }
        set { _EntrainOn = value; }
    }
    #endregion

    #region Private Methods
    private double GetOilDensity(int param)
    {
        FileStream fs = null;
        TextReader tr = null;
        double Result = 0;
        try
        {
            fs = new FileStream(_OilInfoLocation + "\\OILDATA.LST", FileMode.Open);
            tr = new StreamReader(fs);
            string msg = tr.ReadLine(); //[Oildata]
            msg = tr.ReadLine(); //Version
            while (msg != "")
            {
                msg = tr.ReadLine().Trim(); //
                if (msg.ToUpper() == _OilType.ToUpper())
                {
                    for (int i = 1; i < 10; i++)
                    {
                        msg = tr.ReadLine();
                        if (i == 1 && param == 1)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 2 && param == 2)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 3 && param == 3)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 5 && param == 5)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 6 && param == 6)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 7 && param == 7)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 8 && param == 8)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                        else if (i == 9 && param == 9)
                        {
                            Result = Convert.ToDouble(msg);
                            break;
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            //Result = 0;
        }
        finally
        {
            if (tr != null)
                tr.Close();
            if (fs != null)
                fs.Close();
        }
        return Result;
    }

    #endregion

    #region Constructors
    public OilInputData(string appPath, string sLocation)
	{
        _DataLocation = appPath + ConfigurationManager.AppSettings["DataLocation"];
        _EXEPath = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilExeLocation"];
        _IniPath = _DataLocation + ConfigurationManager.AppSettings["OilIniLocation"];
        _INIFileName = ConfigurationManager.AppSettings["OilIniFile"];
        _INPFileName = ConfigurationManager.AppSettings["OilInpFile"];
        _OutputLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilOutputLocation"];
        if (!(Directory.Exists(_OutputLocation)))
            Directory.CreateDirectory(_OutputLocation);
        _RunLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilRunLocation"];
        if (!(Directory.Exists(_RunLocation)))
            Directory.CreateDirectory(_RunLocation);
        _InpPath = _RunLocation;
        _WindLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilWindsLocation"];
        if (!(Directory.Exists(_WindLocation)))
            Directory.CreateDirectory(_WindLocation);
        _CurrentLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilCurrentsLocation"];
        if (!(Directory.Exists(_CurrentLocation)))
            Directory.CreateDirectory(_CurrentLocation);
        _OilInfoLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilInfoLocation"];
        _CoastlineFile = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["OilCoastlineFile"];

    }
    #endregion
}
