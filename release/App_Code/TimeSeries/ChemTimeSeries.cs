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
using System.Data.Odbc;
using System.Diagnostics;

/// <summary>
/// Summary description for ChemTimeSeries
/// </summary>
public class ChemTimeSeries : TimeSeries
{
	public ChemTimeSeries(string sOutputPath, string sScenarioName)
	{
        OutputPath = sOutputPath;
        ScenarioName = sScenarioName;
	}

    public override string GetScenarioTimeSeries()
    {
        OdbcDataReader dr = OpenDataReader();
        string Result = "";
        if (dr != null)
        {
            Result = "Time,Surface (Tonnes),Water Col (Tonnes),Ashore (Tonnes);";
            DateTime baseDate = new DateTime(1979, 12, 31);

            while (dr.Read())
            {
                double dPart = Convert.ToDouble(dr["WC_Partic"]);
                double dDisslv = Convert.ToDouble(dr["WC_Disslv"]);
                double dAdsorb = Convert.ToDouble(dr["WC_Adsorb"]);
                double dTotal = dPart + dDisslv + dAdsorb;
                TimeSpan mySpan = Convert.ToDateTime(dr["DateTime"]).Subtract(baseDate);
                Result += String.Format("{0},{1},{2},{3};", mySpan.TotalMinutes, dr["Surface"], dTotal, dr["Ashore"]);
            }
            dr.Close();
        }
        CloseDataConnection();
        return Result;
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

        while (!(myProcess.HasExited))
        {

        }

        using (StreamReader sr = new StreamReader(sNewFile))
        {
            Result = sr.ReadToEnd();
        }
        return Result;
    }
}
