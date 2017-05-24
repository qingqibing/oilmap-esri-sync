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
using System.Data.OleDb;
using System.Runtime.InteropServices;
using System.Globalization;
using System.Data.Odbc;
using System.Diagnostics;

/// <summary>
/// Summary description for OilTimeSeries
/// </summary>
public class OilTimeSeries : TimeSeries
{
    private DateTime _StartDate;

	public OilTimeSeries(string sOutputPath, string sScenarioName)
	{
        OutputPath = sOutputPath;
        ScenarioName = sScenarioName;

        string sFilename = OutputPath + "\\RUNDATA\\" + ScenarioName + ".inp";
        int iYear = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Year", ""));
        int iMonth = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Month", ""));
        int iDay = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Day", ""));
        int iHour = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Hour", ""));
        int iMinute = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Minute", ""));
        _StartDate = new DateTime(iYear, iMonth, iDay, iHour, iMinute, 0);
	}

    public override string GetScenarioTimeSeriesFromEXE(string sEXEPath)
    {
        string Result = "";
        string sFatesfile = OutputPath + "\\Fates\\" + ScenarioName + ".DBF";
        string sNewFile = Path.ChangeExtension(sFatesfile, ".FTE");

        Process myProcess = new Process();
        myProcess.StartInfo.FileName = sEXEPath;
        myProcess.StartInfo.CreateNoWindow = false;
        myProcess.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
        myProcess.StartInfo.ErrorDialog = false;
        myProcess.StartInfo.Arguments = sFatesfile;
        myProcess.Start();
        myProcess.WaitForExit();       

        using (StreamReader sr = new StreamReader(sNewFile))
        {
            Result = sr.ReadToEnd();
        }
        return Result;
    }

    public override string GetScenarioTimeSeries()
    {
        OdbcDataReader dr = OpenDataReader();
        string Result = "";
        if (dr != null)
        {
            Result = "Time (Hours),Surface (Tonnes),Water Col (Tonnes),Ashore (Tonnes),Evaporated (Tonnes),Thickness (m),Viscosity (cSt),Total Area (km²),Volume (m³),Density;";
            DateTime baseDate = new DateTime(1979, 12, 31);

            while (dr.Read())
            {
                DateTime thisDate = _StartDate.AddHours(Convert.ToDouble(dr["Time"]));
                TimeSpan mySpan = Convert.ToDateTime(thisDate).Subtract(baseDate);
                double dSurface = Convert.ToDouble(dr["Surface"]);
                double dWaterCol = Convert.ToDouble(dr["WaterCol"]);
                double dAshore = Convert.ToDouble(dr["Ashore"]);
                double dEvaporated = Convert.ToDouble(dr["Evaporated"]);
                double dThickness = Convert.ToDouble(dr["Thickness"]);
                double dViscosity = Convert.ToDouble(dr["Viscosity"]);
                double dTotalArea = Convert.ToDouble(dr["TotalArea"]);
                double dMousseVol = Convert.ToDouble(dr["MousseVol"]);
                double dDensity = Convert.ToDouble(dr["Density"]);
                Result += String.Format("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9};", mySpan.TotalMinutes, dSurface.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dWaterCol.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dAshore.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dEvaporated.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dThickness.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dViscosity.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dTotalArea.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dMousseVol.ToString(CultureInfo.CreateSpecificCulture("en-US")),
                                                                                     dDensity.ToString(CultureInfo.CreateSpecificCulture("en-US")));
            }
            dr.Close();
        }
        CloseDataConnection();
        return Result;
    }
}
