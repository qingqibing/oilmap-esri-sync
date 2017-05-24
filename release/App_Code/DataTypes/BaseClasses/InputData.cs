using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;

/// <summary>
/// Summary description for InputData
/// </summary>
public class InputData
{
    #region Private Members
    protected BoundingBox _BBox;
    protected LatLon _IncidentSite;
    protected string _CaseName;
    protected string _FileName;
    protected DateTime _StartDate;
    protected DateTime _EndDate;
    protected string _WindFile;
    protected string _CurrentFile;
    protected string _EcopWinds;
    protected string _EcopCurrents;
    protected string _DataLocation;
    protected string _CoastlineFile;
    #endregion

    #region Public Properties
    public BoundingBox bBox
    {
        get { return _BBox; }
        set { _BBox = value; }
    }
    public LatLon incidentSite
    {
        get { return _IncidentSite; }
        set 
        { 
            _IncidentSite = value; 
        }
    }
    public string caseName
    {
        get { return _CaseName; }
        set { _CaseName = value; }
    }
    public DateTime start
    {
        get { return _StartDate; }
        set { _StartDate = value; }
    }
    public DateTime end
    {
        get { return _EndDate; }
        set { _EndDate = value; }
    }
    public string windsFile
    {
        get { return _WindFile; }
        set { _WindFile = value; }
    }
    public string currentFile
    {
        get { return _CurrentFile; }
        set { _CurrentFile = value; }
    }
    public string ecopWinds
    {
        get { return _EcopWinds; }
        set { _EcopWinds = value; }
    }
    public string ecopCurrents
    {
        get { return _EcopCurrents; }
        set { _EcopCurrents = value; }
    }
    public string fileName
    {
        get { return _FileName; }
        set { _FileName = value; }
    }
    public string dataLocation
    {
        get { return _DataLocation; }
        set { _DataLocation = value; }
    }
    public string coastLineFile
    {
        get { return _CoastlineFile; }
        set { _CoastlineFile = value; }
    }
    #endregion

    #region Constructors
    public InputData()
	{
		//
		// TODO: Add constructor logic here
		//
    }
    #endregion

    #region Private Methods
    #endregion

    #region Public Methods
    #endregion
}
