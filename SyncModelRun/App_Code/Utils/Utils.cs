using System;
using System.Data;
using System.Configuration;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.Drawing;

/// <summary>
/// Summary description for Utils
/// </summary>
public static class Utils
{
    #region Private Members
    //static private EventLog _Log;

    #endregion

    #region Public Properties
    #endregion

    #region Constructors
    //public Utils()
    //{
    //    _Log = new EventLog("ModelRun", ".");
    //}
    #endregion

    #region Private Methods
    #endregion

    #region Public Methods
    static public int dateTimeToInt(DateTime myDate)
    {
        if (myDate != new DateTime(1, 1, 1))
        {
            TimeSpan totalTime = myDate.Subtract(new DateTime(1979, 12, 31));
            return (totalTime.Days * 60 * 24) + ((totalTime.Hours * 60) + totalTime.Minutes);
        }
        else
            return -1;
    }
    static public double convertNMToDecDegrees(double min)
    {
        return min * 0.01665518;
    }
    static public double convertNMToDecDegrees(double min, double lat)
    {
        return min * 0.01665518 * (1/Math.Cos(lat * 0.0174533));
    }
    static public BoundingBox convertLatLon360(BoundingBox bBox)
    {
        BoundingBox retval = bBox.clone();
        if((retval.west > 0) & (retval.east < 0))
        {
            retval.east += 360;
        }
        return retval;
    }
    static public BoundingBox convertBBoxMariano(BoundingBox bBox)
    {
        BoundingBox retval = bBox.clone();
        if(retval.east > 180)
        {
            retval.west -= 360;
            retval.east -= 360;
        }
        return retval;
    }

    static public bool PointInPolygon(PointF p, Polygon poly)
    {
        bool inside = false;
        if (poly.numPoints < 3)
        {
            return inside;
        }

        int lastIndex = 0;
        for (int j = 0; j < poly.numParts; j++)
        {
            lastIndex = (j == poly.numParts - 1 ? poly.numPoints -1 : poly.parts[j + 1] - 1);
            for (int i = poly.parts[j]; i < (j == poly.numParts - 1 ? poly.numPoints : poly.parts[j + 1]); i++)
            {
                if (poly.points[i].X < p.X && poly.points[lastIndex].X >= p.X
                    || poly.points[lastIndex].X < p.X && poly.points[i].X >= p.X)
                {
                    if (poly.points[i].Y + (p.X - poly.points[i].X) / (poly.points[lastIndex].X - poly.points[i].X) *
                        (poly.points[lastIndex].Y - poly.points[i].Y) < p.Y)
                    {
                        inside = !inside;
                    }
                }
                lastIndex = i;
            }
        }
        return inside;
    }
    #endregion
}
