using System;
using System.Web;
using System.Collections;
using System.Web.Services;
using System.Web.Services.Protocols;
using System.Xml;
using System.IO;
using System.Globalization;
using System.Diagnostics;
using System.Drawing;
using System.Collections.Generic;


/// <summary>
/// Summary description for AddResponse
/// </summary>
[WebService(Namespace = "http://staging.asascience.com/ModelService")]
[WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
public class AddResponse : System.Web.Services.WebService
{
    private struct RspObject
    {
        public string Name;
        public short type;
        public float Lon1;
        public float Lat1;
        public float Lon2;
        public float Lat2;
        public int StartTime;
        public int EndTime;
        public short tankage;
        public short Delay;
        public short Perc_effective;
        public short speed;
        public short status;
        public short endurance;
        public short on;
        public short area;
        public short currthrs;
        public short wavethrs;
        public short StartTimeOld;
        public short EndTimeOld;
        public short opspeed;
        public short turntime;
        public short swathwidth;
        public float minmass;
        public short searchtype;
        public short ntrips;
        public short i1;
        public short i2;
        public short i3;
    }

    public AddResponse()
    {

    }

    [WebMethod]
    public string AddResponseObject(string sLocation, string sScenario, string sResponseObject, int iResponseType, bool bRunModel)
    {
        string sResult = "";
        switch (iResponseType)
        {
            case 0: //booms
                sResult = AddBoomToScenario(sLocation, sScenario, sResponseObject);
                break;

            case 1: //overflight polygons
                sResult = AddOverflightToScenario(sLocation, sScenario, sResponseObject);
                break;
        }

        if (bRunModel)
            RunOilModel(sLocation, sScenario);

        return sResult;
    }

    private string AddOverflightToScenario(string sLocation, string sScenario, string sResponseObject)
    {
        XmlDocument oDoc = new XmlDocument();
        oDoc.LoadXml(sResponseObject);

        string sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        string sResponseFile = sWebPath + "\\ModelData\\" + sLocation + "\\Rundata\\" + sScenario + ".RLW";

        if (File.Exists(sResponseFile))
            File.Delete(sResponseFile);

        XmlElement oRootNode = (XmlElement)oDoc.SelectSingleNode("overflights");
        XmlElement oPolygons = (XmlElement)oRootNode.SelectSingleNode("./polygons");

        using (TextWriter tw = new StreamWriter(File.Open(sResponseFile, FileMode.Create)))
        {
            XmlNodeList oList = oPolygons.SelectNodes("./ring");
            foreach (XmlElement oPolyline in oList)
            {
                XmlElement oNode = (XmlElement)oPolyline.SelectSingleNode("./name");
                string sName = oNode.InnerText.PadRight(20);
                oNode = (XmlElement)oPolyline.SelectSingleNode("./time_utc");
                int iStartTime = GetTimeFromString(oNode.InnerText);
                oNode = (XmlElement)oPolyline.SelectSingleNode("./percentoil");
                double dPercOil = double.Parse(oNode.InnerText);

                double xMin = 99999;
                double yMin = 99999;
                double xMax = -99999;
                double yMax = -99999;
                List<PointF> aPoints = new List<PointF>();
                XmlNodeList oRingList = oPolyline.SelectNodes("./ringpoint");
                for (int i = 1; i <= oRingList.Count; i++)
                {
                    XmlElement oRingNode = (XmlElement)oPolyline.SelectSingleNode("./ringpoint[@id='" + i.ToString() + "']");
                    XmlElement oPointNode = (XmlElement)oRingNode.SelectSingleNode("./x");
                    PointF myPoint = new PointF();
                    myPoint.X = float.Parse(oPointNode.InnerText);
                    oPointNode = (XmlElement)oRingNode.SelectSingleNode("./y");
                    myPoint.Y  = float.Parse(oPointNode.InnerText);
                    aPoints.Add(myPoint);

                    if (myPoint.X < xMin)
                        xMin = myPoint.X;
                    if (myPoint.Y < yMin)
                        yMin = myPoint.Y;
                    if (myPoint.X > xMax)
                        xMax = myPoint.X;
                    if (myPoint.Y > yMin)
                        yMax = myPoint.Y;
                }

                tw.WriteLine(iStartTime.ToString());
                tw.WriteLine(dPercOil.ToString());
                tw.WriteLine("{0} {1} {2} {3} {4}", aPoints.Count, xMin, yMin, xMax, yMax);
                foreach (PointF myPoint in aPoints)
                    tw.WriteLine("{0} {1}", myPoint.X, myPoint.Y);
            }
        }
        return sWebPath + "\\ModelData\\" + sLocation + "\\Outdata\\" + sScenario + ".INP";
    }

    private void RunOilModel(string sLocation, string sScenario)
    {
        string sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        string sExePath = sWebPath + "\\ModelData\\"+sLocation+"\\OilModel\\oilmodel.exe";
        string sInpFile = sWebPath + "\\ModelData\\" + sLocation + "\\Rundata\\" + sScenario + ".INP";
        Process modelProcess = new Process();
        modelProcess.StartInfo.FileName = String.Format("\"{0}\"", sExePath);
        modelProcess.StartInfo.CreateNoWindow = false;
        modelProcess.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
        modelProcess.StartInfo.ErrorDialog = false;
        modelProcess.StartInfo.Arguments = String.Format("\"{0}\"", sInpFile);
        modelProcess.Start();
        modelProcess.WaitForExit();
    }

    private string AddBoomToScenario(string sLocation, string sScenario, string sResponseObject)
    {
        XmlDocument oDoc = new XmlDocument();
        oDoc.LoadXml(sResponseObject);

        string sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        string sResponseFile = sWebPath + "\\ModelData\\" + sLocation + "\\Response\\" + sScenario + ".NO2";

        if (File.Exists(sResponseFile))
            File.Delete(sResponseFile);

        XmlElement oRootNode = (XmlElement)oDoc.SelectSingleNode("booms");
        XmlElement oPolylines = (XmlElement)oRootNode.SelectSingleNode("./polylines");

        using (BinaryWriter bw = new BinaryWriter(File.Open(sResponseFile, FileMode.Create)))
        {            
            XmlNodeList oList = oPolylines.SelectNodes("./polyline");
            foreach (XmlElement oPolyline in oList)
            {
                RspObject myObject = new RspObject();
                XmlElement oNode = (XmlElement)oPolyline.SelectSingleNode("./name");
                myObject.Name = oNode.InnerText.PadRight(20);
                myObject.i1 = short.Parse(oPolyline.GetAttribute("id"));
                oNode = (XmlElement)oPolyline.SelectSingleNode("./start_utc");
                myObject.StartTime = GetTimeFromString(oNode.InnerText);
                oNode = (XmlElement)oPolyline.SelectSingleNode("./end_utc");
                myObject.EndTime = GetTimeFromString(oNode.InnerText);
                oNode = (XmlElement)oPolyline.SelectSingleNode("./currentthreshold");
                myObject.currthrs = (short)double.Parse(oNode.InnerText);
                oNode = (XmlElement)oPolyline.SelectSingleNode("./wavethreshold");
                myObject.wavethrs = (short)double.Parse(oNode.InnerText);
                XmlNodeList oLineList = oPolyline.SelectNodes("./linepoint");
                for (int i = 1; i < oLineList.Count; i++)
                {
                    XmlElement oLineNode = (XmlElement)oPolyline.SelectSingleNode("./linepoint[@id='" + i.ToString() + "']");
                    XmlElement oPointNode = (XmlElement)oLineNode.SelectSingleNode("./x");
                    myObject.Lon1 = float.Parse(oPointNode.InnerText);
                    oPointNode = (XmlElement)oLineNode.SelectSingleNode("./y");
                    myObject.Lat1 = float.Parse(oPointNode.InnerText);
                    oLineNode = (XmlElement)oPolyline.SelectSingleNode("./linepoint[@id='" + (i + 1).ToString() + "']");
                    oPointNode = (XmlElement)oLineNode.SelectSingleNode("./x");
                    myObject.Lon2 = float.Parse(oPointNode.InnerText);
                    oPointNode = (XmlElement)oLineNode.SelectSingleNode("./y");
                    myObject.Lat2 = float.Parse(oPointNode.InnerText);
                    WriteToFile(bw, myObject);
                }
            }
        }
        return sWebPath + "\\ModelData\\" + sLocation + "\\Outdata\\" + sScenario + ".INP";
    }

    private void WriteToFile(BinaryWriter bw, RspObject myObject)
    {
        bw.Write(myObject.Name);
        bw.Write(myObject.type);
        bw.Write(myObject.Lon1);
        bw.Write(myObject.Lat1);
        bw.Write(myObject.Lon2);
        bw.Write(myObject.Lat2);
        bw.Write(myObject.StartTime);
        bw.Write(myObject.EndTime);
        bw.Write(myObject.tankage);
        bw.Write(myObject.Delay);
        bw.Write(myObject.Perc_effective);
        bw.Write(myObject.speed);
        bw.Write(myObject.status);
        bw.Write(myObject.endurance);
        bw.Write(myObject.on);
        bw.Write(myObject.area);
        bw.Write(myObject.currthrs);
        bw.Write(myObject.wavethrs);
        bw.Write(myObject.StartTimeOld);
        bw.Write(myObject.EndTimeOld);
        bw.Write(myObject.opspeed);
        bw.Write(myObject.turntime);
        bw.Write(myObject.swathwidth);
        bw.Write(myObject.minmass);
        bw.Write(myObject.searchtype);
        bw.Write(myObject.ntrips);
        bw.Write(myObject.i1);
        bw.Write(myObject.i2);
        bw.Write(myObject.i3);
    }

    private int GetTimeFromString(string sUTCTime)
    {
        DateTime thisTime = DateTime.ParseExact(sUTCTime, "yyyyMMddTHHmm", CultureInfo.InvariantCulture);
        DateTime baseDate = new DateTime(1979, 12, 31);

        TimeSpan mySpan = thisTime.Subtract(baseDate);
        return (int)mySpan.TotalMinutes;
    }

}

