using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Data.OleDb;
using System.IO;

/// <summary>
/// Summary description for ChemInputData
/// </summary>
public class ChemInputData:InputData
{
	#region Private Members
    //Paths
    private string _IniPath;
    private string _CnpPath;
    private string _OutputLocation;
    private string _RunLocation;
    private string _WindLocation;
    private string _CurrentLocation;
    private string _EXEPath;

    //File Names
    private string _CNPFileName;
    private string _INIFileName;

    //Chem Model Info
    private string _Scenario;
    private DateTime _SpillTime;
    private string _ChemType;
    private bool _ModelMethod;
    private int _CAS1;
    private int _CAS2;
    private int _CAS3;
    private double _Dens25c;
    //private double _Vapprs;
    //private double _Thrsld;
    //private double _Slblty;
    private double _Thk25c;
    private double _Partsize;
    private double _Dgrda25c;
    private double _Dgrdw25c;
    private double _Dgrds25c;
    private int _Chemsticky;
    private double _Dbulk25c;
    private double _Concaqu;
    private double _Concemul;
    private double _Concphob;
    private double _Statecode;
    private double _Fwsol25c;
    private double _Swsol25c;
    private double _Vapr25c;
    private double _Srft25c;
    private double _Visc25c;
    private double _VISA;
    private double _VISB;
    private double _Hlaw25c;
    private double _Dislv25c;
    private double _Molwt;
    private double _Bpc;
    //private double _Apigrav;
    //private double _Flashptc;
    private double _Mpc;
    private double _Logkow;
    private double _Logkoc;
    private double _Ccode;
    private double _DensAtT;
    private double _DegCDens;
    private double _ViscAtT;
    private double _DegCVis;
    private double _VapPrsAtT;
    private double _DegCVap;
    private double _DgrdSurfW25c;
    private double _HlawAtT;
    private double _DegChLaw;
    private int _React;
    private string _ReactsWith;
    private double _Diffus25c;
    private string _Formula;
    private int _UnNo;
    private int _FormNo;
    private int _AcidBaseCons;
    private double _SpillDuration;
    #endregion

    #region Public Properties
    //Paths (READ ONLY)
    public string exePath
    {
        get { return _EXEPath; }
    }
    public string iniPath
    {
        get { return _IniPath; }
    }
    public string cnpPath
    {
        get { return _CnpPath; }
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
    public string cnpFileName
    {
        get { return _CNPFileName; }
        set { _CNPFileName = value; }
    }
    public string iniFileName
    {
        get { return _INIFileName; }
        set { _INIFileName = value; }
    }

    //Chem Model Info
    public string scenario
    {
        get { return _Scenario; }
        set { _Scenario = value; }
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
        get { return _IncidentSite.lon.ToString(); }
        set { _IncidentSite.lon = Convert.ToDouble(value); }
    }
    public string splat1
    {
        get { return _IncidentSite.lat.ToString(); }
        set { _IncidentSite.lat = Convert.ToDouble(value); }
    }
    public double simulationLength
    {
        get
        {
            TimeSpan ts = new TimeSpan(_EndDate.Ticks - _StartDate.Ticks);
            return (double)ts.TotalDays;
        }
    }
    public string chemType
    {
        get { return _ChemType; }
        set
        {
            _ChemType = value;
            GetChemicalValues();
        }
    }
    public bool ModelMethod
    {
        get { return _ModelMethod; }
        set { _ModelMethod = value; }
    }
    public int CAS1
    {
        get { return _CAS1; }
    }
    public int CAS2
    {
        get { return _CAS2; }
    }
    public int CAS3
    {
        get { return _CAS3; }
    }
    public double Dens25c
    {
        get { return _Dens25c; }
    }
    //public double Vapprs
    //{
    //    get { return _Vapprs; }
    //}
    //private double Thrsld
    //{
    //    get { return _Thrsld; }
    //}
    //public double Slblty
    //{
    //    get { return _Slblty; }
    //}
    public double Thk25c
    {
        get { return _Thk25c; }
    }
    public double Partsize
    {
        get { return _Partsize; }
    }
    public double Dgrda25c
    {
        get { return _Dgrda25c; }
    }
    public double Dgrdw25c
    {
        get { return _Dgrdw25c; }
    }
    public double Dgrds25c
    {
        get { return _Dgrds25c; }
    }
    public int Chemsticky
    {
        get { return _Chemsticky; }
    }
    public double Dbulk25c
    {
        get { return _Dbulk25c; }
    }
    public double Concaqu
    {
        get { return _Concaqu; }
    }
    public double Concemul
    {
        get { return _Concemul; }
    }
    public double Concphob
    {
        get { return _Concphob; }
    }
    public double Statecode
    {
        get { return _Statecode; }
    }
    public double Fwsol25c
    {
        get { return _Fwsol25c; }
    }
    public double Swsol25c
    {
        get { return _Swsol25c; }
    }
    public double Vapr25c
    {
        get { return _Vapr25c; }
    }
    public double Srft25c
    {
        get { return _Srft25c; }
    }
    public double Visc25c
    {
        get { return _Visc25c; }
    }
    public double VISA
    {
        get { return _VISA; }
    }
    public double VISB
    {
        get { return _VISB; }
    }
    public double Hlaw25c
    {
        get { return _Hlaw25c; }
    }
    public double Dislv25c
    {
        get { return _Dislv25c; }
    }
    public double Molwt
    {
        get { return _Molwt; }
    }
    public double Bpc
    {
        get { return _Bpc; }
    }
    //public double Apigrav
    //{
    //    get { return _Apigrav; }
    //}
    //public double Flashptc
    //{
    //    get { return _Flashptc; }
    //}
    public double Mpc
    {
        get { return _Mpc; }
    }
    public double Logkow
    {
        get { return _Logkow; }
    }
    public double Logkoc
    {
        get { return _Logkoc; }
    }
    public double Ccode
    {
        get { return _Ccode; }
    }
    public double DensAtT
    {
        get { return _DensAtT; }
    }
    public double DegCDens
    {
        get { return _DegCDens; }
    }
    public double ViscAtT
    {
        get { return _ViscAtT; }
    }
    public double DegCVis
    {
        get { return _DegCVis; }
    }
    public double VapPrsAtT
    {
        get { return _VapPrsAtT; }
    }
    public double DegCVap
    {
        get { return _DegCVap; }
    }
    public double DgrdSurfW25c
    {
        get { return _DgrdSurfW25c; }
    }
    public double HlawAtT
    {
        get { return _HlawAtT; }
    }
    public double DegChLaw
    {
        get { return _DegChLaw; }
    }
    public int React
    {
        get { return _React; }
    }
    public string ReactsWith
    {
        get { return _ReactsWith; }
    }
    public double Diffus25c
    {
        get { return _Diffus25c; }
    }
    public string Formula
    {
        get { return _Formula; }
    }
    public int UnNo
    {
        get { return _UnNo; }
    }
    public int FormNo
    {
        get { return _FormNo; }
    }
    public int AcidBaseCons
    {
        get {return _AcidBaseCons;}
    }
    public double spillDuration
    {
        get { return _SpillDuration; }
        set { _SpillDuration = value; }
    }

    #endregion

    #region Constructors
    public ChemInputData(string appPath, string sLocation)
	{
        /*_DataLocation = appPath + System.Configuration.ConfigurationManager.AppSettings["DataLocation"];
        _EXEPath = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemExeLocation"];
        _IniPath = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemIniLocation"];
        _INIFileName = System.Configuration.ConfigurationManager.AppSettings["ChemIniFile"];
        _CnpPath = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemCnpLocation"];
        _CNPFileName = System.Configuration.ConfigurationManager.AppSettings["ChemCnpFile"];
        _OutputLocation = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemOutputLocation"];
        _RunLocation = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemRunLocation"];
        _WindLocation = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemWindLocation"];
        _CurrentLocation = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemCurrentLocation"];
        _CoastlineFile = appPath + System.Configuration.ConfigurationManager.AppSettings["ChemCoastlineFile"];*/
        _DataLocation = appPath + ConfigurationManager.AppSettings["DataLocation"];
        _EXEPath = _DataLocation + ConfigurationManager.AppSettings["ChemExeLocation"];
        _IniPath = _DataLocation + ConfigurationManager.AppSettings["ChemIniLocation"];
        _INIFileName = ConfigurationManager.AppSettings["ChemIniFile"];
        _CNPFileName = ConfigurationManager.AppSettings["ChemCnpFile"];
        _OutputLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["ChemOutputLocation"];
        if (!(Directory.Exists(_OutputLocation)))
            Directory.CreateDirectory(_OutputLocation);
        _RunLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["ChemRunLocation"];
        if (!(Directory.Exists(_RunLocation)))
            Directory.CreateDirectory(_RunLocation);
        _CnpPath = _RunLocation;
        _WindLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["ChemWindLocation"];
        if (!(Directory.Exists(_WindLocation)))
            Directory.CreateDirectory(_WindLocation);
        _CurrentLocation = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["ChemCurrentsLocation"];
        if (!(Directory.Exists(_CurrentLocation)))
            Directory.CreateDirectory(_CurrentLocation);
        _CoastlineFile = _DataLocation + "\\" + sLocation + ConfigurationManager.AppSettings["ChemCoastlineFile"];
    }
    #endregion

    #region Private Methods
    private void GetChemicalValues()
    {
        string sFilename = _EXEPath + "\\system\\ChemMap.mdb";
        OleDbConnection myConn = new OleDbConnection();
        try
        {
            myConn.ConnectionString = "Provider=Microsoft.Jet.OLEDB.4.0;Jet OLEDB:Database Password=i2w67nu;Data Source=" + sFilename;
            myConn.Open();
            string strSql = "SELECT * FROM main WHERE Chemname = @Chemname";
            OleDbCommand myCommand = new OleDbCommand(strSql, myConn);
            OleDbParameter myParam = new OleDbParameter("@Chemname", _ChemType);
            myCommand.Parameters.Add(myParam);
            OleDbDataReader dr = myCommand.ExecuteReader();
            if (dr.Read())
            {
                _CAS1 = !dr.IsDBNull(dr.GetOrdinal("Cas1")) ? Convert.ToInt32(dr["Cas1"]) : 0;
                _CAS2 = !dr.IsDBNull(dr.GetOrdinal("Cas2")) ? Convert.ToInt32(dr["Cas2"]) : 0;
                _CAS3 = !dr.IsDBNull(dr.GetOrdinal("Cas3")) ? Convert.ToInt32(dr["Cas3"]) : 0;
                _Dens25c = !dr.IsDBNull(dr.GetOrdinal("dens25c")) ? Convert.ToDouble(dr["dens25c"]) : 0;
                _Thk25c = !dr.IsDBNull(dr.GetOrdinal("thk25c")) ? Convert.ToDouble(dr["thk25c"]) : 0;
                _Partsize = !dr.IsDBNull(dr.GetOrdinal("partsize")) ? Convert.ToDouble(dr["partsize"]) : 0;
                _Dgrda25c = !dr.IsDBNull(dr.GetOrdinal("dgrda25c")) ? Convert.ToDouble(dr["dgrda25c"]) : 0;
                _Dgrdw25c = !dr.IsDBNull(dr.GetOrdinal("dgrdw25c")) ? Convert.ToDouble(dr["dgrdw25c"]) : 0;
                _Dgrds25c = !dr.IsDBNull(dr.GetOrdinal("dgrds25c")) ? Convert.ToDouble(dr["dgrds25c"]) : 0;
                _Chemsticky = !dr.IsDBNull(dr.GetOrdinal("sticky")) ? Convert.ToInt32(dr["sticky"]) : 0;
                _Dbulk25c = !dr.IsDBNull(dr.GetOrdinal("dbulk25c")) ? Convert.ToDouble(dr["dbulk25c"]) : 0;
                _Concaqu = !dr.IsDBNull(dr.GetOrdinal("concaqu")) ? Convert.ToDouble(dr["concaqu"]) : 0;
                _Concemul = !dr.IsDBNull(dr.GetOrdinal("concemul")) ? Convert.ToDouble(dr["concemul"]) : 0;
                _Concphob = !dr.IsDBNull(dr.GetOrdinal("concphob")) ? Convert.ToDouble(dr["concphob"]) : 0;
                _Statecode = !dr.IsDBNull(dr.GetOrdinal("statecode")) ? Convert.ToDouble(dr["statecode"]) : 0;
                _Fwsol25c = !dr.IsDBNull(dr.GetOrdinal("fwsol25c")) ? Convert.ToDouble(dr["fwsol25c"]) : 0;
                _Swsol25c = !dr.IsDBNull(dr.GetOrdinal("swsol25c")) ? Convert.ToDouble(dr["swsol25c"]) : 0;
                _Vapr25c = !dr.IsDBNull(dr.GetOrdinal("vapr25c")) ? Convert.ToDouble(dr["vapr25c"]) : 0;
                _Srft25c = !dr.IsDBNull(dr.GetOrdinal("srft25c")) ? Convert.ToDouble(dr["srft25c"]) : 0;
                _Visc25c = !dr.IsDBNull(dr.GetOrdinal("visc25c")) ? Convert.ToDouble(dr["visc25c"]) : 0;
                _VISA = !dr.IsDBNull(dr.GetOrdinal("visa")) ? Convert.ToDouble(dr["visa"]) : 0;
                _VISB = !dr.IsDBNull(dr.GetOrdinal("visb")) ? Convert.ToDouble(dr["visb"]) : 0;
                _Hlaw25c = !dr.IsDBNull(dr.GetOrdinal("hlaw25c")) ? Convert.ToDouble(dr["hlaw25c"]) : 0;
                _Dislv25c = !dr.IsDBNull(dr.GetOrdinal("dislv25c")) ? Convert.ToDouble(dr["dislv25c"]) : 0;
                _Molwt = !dr.IsDBNull(dr.GetOrdinal("molwt")) ? Convert.ToDouble(dr["molwt"]) : 0;
                _Bpc = !dr.IsDBNull(dr.GetOrdinal("bpc")) ? Convert.ToDouble(dr["bpc"]) : 0;
                _Mpc = !dr.IsDBNull(dr.GetOrdinal("mpc")) ? Convert.ToDouble(dr["mpc"]) : 0;
                _Logkow = !dr.IsDBNull(dr.GetOrdinal("logkow")) ? Convert.ToDouble(dr["logkow"]) : 0;
                _Logkoc = !dr.IsDBNull(dr.GetOrdinal("logkoc")) ? Convert.ToDouble(dr["logkoc"]) : 0;
                _Ccode = !dr.IsDBNull(dr.GetOrdinal("ccode")) ? Convert.ToDouble(dr["ccode"]) : 0;
                _DensAtT = !dr.IsDBNull(dr.GetOrdinal("densatt")) ? Convert.ToDouble(dr["densatt"]) : 0;
                _DegCDens = !dr.IsDBNull(dr.GetOrdinal("degcdens")) ? Convert.ToDouble(dr["degcdens"]) : 0;
                _ViscAtT = !dr.IsDBNull(dr.GetOrdinal("viscatt")) ? Convert.ToDouble(dr["viscatt"]) : 0;
                _DegCVis = !dr.IsDBNull(dr.GetOrdinal("degcvisc")) ? Convert.ToDouble(dr["degcvisc"]) : 0;
                _VapPrsAtT = !dr.IsDBNull(dr.GetOrdinal("vapprsatt")) ? Convert.ToDouble(dr["vapprsatt"]) : 0;
                _DegCVap = !dr.IsDBNull(dr.GetOrdinal("degcvap")) ? Convert.ToDouble(dr["degcvap"]) : 0;
                _DgrdSurfW25c = !dr.IsDBNull(dr.GetOrdinal("dgrdsurfw25c")) ? Convert.ToDouble(dr["dgrdsurfw25c"]) : 0;
                _HlawAtT = !dr.IsDBNull(dr.GetOrdinal("hlawatt")) ? Convert.ToDouble(dr["hlawatt"]) : 0;
                _DegChLaw = !dr.IsDBNull(dr.GetOrdinal("degchlaw")) ? Convert.ToDouble(dr["degchlaw"]) : 0;
                _React = !dr.IsDBNull(dr.GetOrdinal("react")) ? Convert.ToInt32(dr["react"]) : 0;
                _ReactsWith = !dr.IsDBNull(dr.GetOrdinal("reactswith")) ? dr["reactswith"].ToString() : "";
                _Diffus25c = !dr.IsDBNull(dr.GetOrdinal("diffus25c")) ? Convert.ToDouble(dr["diffus25c"]) : 0;
                _Formula = !dr.IsDBNull(dr.GetOrdinal("formula")) ? dr["formula"].ToString() : "";
                _UnNo = !dr.IsDBNull(dr.GetOrdinal("unno")) ? Convert.ToInt32(dr["unno"]) : 0;
                _FormNo = !dr.IsDBNull(dr.GetOrdinal("FORMNO")) ? Convert.ToInt32(dr["FORMNO"]) : 0;
                _AcidBaseCons = !dr.IsDBNull(dr.GetOrdinal("Acid_Base_Cons")) ? Convert.ToInt32(dr["Acid_Base_Cons"]) : 0;
            }
            dr.Close();
        }
        catch (Exception exception)
        { }
        finally
        {
            myConn.Close();
        }
        
    }
    #endregion
}
