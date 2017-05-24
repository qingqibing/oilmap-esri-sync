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
using System.Runtime.InteropServices;
using System.Text;
using System.Globalization;

/// <summary>
/// Summary description for FileScraper
/// </summary>
public class FileScraper
{
    [DllImport("KERNEL32.DLL", EntryPoint = "GetPrivateProfileStringW",
SetLastError = true,
CharSet = CharSet.Unicode, ExactSpelling = true,
CallingConvention = CallingConvention.StdCall)]
    private static extern int GetPrivateProfileString(
      string lpAppName,
      string lpKeyName,
      string lpDefault,
      string lpReturnString,
      int nSize,
      string lpFilename);

    private string _AppPath;
    private string _ModelType;

    public FileScraper(string modelType, string appPath)
    {
        _ModelType = modelType;
        _AppPath = appPath;
    }

    public string getModelFileNamesWithTime(string sLocation)
    {
        DateTime baseDate = new DateTime(1979, 12, 31);
        
        string retval = "";
        DirectoryInfo di = null;
        FileInfo[] modelFiles = null;
        bool first = true;
        
            System.Globalization.CultureInfo ci =
               System.Globalization.CultureInfo.InstalledUICulture;
            System.Globalization.NumberFormatInfo ni = (System.Globalization.NumberFormatInfo)
               ci.NumberFormat.Clone();
            NumberFormatInfo numberFormatInfo = System.Globalization.CultureInfo.CurrentCulture.NumberFormat;
        string sDecimalSeparator = numberFormatInfo.NumberDecimalSeparator;
            if (numberFormatInfo.NumberDecimalSeparator == ",")
            {
                ni.NumberDecimalSeparator = ".";
            }
            else if (numberFormatInfo.NumberDecimalSeparator == ".")
            {
                ni.NumberDecimalSeparator = ",";                
            }


            switch (_ModelType.ToUpper())
            {
                case "OILSPILL":
                    di = new DirectoryInfo(sLocation + ConfigurationManager.AppSettings["OilOutputLocation"]);
                    modelFiles = di.GetFiles("*.OMP");
                    foreach (FileInfo fi in modelFiles)
                    {
                        if (first)
                        {
                            retval = Path.GetFileNameWithoutExtension(fi.Name);
                            first = false;
                        }
                        else
                            retval += ";" + Path.GetFileNameWithoutExtension(fi.Name);

                        string sFilename = sLocation + ConfigurationManager.AppSettings["OilRunLocation"] + "\\" + Path.ChangeExtension(fi.Name, ".INP");
                        int iYear = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Start Year", "0"));
                        int iMonth = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Start Month", "0"));
                        int iDay = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Start Day", "0"));
                        int iHour = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Start Hour", "0"));
                        int iMinute = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Start Minute", "0"));
                        int iInterval = int.Parse(GetIniFileString(sFilename, "OILMAPW", "out_intvl", "60"));

                        DateTime thisDate = new DateTime(iYear, iMonth, iDay, iHour, iMinute, 0);
                        TimeSpan myStartSpan = thisDate.Subtract(baseDate);

                        int iDuration = int.Parse(GetIniFileString(sFilename, "OILMAPW", "Simulation Length", "0"));
                        TimeSpan myEndSpan = thisDate.AddHours(iDuration).Subtract(baseDate);
                        retval += String.Format(",{0},{1},{2}", myStartSpan.TotalMinutes, myEndSpan.TotalMinutes, iInterval);

                        double dLat = 0;
                        double dLon = 0;
                        string sTempValue = GetIniFileString(sFilename, "OILMAPW", "Spill Lat", "0");
                        if (sTempValue.Contains(sDecimalSeparator))
                            dLat = float.Parse(sTempValue);
                        else
                            dLat = float.Parse(sTempValue, ni);

                        sTempValue = GetIniFileString(sFilename, "OILMAPW", "Spill Lon", "0");
                        if (sTempValue.Contains(sDecimalSeparator))
                            dLon = float.Parse(sTempValue);
                        else
                            dLon = float.Parse(sTempValue, ni);

                        BoundingBox AOI = CalculateAOI(new LatLon(dLat, dLon), iDuration);
                        retval += string.Format(",{0},{1},{2},{3}", AOI.west.ToString().Replace(",", "."), AOI.south.ToString().Replace(",", "."), AOI.east.ToString().Replace(",", "."), AOI.north.ToString().Replace(",", "."));

                        string sEcopWinds = GetIniFileString(sFilename, "OILMAPW", "EcopWinds", "");
                        string sEcopCurrents = GetIniFileString(sFilename, "OILMAPW", "EcopCurrents", "");
                        retval += string.Format(",{0},{1}", sEcopWinds, sEcopCurrents);
                    }
                    break;
                case "CHEMSPILL":
                    di = new DirectoryInfo(sLocation + ConfigurationManager.AppSettings["ChemOutputLocation"]);
                    modelFiles = di.GetFiles("*.CTR");
                    foreach (FileInfo fi in modelFiles)
                    {
                        if (first)
                        {
                            retval = Path.GetFileNameWithoutExtension(fi.Name);
                            first = false;
                        }
                        else
                            retval += ";" + Path.GetFileNameWithoutExtension(fi.Name);

                        string sFilename = sLocation + ConfigurationManager.AppSettings["ChemRunLocation"] + "\\" + Path.ChangeExtension(fi.Name, ".CNP");
                        int iYear = int.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Start Year", ""));
                        int iMonth = int.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Start Month", ""));
                        int iDay = int.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Start Day", ""));
                        int iHour = int.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Start Hour", ""));
                        int iMinute = int.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Start Minute", ""));

                        DateTime thisDate = new DateTime(iYear, iMonth, iDay, iHour, iMinute, 0);
                        TimeSpan myStartSpan = thisDate.Subtract(baseDate);

                        int iDuration = (int)(double.Parse(GetIniFileString(sFilename, "Chemical Scenario", "Run Length", "")) * 24);
                        TimeSpan myEndSpan = thisDate.AddHours(iDuration).Subtract(baseDate);
                        retval += String.Format(",{0},{1}", myStartSpan.TotalMinutes, myEndSpan.TotalMinutes);

                        double dLat = 0;
                        double dLon = 0;
                        string sTempValue = GetIniFileString(sFilename, "Chemical Scenario", "Spill Lat", "0");
                        if (sTempValue.Contains(sDecimalSeparator))
                            dLat = float.Parse(sTempValue);
                        else
                            dLat = float.Parse(sTempValue, ni);

                        sTempValue = GetIniFileString(sFilename, "Chemical Scenario", "Spill Lon", "0");
                        if (sTempValue.Contains(sDecimalSeparator))
                            dLon = float.Parse(sTempValue);
                        else
                            dLon = float.Parse(sTempValue, ni);

                        BoundingBox AOI = CalculateAOI(new LatLon(dLat, dLon), iDuration);
                        retval += string.Format(",{0},{1},{2},{3}", AOI.west.ToString().Replace(",", "."), AOI.south.ToString().Replace(",", "."), AOI.east.ToString().Replace(",", "."), AOI.north.ToString().Replace(",", "."));

                        string sEcopWinds = GetIniFileString(sFilename, "Chemical Scenario", "EcopWinds", "");
                        string sEcopCurrents = GetIniFileString(sFilename, "Chemical Scenario", "EcopCurrents", "");
                        retval += string.Format(",{0},{1}", sEcopWinds, sEcopCurrents);
                    }
                    break;
            }
        return retval;
    }

    private BoundingBox CalculateAOI(LatLon pIncidentSite, double dSpillDuration)
    {
        BoundingBox Result = new BoundingBox();
        double dMidLat = pIncidentSite.lat;
        double dLongitude, dLatitude;
        Meters2LonLat(3000, dMidLat, out dLongitude, out dLatitude);
        double xDiff = dSpillDuration * dLongitude;
        if (xDiff < 0.25)
            xDiff = 0.25;
        double yDiff = dSpillDuration * dLatitude;
        if (yDiff < 0.25)
            yDiff = 0.25;

        Result.west = pIncidentSite.lon - xDiff;
        Result.east = pIncidentSite.lon + xDiff;
        Result.north = pIncidentSite.lat + yDiff;
        Result.south = pIncidentSite.lat - yDiff;

        return Result;
    }

    public string getModelFileNames(string sLocation)
    {
        string retval = "";
        DirectoryInfo di = null;
        FileInfo[] modelFiles = null;
        bool first = true;
        switch (_ModelType.ToUpper())
        {
            case "OILSPILL":
                di = new DirectoryInfo(sLocation + ConfigurationManager.AppSettings["OilOutputLocation"]);
                modelFiles = di.GetFiles("*.OMP");
                foreach (FileInfo fi in modelFiles)
                {
                    if (first)
                    {
                        retval = Path.GetFileNameWithoutExtension(fi.Name);
                        first = false;
                    }
                    else
                        retval += ";" + Path.GetFileNameWithoutExtension(fi.Name);
                }
                break;
            case "CHEMSPILL":
                di = new DirectoryInfo(sLocation + ConfigurationManager.AppSettings["ChemOutputLocation"]);
                modelFiles = di.GetFiles("*.CTR");
                foreach (FileInfo fi in modelFiles)
                {
                    if (first)
                    {
                        retval = Path.GetFileNameWithoutExtension(fi.Name);
                        first = false;
                    }
                    else
                        retval += ";" + Path.GetFileNameWithoutExtension(fi.Name);
                }
                break;
        }
        return retval;
    }

    public static string GetIniFileString(string iniFile, string category, string key, string defaultValue)
    {
        try
        {
            string returnString = new string(' ', 1024);
            GetPrivateProfileString(category, key, defaultValue, returnString, 1024, iniFile);
            return returnString.Split('\0')[0];
        }
        catch
        {
            return "";
        }
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
