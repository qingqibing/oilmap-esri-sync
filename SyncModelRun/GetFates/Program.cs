using System;
using System.Collections.Generic;
using System.Text;
using System.Data.Odbc;
using System.IO;
using System.Globalization;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.Xml;

namespace GetFates
{
    class Program
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

        private static string m_sFilename = "";
        private static OdbcConnection _OdbcConnection;
        private static string m_sScenario;
        private static DateTime _StartDate;

        static void Main(string[] args)
        {
            m_sFilename = args[0];
            m_sScenario = Path.GetFileNameWithoutExtension(m_sFilename);
            _StartDate = GetScenarioStartDate(m_sFilename, m_sScenario);
            GetScenarioTimeSeries();
        }

        private static DateTime GetScenarioStartDate(string sFatefile, string sScenario)
        {
            DateTime Result;

            string sFilename = Path.GetDirectoryName(Path.GetDirectoryName(sFatefile)) + "\\Outdata\\" + sScenario + ".INP";
            int iYear = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Year", ""));
            int iMonth = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Month", ""));
            int iDay = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Day", ""));
            int iHour = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Hour", ""));
            int iMinute = Convert.ToInt32(GetIniFileString(sFilename, "OILMAPW", "Start Minute", ""));
            Result = new DateTime(iYear, iMonth, iDay, iHour, iMinute, 0);
            return Result;
        }

        private static OdbcDataReader OpenDataReader()
        {
            //string sFilename = OutputPath + "\\FATES\\" + ScenarioName + ".dbf";
            try
            {
                if (!(File.Exists(m_sFilename)))
                    return null;

                if (Path.GetFileNameWithoutExtension(m_sFilename).Length > 8)
                {
                    string sTemp = m_sFilename;
                    m_sFilename = Path.GetDirectoryName(m_sFilename) + "\\TempDBF.dbf";
                    if (File.Exists(m_sFilename))
                        File.Delete(m_sFilename);
                    File.Copy(sTemp, m_sFilename);
                }

                _OdbcConnection = new OdbcConnection();
                _OdbcConnection.ConnectionString = "DSN=Visual FoxPro Tables;SourceType=DBF;SourceDB=" + Path.GetDirectoryName(m_sFilename) + ";Exclusive=No; Collate=Machine;NULL=NO;DELETED=NO;BACKGROUNDFETCH=NO;"; //"Driver={Microsoft Visual FoxPro Driver};DriverID=277;Dbq=" + OutputPath + "\\FATES;"; // "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + OutputPath + "\\FATES\\" + "; Extended Properties=dBASE IV;User ID=Admin;Password=;";
                _OdbcConnection.Open();
                OdbcCommand oCmd = _OdbcConnection.CreateCommand();
                oCmd.CommandText = @"SELECT * FROM " + m_sFilename;
                OdbcDataReader dr = oCmd.ExecuteReader();
                return dr;
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetFates.OpenDataReader\r\n" + ex.Message);
                return null;
            }
        }

        private static void CloseDataConnection()
        {
            //_OleDbConnection.Close();
            _OdbcConnection.Close();
        }

        private static void GetScenarioTimeSeries()
        {
            try
            {
                XmlDocument oDoc = new XmlDocument();
                XmlElement oRootNode = oDoc.CreateElement("Fates");                
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

                        XmlElement oNode = oDoc.CreateElement("DataPoint");
                        oNode.SetAttribute("time", thisDate.ToString("yyyy/MM/dd HH:mm"));

                        XmlElement oNode2 = oDoc.CreateElement("Surface");
                        oNode2.SetAttribute("unit", "Tonnes");
                        oNode2.InnerText = dSurface.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("WaterCol");
                        oNode2.SetAttribute("unit", "Tonnes");
                        oNode2.InnerText = dWaterCol.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Ashore");
                        oNode2.SetAttribute("unit", "Tonnes");
                        oNode2.InnerText = dAshore.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Evaporated");
                        oNode2.SetAttribute("unit", "Tonnes");
                        oNode2.InnerText = dEvaporated.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Thickness");
                        oNode2.SetAttribute("unit", "m");
                        oNode2.InnerText = dWaterCol.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Area");
                        oNode2.SetAttribute("unit", "km²");
                        oNode2.InnerText = dAshore.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Viscosity");
                        oNode2.SetAttribute("unit", "cSt");
                        oNode2.InnerText = dEvaporated.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Volume");
                        oNode2.SetAttribute("unit", "m³");
                        oNode2.InnerText = dEvaporated.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oNode2 = oDoc.CreateElement("Density");
                        oNode2.SetAttribute("unit", "");
                        oNode2.InnerText = dEvaporated.ToString(CultureInfo.CreateSpecificCulture("en-US"));
                        oNode.AppendChild(oNode2);

                        oRootNode.AppendChild(oNode);

                    }
                    dr.Close();
                }
                CloseDataConnection();
                oDoc.AppendChild(oRootNode);

                string sNewFile = Path.GetDirectoryName(m_sFilename) + "\\" + m_sScenario + ".FTE";
                using (StreamWriter sw = new StreamWriter(sNewFile))
                {
                    sw.Write(Result);
                    //sw.Write(oDoc.OuterXml);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetFates.GetScenarioTimeSeries\r\n" + ex.Message);
                EventLog.WriteEntry("GetScenarioTimeSeries", ex.Message, EventLogEntryType.Error);
            }
        }

        private static string GetIniFileString(string iniFile, string category, string key, string defaultValue)
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
}
