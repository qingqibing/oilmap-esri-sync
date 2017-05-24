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
using System.Runtime.InteropServices;
using System.Text;
using System.Data.Odbc;

/// <summary>
/// Summary description for TimeSeries
/// </summary>
public class TimeSeries
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
    public const string _ConnectionString = "Provider=Microsoft.Jet.OLEDB.4.0;Extended Properties=dBASE IV;User ID=Admin;Password=;Data Source=";
    private string _OutputPath;
    private string _ScenarioName;
    private OdbcConnection _OdbcConnection;

	public TimeSeries()
	{
		//
		// TODO: Add constructor logic here
		//
	}

    public string OutputPath
    {
        get { return _OutputPath; }
        set { _OutputPath = value; }
    }

    public string ScenarioName
    {
        get { return _ScenarioName; }
        set { _ScenarioName = value; }
    }

    public virtual string GetScenarioTimeSeries()
    {
        return "";
    }

    public virtual string GetScenarioTimeSeriesFromEXE(string sEXEPath)
    {
        return "";
    }

    public OdbcDataReader OpenDataReader()
    {
        string sFilename = OutputPath + "\\FATES\\" + ScenarioName + ".dbf";
        if (!(File.Exists(sFilename)))
            return null;

        if (Path.GetFileNameWithoutExtension(sFilename).Length > 8)
        {
            string sTemp = sFilename;
            sFilename = OutputPath + "\\FATES\\TempDBF.dbf";
            if (File.Exists(sFilename))
                File.Delete(sFilename);
            File.Copy(sTemp, sFilename);
        }

        _OdbcConnection = new OdbcConnection();
        _OdbcConnection.ConnectionString = "DSN=Visual FoxPro Tables;SourceType=DBF;SourceDB=" + OutputPath + "\\FATES;Exclusive=No; Collate=Machine;NULL=NO;DELETED=NO;BACKGROUNDFETCH=NO;"; //"Driver={Microsoft Visual FoxPro Driver};DriverID=277;Dbq=" + OutputPath + "\\FATES;"; // "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + OutputPath + "\\FATES\\" + "; Extended Properties=dBASE IV;User ID=Admin;Password=;";
        _OdbcConnection.Open();
        OdbcCommand oCmd = _OdbcConnection.CreateCommand();
        oCmd.CommandText = @"SELECT * FROM " + sFilename;
        OdbcDataReader dr = oCmd.ExecuteReader();
        return dr;
    }

    /*public OleDbDataReader OpenDataReader()
    {
        string sFilename = OutputPath + "\\FATES\\" + ScenarioName + ".dbf";
        if (!(File.Exists(sFilename)))
            return null;

        if (Path.GetFileNameWithoutExtension(sFilename).Length > 8)
        {
            string sTemp = sFilename;
            sFilename = OutputPath + "\\FATES\\TempDBF.dbf";
            if (File.Exists(sFilename))
                File.Delete(sFilename);
            File.Copy(sTemp, sFilename);
        }

        _OleDbConnection = new OleDbConnection();
        _OleDbConnection.ConnectionString = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + OutputPath + "\\FATES\\" + "; Extended Properties=dBASE IV;User ID=Admin;Password=;";
        _OleDbConnection.Open();
        OleDbCommand oCmd = _OleDbConnection.CreateCommand();
        oCmd.CommandText = @"SELECT * FROM " + sFilename;
        OleDbDataReader dr = oCmd.ExecuteReader();
        return dr;
    }*/

    public void CloseDataConnection()
    {
        //_OleDbConnection.Close();
        _OdbcConnection.Close();
    }

    public string GetIniFileString(string iniFile, string category, string key, string defaultValue)
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
