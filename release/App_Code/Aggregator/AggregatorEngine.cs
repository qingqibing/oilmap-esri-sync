using System;
using System.Data;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.IO;
using System.Configuration;

/// <summary>
/// Summary description for AggregatorEngine
/// </summary>
public class AggregatorEngine
{
    #region Private Members
    private int _DataName; //NCOM, GFS, NDBC etc...
    private DateTime _StartDate;
    private DateTime _EndDate;
    private BoundingBox _BBox;
    private string _AppPath;
    private string _OuputDirectory;
    private string _WindDataLocation;
    private string _CurrentDataLocation;
    private string _BathyLocation;
    private List<string> _FileList;
    #endregion

    #region Public Properties
    public int dataName
    {
        get { return _DataName; }
        set { _DataName = value; }
    }
    public DateTime startDate
    {
        get { return _StartDate; }
        set { _StartDate = value; }
    }
    public DateTime endDate
    {
        get { return _EndDate; }
        set { _EndDate = value; }
    }
    public BoundingBox bBox
    {
        get { return _BBox; }
        set { _BBox = value; }
    }
    public string outputDirectory
    {
        get { return _OuputDirectory; }
        set { _OuputDirectory = value; }
    }
    #endregion

    #region Constructors
    /// <summary>
    /// Full Constructor
    /// </summary>
    /// <param name="dataName">Name of the Data (i.e. NCOM, GFS, NDBC)</param>
    /// <param name="start">Start time of the data</param>
    /// <param name="end">End time of the Data</param>
    /// <param name="bBox">Bounding Box or AOI</param>
    /// <param name="outDir">Path to write the file to</param>
    public AggregatorEngine(int dataName, DateTime start, DateTime end, BoundingBox bBox, string applicationPath, string outputDir, bool isRiver)
    {
        _DataName = dataName;
        _StartDate = start;
        _EndDate = end;
        _BBox = bBox;
        _AppPath = applicationPath;
        _WindDataLocation = _AppPath + "\\ModelData\\Winds"; //ConfigurationManager.AppSettings["WindDataLocation"];
        _CurrentDataLocation = _AppPath + "\\ModelData\\Currents";// ConfigurationManager.AppSettings["CurrentDataLocation"];
        if (isRiver)
            _CurrentDataLocation = _AppPath + "\\ModelData\\RiverCurrents"; // ConfigurationManager.AppSettings["RiverCurrentLocation"];
        _BathyLocation = _AppPath + "\\ModelData\\Bathy"; // ConfigurationManager.AppSettings["BathyDataLocation"];
        _FileList = new List<string>();
        _OuputDirectory = outputDir;
    }
    #endregion

    #region Public Methods
    public string getCurrents(string filePrefix, string fileName)
    {
        string retval = "";
        collectFiles(_CurrentDataLocation, filePrefix);
        retval = uniteFiles(fileName);        
        return retval;
    }

    public string getWinds(string filePrefix, string fileName)
    {
        string retval = "";
        collectFiles(_WindDataLocation, filePrefix);
        retval = uniteFiles(fileName);
        return retval;
    }
    #endregion

    #region Private Methods
    /// <summary>
    /// Collects the files within the time range of start date and end date
    /// </summary>
    /// <param name="dataLocation">Location of the files</param>
    /// <param name="prefix">The prefix of the file before the date bit</param>
    private void collectFiles(string dataLocation, string prefix)
    {
        _FileList = new List<string>();
        //Set the start and End times
        DateTime startCheck = new DateTime(_StartDate.Year, _StartDate.Month, _StartDate.Day);
        DateTime endCheck = new DateTime(_EndDate.Year, _EndDate.Month, _EndDate.Day);
        
        //Loop through and grab the files
        while (startCheck <= endCheck)
        {
            string fileName = dataLocation + "\\" + prefix + startCheck.ToString("yyyyMMdd") + ".nc";
            if (File.Exists(fileName))
                _FileList.Add(fileName);
            startCheck = startCheck.AddDays(1);
        }

        //Reverse the list because the uniter needs the latest file first
        _FileList.Reverse();
    }
    /// <summary>
    /// Unites the data sources and compiles it to a file
    /// </summary>
    /// <returns>file name of the compiled file</returns>
    private string uniteFiles(string fileName)
    {
        string retval = "";
        //Set up the Unite Object
        ASAUniteV3._BlackNite uniter = new ASAUniteV3.BlackNite();
        uniter.Init();
        uniter.AOI_West = (float)_BBox.west;
        uniter.AOI_East = (float)_BBox.east;
        uniter.AOI_North = (float)_BBox.north;
        uniter.AOI_South = (float)_BBox.south;
        uniter.AOI_startTmin = DateTime2Int(_StartDate.AddHours(0));
        uniter.AOI_endTmin = DateTime2Int(_EndDate.AddHours(10));
        uniter.DepthFile = _BathyLocation + "\\ETOP2.dos";
        uniter.CellSizeKm = 5;
        uniter.OutNCType = 1;
        uniter.OutUnit = "Knots";
        uniter.TimeStepMin = 60;
        if (outputDirectory.Contains("WINDS"))
            uniter.WindOut = true;
        else
            uniter.WindOut = false;
        uniter.Sources = "WUHAN";
        //Loop through and add all the files
        if (_FileList.Count == 0)
            return "ERROR: No files found in the given time range";
     
        foreach (string file in _FileList)
        {
            uniter.AddFiles(file);
        }
      
        try
        {
            int status = 0;
            retval = _OuputDirectory + fileName + ".nc";
            if (uniter.Make(retval) > -1)
            {
                string blank = "";
                while (status < 100)
                {
                    status = uniter.Progress(ref blank);
                    if (status < 0)
                    {
                        retval = "ERROR: ASAUnite has failed" + uniter.Error;
                        break;
                    }
                }
            }
            else
            {
                retval = "ERROR: " + uniter.Error;
            }
        }
        catch (Exception ex)
        {
            retval = "ERROR: " + ex.Message;
        }
        return retval;
    }
    public int DateTime2Int(DateTime dt)
    {
        try
        {
            int iDT = 0;

            if (dt != null)
            {
                DateTime dtBase = new DateTime(1979, 12, 31);
                TimeSpan ts = dt.Subtract(dtBase);

                iDT = (ts.Days * 60 * 24) + ((ts.Hours * 60) + ts.Minutes);
            }

            return iDT;
        }
        catch
        {
            return 0;
        }
    }
    #endregion
}
