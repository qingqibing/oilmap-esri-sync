using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Runtime.InteropServices;
//using System.Web.UI.MobileControls;
using System.Collections.Generic;

/// <summary>
/// Summary description for NowcastingProcessor
/// </summary>
public class NowcastingProcessor
{
    [DllImport("nowcast.dll", EntryPoint = "Initialize", CharSet = CharSet.Ansi)]
    public static extern int Initialize();
    [DllImport("nowcast.dll", EntryPoint = "CreateProRequest", CharSet = CharSet.Ansi)]
    public static extern int CreateProRequest(string pCompany, int LenPCompany, string pUser, int LenPUser, string Ppass, int LenPPass, int StartTime, int LastForecastTime, int LastUpdateTime, int NDPlong, int Use48, string PBlocksString, int LenPBlocksString);
    [DllImport("nowcast.dll", EntryPoint = "CreateProRequestB", CharSet = CharSet.Ansi)]
    public static extern int CreateProRequestB(string pCompany, int LenPCompany, string pUser, int LenPUser, string Ppass, int LenPPass, int StartTime, int LastForecastTime, int LastUpdateTime, int NDPlong, int FCHours, string PBlocksString, int LenPBlocksString, string PArcString, int LenPArcString);
    [DllImport("nowcast.dll", EntryPoint = "MakeTheRequest", CharSet = CharSet.Ansi)]
    public static extern int MakeTheRequest(string PWebAdd, int WALen, int UseProxy, string PProxyAdd, int PALen, int ThePort, string PUserName, int UNLen, string PPassword, int UPLen, int ProxyAuth, int DoDisconn);
    [DllImport("nowcast.dll", EntryPoint = "InterpretData", CharSet = CharSet.Ansi)]
    public static extern int InterpretData();
    [DllImport("nowcast.dll", EntryPoint = "ResetForNewRequest", CharSet = CharSet.Ansi)]
    public static extern int ResetForNewRequest();
    [DllImport("nowcast.dll", EntryPoint = "GetTotalRecords", CharSet = CharSet.Ansi)]
    public static extern int GetTotalRecords(ref int TotRec);
    [DllImport("nowcast.dll", EntryPoint = "GetARecord", CharSet = CharSet.Ansi)]
    public static extern int GetARecord(int recno, ref byte datatype, ref float LAT, ref float LON, ref int ForecastTime, ref float value1, ref float value2);
    [DllImport("nowcast.dll", EntryPoint = "GetError", CharSet = CharSet.Ansi)]
    public static extern int GetError();
    [DllImport("nowcast.dll", EntryPoint = "kmph2knots", CharSet = CharSet.Ansi)]
    public static extern float kmph2knots(float kmph);
    [DllImport("nowcast.dll", EntryPoint = "mps2knots", CharSet = CharSet.Ansi)]
    public static extern float mps2knots(float mps);
    [DllImport("nowcast.dll", EntryPoint = "Finalize", CharSet = CharSet.Ansi)]
    public static extern int Finalize();
    //This stuff is for direct dial up connections. Won't be used here.
    /*[DllImport("nowcast.dll", EntryPoint = "RASConnect", CharSet = CharSet.Ansi)]    
    public static extern int RASConnect(string PConnName, int CNLen);
    [DllImport("nowcast.dll", EntryPoint = "RASDisconnect", CharSet = CharSet.Ansi)]
    public static extern int RASDisconnect();
    [DllImport("nowcast.dll", EntryPoint = "RASGetLastError", CharSet = CharSet.Ansi)]
    public static extern int RASGetLastError(string PErr, int ErrLen);*/

    private const int m_cWinds = 1;
    private const int m_cTemp = 4;
    private const int m_cCurrents = 16;
    private const int m_cNCMaxArchive = -72;

    private int m_iDataType;

    private double m_dLatitude;
    private double m_dLongitude;
    private DateTime m_dteStartTime;
    private DateTime m_dteEndTime;
    private string m_sFilename;

    private struct VelocityType
    {
        public float u;
        public float v;
    }

    private string m_sUser = "" + (char)0;
    private string m_sCompany = "" + (char)0;
    private string m_sPass = "" + (char)0;
    private string m_sWebadd = "" + (char)0;
    private string m_sProxyadd = "" + (char)0;
    private string m_sProxyUser = "" + (char)0;
    private string m_sProxyPass = "" + (char)0;
    private short m_iUseProxy = 0;
    private short m_iThePort = 0;
    private short m_iProxyAuth = 0;
    private short m_iDoDisconn = 0;

    public double Latitude
    {
        get { return m_dLatitude; }
        set { m_dLatitude = value; }
    }

    public double Longitude
    {
        get { return m_dLongitude; }
        set { m_dLongitude = value; }
    }

    public DateTime StartTime
    {
        get { return m_dteStartTime; }
        set { m_dteStartTime = value; }
    }

    public DateTime EndTime
    {
        get { return m_dteEndTime; }
        set { m_dteEndTime = value; }
    }
    
    public int DataType
    {
        get { return m_iDataType; }
        set { m_iDataType = value; }
    }

    public string Filename
    {
        get { return m_sFilename; }
        set { m_sFilename = value; }
    }

    public NowcastingProcessor()
	{
		//
		// TODO: Add constructor logic here
		//
	}

    private void GetRegistrationInfo()
    {
        m_sUser = ConfigurationManager.AppSettings["NowcastingUser"] + (char)0; //"Tim Giguere" + (char)0;
        m_sPass = ConfigurationManager.AppSettings["NowcastingPass"] + (char)0; // "trial" + (char)0;
        m_sCompany = ConfigurationManager.AppSettings["NowcastingCompany"] + (char)0; //"ASA" + (char)0;
        m_sWebadd = "www.nowcastingint.com" + (char)0;
    }

    public string GetNowcastingData()
    {
        try
        {

            GetRegistrationInfo();

            TimeZone zone = TimeZone.CurrentTimeZone;

            DateTime dNowDate = DateTime.Now.ToUniversalTime();

            TimeSpan mySpan = dNowDate.Subtract(new DateTime(1970, 1, 1)); //DateDiff("s", "1/1/1970", dNowDate)
            int iStartTime = (int)mySpan.TotalSeconds;

            Initialize();
            string sBlockString = GetGridBlocks2();

            int dDifference1, dDifference2;
            string sPArc = "";

            int iLFT = 0, iLUT = 0, iNDP = m_iDataType, lFCHours = 0;

            if ((m_dteStartTime < dNowDate) && (m_dteEndTime < dNowDate)) //both archive times
            {
                mySpan = m_dteStartTime.Subtract(dNowDate);
                dDifference1 = (int)mySpan.TotalHours;
                mySpan = m_dteEndTime.Subtract(dNowDate);
                dDifference2 = (int)mySpan.TotalHours;
                if (dDifference1 < m_cNCMaxArchive)
                    dDifference1 = m_cNCMaxArchive;

                for (int i = dDifference1; i <= dDifference2; i++)
                    sPArc += i.ToString() + ",";

                if (sPArc != "")
                    sPArc = sPArc.Substring(0, sPArc.Length - 1) + (char)0;

                lFCHours = 0;
            }
            else if ((m_dteStartTime < dNowDate) && (m_dteEndTime >= dNowDate)) //starts off in the past, then needs forecast data
            {
                mySpan = m_dteEndTime.Subtract(dNowDate);
                dDifference2 = (int)mySpan.TotalHours;            //get archive data, then determine how much forecast data to get
                if (dDifference2 < 24)
                    lFCHours = 1;
                else if ((dDifference2 >= 24) && (dDifference2 < 48))
                    lFCHours = 2;
                else if (dDifference2 >= 48)
                    lFCHours = 3;

                mySpan = m_dteStartTime.Subtract(dNowDate);
                dDifference1 = (int)mySpan.TotalHours;

                if (dDifference1 < m_cNCMaxArchive)
                    dDifference1 = m_cNCMaxArchive;
                sPArc = "";
                for (int irec = dDifference1; irec <= -1; irec++)
                    sPArc += irec.ToString() + ",";
                if (sPArc != "")
                    sPArc = sPArc.Substring(0, sPArc.Length - 1) + (char)0;
            }
            else        //only need forecast data, determine how much to get
            {
                mySpan = m_dteEndTime.Subtract(dNowDate);
                dDifference2 = (int)mySpan.TotalHours;

                if (dDifference2 < 24)
                    lFCHours = 1;
                else if ((dDifference2 >= 24) && (dDifference2 < 48))
                    lFCHours = 2;
                else if (dDifference2 >= 48)
                    lFCHours = 3;

                sPArc = "" + (char)0;
            }

            int m_lResult;
            m_lResult = CreateProRequestB(m_sCompany, m_sCompany.Length, m_sUser, m_sUser.Length, m_sPass, m_sPass.Length, iStartTime, iLFT, iLUT, iNDP, lFCHours, sBlockString, sBlockString.Length, sPArc, sPArc.Length);

            m_lResult = MakeTheRequest(m_sWebadd, m_sWebadd.Length, m_iUseProxy, m_sProxyadd, m_sProxyadd.Length, m_iThePort, m_sProxyUser, m_sProxyUser.Length, m_sProxyPass, m_sProxyPass.Length, m_iProxyAuth, m_iDoDisconn);
            if (m_lResult != 0)
                throw new Exception(String.Format("MakeTheRequest:\r\n{0}\r\n{1}\r\n{2}\r\n{3}\r\n{4}\r\n{5}\r\n{6}\r\n{7}\r\n{8}\r\n{9}\r\n{10}",
                    GetNowcastError(m_lResult),
                    m_sCompany,
                    m_sUser,
                    m_sPass,
                    iStartTime, 
                    iLFT, 
                    iLUT, 
                    iNDP, 
                    lFCHours, 
                    sBlockString, 
                    sPArc));
            m_lResult = InterpretData();
            if (m_lResult != 0)
                throw new Exception("InterpretData:\r\n" + GetNowcastError(m_lResult));
            int lTotalRec = 0;
            m_lResult = GetTotalRecords(ref lTotalRec);
            if (m_lResult != 0)
                throw new Exception("GetTotalRecords:\r\n" + GetNowcastError(m_lResult));

            if (lTotalRec == 0)
                return "";

            List<string> aPos = new List<string>();
            List<int> aTimes = new List<int>();
            byte byDT = 0;
            float sgLat = 0, sgLon = 0, sgV1 = 0, sgV2 = 0;
            int lFT = 0;
            string sCurrentPos;

            for (int irec = 1; irec <= lTotalRec; irec++)
            {
                GetARecord(irec, ref byDT, ref sgLat, ref sgLon, ref lFT, ref sgV1, ref sgV2);
                sCurrentPos = sgLat.ToString() + sgLon.ToString();
                if (!(aPos.Contains(sCurrentPos))) //current position hasn't been put in yet
                {
                    aPos.Add(sCurrentPos);
                }
            }

            int[] iCellID = new int[] { 0 };
            float[] fLat = new float[] { 0 };
            float[] fLon = new float[] { 0 };
            int[] iTimeID = new int[] { 0 };
            int[] iTime = new int[] { 0 };
            float[] iVal = new float[] { 0 };
            int[] aIndex = new int[2];
            int lTimeVarID = 0, lCellVarID = 0;
            int lLatVarID = 0, lLonVarID = 0;
            int lUID = 0, lVID = 0;
            int lID = CreateDefaultNCFile(m_sFilename, aPos.Count, ref lTimeVarID, ref lCellVarID, ref lLatVarID, ref lLonVarID, ref lUID, ref lVID);
            int iResult = 0;
            aPos.Clear();

            for (int irec = 1; irec <= lTotalRec; irec++)
            {
                GetARecord(irec, ref byDT, ref sgLat, ref sgLon, ref lFT, ref sgV1, ref sgV2);
                sCurrentPos = sgLat.ToString() + sgLon.ToString();
                if (!(aPos.Contains(sCurrentPos))) //current position hasn't been put in yet
                {
                    iCellID[0] = aPos.Count;
                    iResult = NetCDF.nc_put_var1_int(lID, lCellVarID, iCellID, iCellID);
                    fLat[0] = sgLat;
                    iResult = NetCDF.nc_put_var1_float(lID, lLatVarID, iCellID, fLat);
                    fLon[0] = sgLon;
                    iResult = NetCDF.nc_put_var1_float(lID, lLonVarID, iCellID, fLon);
                    aPos.Add(sCurrentPos);
                }

                if (!(aTimes.Contains(lFT))) //current time hasn't been added
                {
                    iTimeID[0] = aTimes.Count;
                    iTime[0] = lFT;
                    iResult = NetCDF.nc_put_var1_int(lID, lTimeVarID, iTimeID, iTime);
                    aTimes.Add(lFT);
                }

                aIndex[0] = aTimes.IndexOf(lFT);
                aIndex[1] = aPos.IndexOf(sCurrentPos);

                switch (m_iDataType)
                {
                    case m_cWinds:
                        sgV1 = mps2knots(sgV1);
                        sgV2 += 180;
                        break;
                    case m_cCurrents:
                        sgV1 = kmph2knots(sgV1);
                        break;
                }

                VelocityType tVelocity = GetVVectors(sgV2, sgV1);
                iVal[0] = tVelocity.u;
                iResult = NetCDF.nc_put_var1_float(lID, lUID, aIndex, iVal);
                iVal[0] = tVelocity.v;
                iResult = NetCDF.nc_put_var1_float(lID, lVID, aIndex, iVal);
            }

            NetCDF.nc_close(lID);
        }
        catch (Exception ex)
        {
            m_sFilename = "";
        }
        finally
        {
            ResetForNewRequest();
            Finalize();
        }

        return m_sFilename;
    }

    private VelocityType GetVVectors(float dWDIR, float sdWSPD)
    {
        VelocityType Result;
        dWDIR = 90 - dWDIR;
        float dRadians = dWDIR * (float)(Math.PI / 180);
        Result.u = (sdWSPD * (float)Math.Cos(dRadians));
        Result.v = (sdWSPD * (float)Math.Sin(dRadians));
        return Result;
    }

    private int CreateDefaultNCFile(string sFilename, int iCells, ref int lTimeVarID, ref int lCellVarID, ref int lLatVarID, ref int lLonVarID, ref int lUID, ref int lVID)
    {
        int iResult = 0;
        int lStatus, lTimeID = 0, lCellsID = 0;
        int[] aDimIDs = new int[2];
        string sText;

        lStatus = NetCDF.nc_create(sFilename, 0, ref iResult);
        if (lStatus == 0)
            lStatus = NetCDF.nc_create(sFilename, 0, ref iResult);

        lStatus = NetCDF.nc_def_dim(iResult, "time", NetCDF.NC_UNLIMITED, ref lTimeID);
        lStatus = NetCDF.nc_def_dim(iResult, "ncells", iCells, ref lCellsID);
        aDimIDs[0] = lTimeID;
        aDimIDs[1] = lCellsID;
        lStatus = NetCDF.nc_def_var(iResult, "time", NetCDF.nc_type.NC_INT, 1, aDimIDs, ref lTimeVarID);
        sText = "time";
        lStatus = NetCDF.nc_put_att_text(iResult, lTimeVarID, "long_name", sText.Length, sText);
        sText = "seconds since 1970-01-01 00:00";
        lStatus = NetCDF.nc_put_att_text(iResult, lTimeVarID, "units", sText.Length, sText);
        sText = "UTC";
        lStatus = NetCDF.nc_put_att_text(iResult, lTimeVarID, "reference", sText.Length, sText);

        aDimIDs[0] = lCellsID;
        lStatus = NetCDF.nc_def_var(iResult, "ncells", NetCDF.nc_type.NC_INT, 1, aDimIDs, ref lCellVarID);
        sText = "cell";
        lStatus = NetCDF.nc_put_att_text(iResult, lCellVarID, "long_name", sText.Length, sText);

        lStatus = NetCDF.nc_def_var(iResult, "lat", NetCDF.nc_type.NC_FLOAT, 1, aDimIDs, ref lLatVarID);
        sText = "Cell latitude";
        lStatus = NetCDF.nc_put_att_text(iResult, lLatVarID, "long_name", sText.Length, sText);
        sText = "degrees_north";
        lStatus = NetCDF.nc_put_att_text(iResult, lLatVarID, "units", sText.Length, sText);

        lStatus = NetCDF.nc_def_var(iResult, "lon", NetCDF.nc_type.NC_FLOAT, 1, aDimIDs, ref lLonVarID);
        sText = "Cell longitude";
        lStatus = NetCDF.nc_put_att_text(iResult, lLonVarID, "long_name", sText.Length, sText);
        sText = "degrees_east";
        lStatus = NetCDF.nc_put_att_text(iResult, lLonVarID, "units", sText.Length, sText);

        aDimIDs[0] = lTimeID;
        aDimIDs[1] = lCellsID;
        lStatus = NetCDF.nc_def_var(iResult, "U", NetCDF.nc_type.NC_FLOAT, 2, aDimIDs, ref lUID);
        lStatus = NetCDF.nc_def_var(iResult, "V", NetCDF.nc_type.NC_FLOAT, 2, aDimIDs, ref lVID);
        if (m_iDataType == m_cWinds)
        {
            sText = "eastward wind velocity";
            lStatus = NetCDF.nc_put_att_text(iResult, lUID, "long_name", sText.Length, sText);
            sText = "northward wind velocity";
            lStatus = NetCDF.nc_put_att_text(iResult, lVID, "long_name", sText.Length, sText);            
        }
        else if (m_iDataType == m_cCurrents)
        {
            sText = "eastward current velocity";
            lStatus = NetCDF.nc_put_att_text(iResult, lUID, "long_name", sText.Length, sText);
            sText = "northward current velocity";
            lStatus = NetCDF.nc_put_att_text(iResult, lVID, "long_name", sText.Length, sText);            
        }
        sText = "Knots";
        lStatus = NetCDF.nc_put_att_text(iResult, lUID, "units", sText.Length, sText);
        lStatus = NetCDF.nc_put_att_text(iResult, lVID, "units", sText.Length, sText);
        sText = "99999.0";
        lStatus = NetCDF.nc_put_att_text(iResult, lUID, "missing_value", sText.Length, sText);
        lStatus = NetCDF.nc_put_att_text(iResult, lVID, "missing_value", sText.Length, sText);

        sText = "Created: " + DateTime.Now.ToString("MM/dd/yyyy HH:mm:ss") + " from NowCasting data";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "reference", sText.Length, sText);
        sText = "CF-1.0";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "Conventions", sText.Length, sText);
        sText = "U,V";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "default_view", sText.Length, sText);
        sText = "1";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "netcdf_class", sText.Length, sText);
        sText = "Multi-point, static, non-gridded";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "netcdf_class_description", sText.Length, sText);
        sText = "ncells";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "cell_dimension", sText.Length, sText);
        sText = "time";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "time_var", sText.Length, sText);
        sText = "1";
        lStatus = NetCDF.nc_put_att_text(iResult, NetCDF.NC_GLOBAL, "view_style", sText.Length, sText);

        lStatus = NetCDF.nc_enddef(iResult);

        return iResult;
    }

    private string GetNowcastError(int lError)
    {
        string sResult = "";
        switch (lError)
        {
            case 1:
                sResult = "Sub not found";
                break;
            case 2:
                sResult = "Incorrect Password";
                break;
            case 3:
                sResult = "Incorrect Registration Code";
                break;
            case 4:
                sResult = "License Not Found";
                break;
            case 5:
                sResult = "License Not Active";
                break;
            case 6:
                sResult = "License Expired";
                break;
            case 7:
                sResult = "License Not Started";
                break;
            case 8:
                sResult = "License Not Enough Shots";
                break;
            case 19:
                sResult = "Unknown Error";
                break;
            case 20:
                sResult = "No Records";
                break;
            case 21:
                sResult = "No Data";
                break;
            case 22:
                sResult = "Malformed Request";
                break;
            case 25:
                sResult = "Bad Raw Information";
                break;
            case 30:
                sResult = "Send HTTP Error";
                break;
            case 99:
                sResult = "Conversion Error";
                break;
            case 255:
                sResult = "Service Unavailable";
                break;
            case -1:
                sResult = "Not Initialized";
                break;
            case -2:
                sResult = "Not Interpreted";
                break;
            case -4:
                sResult = "Zip Failed";
                break;
            case -5:
                sResult = "Unzip Failed";
                break;
            case -6:
                sResult = "Parameter Error";
                break;
            case -7:
                sResult = "Invalid Blockstring";
                break;
            case -8:
                sResult = "No String";
                break;
            case -9:
                sResult = "Wrong Product Request";
                break;
            case -10:
                sResult = "No Record";
                break;
            case -11:
                sResult = "Local HTTP Error";
                break;
            case -12:
                sResult = "HTTP Initialization Error";
                break;
            case -13:
                sResult = "Transfer Not Finished";
                break;
            case -14:
                sResult = "HTTP No Transfer";
                break;
            case -15:
                sResult = "Service Not Reset";
                break;
            case -21:
                sResult = "RAS Connection Failed";
                break;
            case -22:
                sResult = "RAS Connected";
                break;
            default:
                sResult = "Not a Nowcasting Error";
                break;
        }

        return sResult;

    }

    private string GetGridBlocks2()
    {
        // Build string of lat/lon points based on given North-West Lowerleft(LL) and UpperRight(UR) corners.
        string strResult = "";
        int startX, startY;
        try
        {
            //' Rounded values of Lowerleft and UpperRight (x,y) pairs

            //' starting value for (x,y) pair
            startX = (int)m_dLongitude - 1;
            startY = (int)m_dLatitude;
            strResult = "";

            //' build string of lat/lon points
            for (int iy = 0; iy <= 2; iy++)
                for (int ix = 0; ix <= 2; ix++)
                    strResult += (startY + iy).ToString() + "," + (startX + ix).ToString() + ",";

            if (strResult != "")
                strResult = strResult.Substring(0, strResult.Length - 1);
        }
        catch
        {
            strResult = "";
        }
        return strResult;
    }
}
