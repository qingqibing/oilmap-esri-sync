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
/// Summary description for LatLon
/// </summary>
public class LatLon
{
    #region Private members
    protected double _Lat;
    protected double _Lon;
    #endregion

    #region Public Properties
    public double lat
    {
        get { return _Lat; }
        set { _Lat = value; }
    }
    public double lon
    {
        get { return _Lon; }
        set { _Lon = value; }
    }
    public double[] latLon
    {
        get { return new double[] { _Lat, _Lon }; }
        set
        {
            _Lat = value[0];
            _Lon = value[1];
        }
    }
    #endregion

    #region constructors
    public LatLon()
    {
        //EMPTY
    }
    /// <summary>
    /// Lat Lon Datatype Constructor
    /// </summary>
    /// <param name="lat">Lattitue</param>
    /// <param name="lon">Longitude</param>
	public LatLon(double lat, double lon)
	{
        _Lon = lon;
        _Lat = lat;
    }
    #endregion

    #region Public Methods
    /// <summary>
    /// Clone Lat Lon
    /// </summary>
    /// <returns>Copy of this lat lon</returns>
    public LatLon clone()
    {
        return new LatLon(_Lat, _Lon);
    }
    public override bool Equals(object obj)
    {
        bool retval = false;
        LatLon test = obj as LatLon;
        if (test.lat == _Lat && test.lon == _Lon)
            retval = true;
        return retval;
    }

    public override int GetHashCode()
    {
        return base.GetHashCode();
    }
    #endregion
}
