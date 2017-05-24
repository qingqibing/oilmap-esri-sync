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
using System.Net;
using System.Collections.Generic;
using System.Xml;
using System.Diagnostics;

/// <summary>
/// Summary description for EDSProcessor
/// </summary>
public class EDSProcessor
{
    EDSService.EDS _EDSService;
	public EDSProcessor()
	{
        _EDSService = new EDSService.EDS();
	}

    public string GetDataSources(string sSubCode, string sDataType, double dWest, double dSouth, double dEast, double dNorth)
    {
        XmlDocument myDoc = new XmlDocument();
        XmlDocument myResult = new XmlDocument();
        string sResult = _EDSService.GetDataCoverage(sSubCode);
        if (!(sResult.ToUpper().Contains("ERROR")))
        {
            myDoc.LoadXml(sResult);
            XmlElement oRootNode = myResult.CreateElement("catalog");
            oRootNode.SetAttribute("version", "1.1");

            XmlNodeList myNodeList = myDoc.SelectNodes("catalog/dataset");
            foreach (XmlElement myElement in myNodeList)
            {
                double dLLX, dLLY, dURX, dURY;
                dLLX = double.Parse(myElement.GetAttribute("extentleft"));
                dLLY = double.Parse(myElement.GetAttribute("extentbottom"));
                dURX = double.Parse(myElement.GetAttribute("extentright"));
                dURY = double.Parse(myElement.GetAttribute("extenttop"));
                if ((myElement.GetAttribute("datatype").ToUpper() == sDataType.ToUpper()) &&
                    ((dLLX <= dEast) && (dURX >= dWest)) &&
                    ((dLLY <= dNorth) && (dURY >= dSouth)))
                {
                    XmlElement myNewElement = myResult.CreateElement("dataset");
                    foreach (XmlAttribute myAttribute in myElement.Attributes)
                    {
                        myNewElement.SetAttribute(myAttribute.Name, myAttribute.Value);
                    }
                    oRootNode.AppendChild(myNewElement);
                }
            }
            myResult.AppendChild(oRootNode);
        }

        return myResult.OuterXml;
    }

    public string GetDataSourceName(string sSubCode, int iID)
    {
        string sResult = "";
        XmlDocument myDoc = new XmlDocument();
        string sXML = _EDSService.GetDataCoverage(sSubCode);
        if (!(sXML.ToUpper().Contains("ERROR")))
        {
            myDoc.LoadXml(sXML);
            XmlElement myNode = (XmlElement)myDoc.SelectSingleNode("catalog/dataset[@id='" + iID.ToString() + "']");
            if (myNode != null)
                sResult = myNode.GetAttribute("source");
        }
        return sResult;
    }

    public string GetDataFile(string sSubCode, int iID, DateTime StartDate, DateTime EndDate, BoundingBox AOI)
    {
        //int iID = GetDataSourceID(sSubCode, sSource);
        string sSource = GetDataSourceName(sSubCode, iID);
        string sFilename = _EDSService.GetData(sSubCode, iID, sSource, 1, StartDate.ToString("yyyy-MM-ddTHH:mm:ss"), EndDate.ToString("yyyy-MM-ddTHH:mm:ss"), AOI.west, AOI.south, AOI.east, AOI.north, false);
        return sFilename;
    }

    public string GetStatus(string sFilename)
    {
        DateTime nowDate = DateTime.Now;
        string sText = "IN_PROCESS";
        string Result = "Error";
        try
        {
            while (sText.Contains("IN_PROCESS"))
            {
                sText = _EDSService.GetStatus(sFilename);
                if (sText.Length > 0)
                {
                    if (sText.Contains("IN_PROCESS"))
                    {
                        nowDate = DateTime.Now;
                    }
                }
                else
                {
                    sText = "IN_PROCESS";
                    if (nowDate.AddSeconds(60) < DateTime.Now)
                    {
                        sText = "TIMEOUT";
                        break;
                    }
                }
                System.Threading.Thread.Sleep(500);
            }

            if (sText.Contains("COMPLETE"))
            {
                Result = "COMPLETE";
            }
        }
        catch (Exception ex)
        {
            Result = "Error: " + ex.Message;
        }
        return Result;
    }

    public void DownloadDataFile(string sOutFilename, string sFilename)
    {
        string sURL = ConfigurationManager.AppSettings["EDSOutput"] + @"/" + sFilename;
        FileStream fs = null;
        Stream sChunks = null;
        try
        {
            fs = new FileStream(sOutFilename, FileMode.Create, FileAccess.Write);
            WebRequest wRemote = WebRequest.Create(sURL);
            WebResponse myWebResponse = wRemote.GetResponse();
            sChunks = myWebResponse.GetResponseStream();
            byte[] bBuffer = new byte[256];
            int iBytesRead = sChunks.Read(bBuffer, 0, 256);
            int iTotalBytesRead = 0;
            while (iBytesRead != 0)
            {
                fs.Write(bBuffer, 0, iBytesRead);
                iTotalBytesRead += iBytesRead;
                iBytesRead = sChunks.Read(bBuffer, 0, 256);
            }
        }
        catch (Exception ex)
        {
            
        }
        finally
        {
            if (sChunks != null)
                sChunks.Close();
            sChunks = null;
            if (fs != null)
                fs.Close();
            fs = null;
        }

    }
}
