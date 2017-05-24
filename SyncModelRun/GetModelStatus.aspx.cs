using System;
using System.Data;
using System.Configuration;
using System.Collections;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.IO;
using System.Runtime.InteropServices;

public partial class GetModelStatus : System.Web.UI.Page
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

    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?Location=World&Scenario=hello2_573_46_30929&ModelType=OILSPILL");

        string sPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        string sLocation = Request.QueryString["Location"];
        string sScenario = Request.QueryString["Scenario"];
        string sModeltype = Request.QueryString["ModelType"];

        int iPercent = 0;
        switch (sModeltype.ToUpper())
        {
            case "OILSPILL":
                iPercent = GetOilPercentDone(sPath, sLocation, sScenario);
                break;
            case "CHEMSPILL":
                iPercent = GetChemPercentDone(sPath, sLocation, sScenario);
                break;
        }
        Response.Write(iPercent.ToString());
    }

    private int GetChemPercentDone(string sPath, string sLocation, string sScenario)
    {
        return 0;
    }

    private int GetOilPercentDone(string sPath, string sLocation, string sScenario)
    {
        string sInpFile = sPath + "\\ModelData\\" + sLocation + "\\Rundata\\" + sScenario + ".INP";
        int iDuration = int.Parse(GetIniFileString(sInpFile, "OILMAPW", "Simulation Length", "0"));
        int iInterval = int.Parse(GetIniFileString(sInpFile, "OILMAPW", "out_intvl", "0"));
        if (iInterval == 0)
            return 0;

        int iTotalSize = (int)(((iDuration + 1) * 60) / iInterval * 12 + 12);
        sInpFile = sPath + "\\ModelData\\" + sLocation + "\\Outdata\\" + sScenario + ".OMP";
        FileInfo f = new FileInfo(sInpFile);
        long s1 = f.Length;
        return (int)((double)((double)s1 / (double)iTotalSize) * 100);
    }

    private string GetIniFileString(string iniFile, string category, string key, string defaultValue)
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
}
