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
/// Summary description for BoundingBox
/// </summary>
public class BoundingBox
{
    #region Private members
    private LatLon _TopLeft;
    private LatLon _TopRight;
    private LatLon _BotRight;
    private LatLon _BotLeft;
    #endregion

    #region Public Properties
    public LatLon topLeft
    {
        get { return _TopLeft; }
        set { _TopLeft = value; }
    }
    public LatLon topRight
    {
        get { return _TopRight; }
        set { _TopRight = value; }
    }
    public LatLon botRight
    {
        get { return _BotRight; }
        set { _BotRight = value; }
    }
    public LatLon botLeft
    {
        get { return _BotLeft; }
        set { _BotLeft = value; }
    }

    public double north
    {
        get { return _TopLeft.lat; }
        set
        {
            if (_TopLeft == null)
                _TopLeft = new LatLon();
            if (_TopRight == null)
                _TopRight = new LatLon();
            _TopLeft.lat = value;
            _TopRight.lat = value;
        }
    }
    public double east
    {
        get { return _TopRight.lon; }
        set
        {
            if (_TopRight == null)
                _TopRight = new LatLon();
            if (_BotRight == null)
                _BotRight = new LatLon();
            _TopRight.lon = value;
            _BotRight.lon = value;
        }
    }
    public double south
    {
        get { return _BotLeft.lat; }
        set
        {
            if (_BotLeft == null)
                _BotLeft = new LatLon();
            if (_BotRight == null)
                _BotRight = new LatLon();
            _BotLeft.lat = value;
            _BotRight.lat = value;
        }
    }
    public double west
    {
        get { return _TopLeft.lon; }
        set
        {
            if (_TopLeft == null)
                _TopLeft = new LatLon();
            if (_BotLeft == null)
                _BotLeft = new LatLon();
            _TopLeft.lon = value;
            _BotLeft.lon = value;
        }
    }
    #endregion

    #region Constructors
    public BoundingBox()
	{
		//
		// TODO: Add constructor logic here
		//
	}
    public BoundingBox(LatLon topLeft, LatLon topRight, LatLon botRight, LatLon botLeft)
    {
        _TopLeft = topLeft;
        _TopRight = topRight;
        _BotLeft = botLeft;
        _BotRight = botRight;
    }
    public BoundingBox(double north, double south, double east, double west)
    {
        _TopRight = new LatLon(east, north);
        _TopLeft = new LatLon(west, north);
        _BotLeft = new LatLon(west, south);
        _BotRight = new LatLon(east, south);
    }
    public BoundingBox(string myBox)
    {
        if (myBox == null)
            return;
        string[] box = myBox.Split(',');
        west = Convert.ToDouble(box[0]);
        south = Convert.ToDouble(box[1]);
        east = Convert.ToDouble(box[2]);
        north = Convert.ToDouble(box[3]);
    }
    #endregion

    #region Public Methods
    public BoundingBox clone()
    {
        return new BoundingBox(north, south, east, west);
    }
    #endregion
}
