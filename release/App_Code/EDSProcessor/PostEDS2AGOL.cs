using ASA.EDS.Data.ASAnc;
using ASA.EDS.Data;
using ASA.EDS.Common;
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using System.Configuration;
using System.Web;
using System.Net;
using System.Web.Caching;
using System.IO;
using System.Text;
using System.Collections;

using ucar.ma2;
using ucar.nc2;
using java.util;
using NetCDFObjAGOL;

namespace Aggregator
{
    public class PostEDS2AGOL
    {
        //private const short MISSING_VALUE = -9999;
        //private const float MISSING_VALUE_F = -9999f;
        //private const float MISSING_VAL_CHECK = -999F;
        //private const float SCALE_FACTOR = 1000f; 

        [DllImport("kernel32", SetLastError = true)]
        static extern IntPtr LoadLibrary(string IpFileName);

        private static readonly string urlOilMapFeatureService = ConfigurationManager.AppSettings["urlOilMapFeatureService"];
        private static readonly string publishMode = ConfigurationManager.AppSettings["publishMode"];
        //private static readonly string urlPortalRoot = ConfigurationManager.AppSettings["urlPortalRoot"];
        //private static readonly string agoTokenService = String.Concat(urlPortalRoot, ConfigurationManager.AppSettings["agoTokenService"]);
        //private static readonly string agoUser = ConfigurationManager.AppSettings["agoUser"];
        //private static readonly string agoPassword = ConfigurationManager.AppSettings["agoPassword"];
        private static readonly string agsTokenService = ConfigurationManager.AppSettings["agsTokenService"];
        private static readonly string agsUser = ConfigurationManager.AppSettings["agsUser"];
        private static readonly string agsPassword = ConfigurationManager.AppSettings["agsPassword"];

        [Serializable]
        public class Token
        {
            public string token { get; set; }
            public long expires { get; set; }
        }

        public PostEDS2AGOL()
        {
        }

        public void ImportJavaLibrary(string javaDLL_)
        {
            if (Environment.Version.Major >= 4)
            {
                LoadLibrary(Path.Combine(javaDLL_, "vjsnativ.dll"));
            }
        }

        public void ProcessEDS2AGOL(string ncFileName_, string dllPath, string typeFile)
        {
            ImportJavaLibrary(dllPath);
            
            try
            {
                // Read the data from the NetCDF file
                NetcdfFile currentFile = new NetcdfFile(ncFileName_);
                
                Iterator dimensions = currentFile.getDimensionIterator();

                Variable varTime = currentFile.findVariable("time");
                ucar.ma2.Array timeVals = varTime.read();
                Index timeIndex = timeVals.getIndex();
                
                Variable varLat = currentFile.findVariable("lat");
                ucar.ma2.Array latVals = varLat.read();
                Index latIndex = latVals.getIndex();
                //int[] shapeLats = latVals.getShape();

                Variable varLon = currentFile.findVariable("lon");
                ucar.ma2.Array lonVals = varLon.read();
                Index lonIndex = lonVals.getIndex();

                int timeDimSize = -1;
                int ncellDimSize = -1;
                int serviceIDType;

                Dimension dim;
                string varName;
                int dimSize;

                while (dimensions.hasNext())
                {
                    dim = (Dimension)dimensions.next();

                    varName = dim.getName();
                    dimSize = dim.getLength();

                    if (varName.Equals("time"))
                    {
                        timeDimSize = dimSize;
                    }
                    else if (varName.Equals("ncell") || varName.Equals("ncells"))
                    {
                        ncellDimSize = dimSize;
                    }                    
                }

                ucar.nc2.Attribute tUnits = varTime.findAttribute("units");

                //Winds or Currents file U + V
                Variable varV;
                Variable varU;
                if (typeFile == "current")
                {
                    varU = currentFile.findVariable("U");
                    varV = currentFile.findVariable("V");
                    serviceIDType = 3;

                }
                else
                {
                    varU = currentFile.findVariable("wind_u");
                    varV = currentFile.findVariable("wind_v");
                    serviceIDType = 4;
                }
                
                System.Collections.ArrayList postNetCDFGroup = new System.Collections.ArrayList ();
                
                // Loop through time steps and create time
                for (int t = 0; t < timeDimSize; t++)
                {
                    //Get time
                    double timeVal = timeVals.getDouble(timeIndex.set(t));

                    //Add minutes to time
                    DateTime ncEpoch = new DateTime(2000, 01, 01, 00, 00, 00);
                    DateTime dataTime = ncEpoch.AddMinutes(timeVal);
                    //if (tUnits.name.Contains("minutes")){}

                    ucar.ma2.Array aU;
                    ucar.ma2.Array aV;

                    int[] shapeU = varU.getShape();
                    int[] shapeV = varV.getShape();
                    int[] originU = new int[varU.getRank()];
                    int[] originV = new int[varV.getRank()];

                    originU[0] = t;
                    shapeU[0] = 1;
                    originV[0] = t;
                    shapeV[0] = 1;
                    if (t == 0)
                    {
                        int[] priorOriginU;
                        priorOriginU = new int[varU.getRank()];
                        priorOriginU[0] = timeDimSize-1;
                        aU = varU.read(priorOriginU, shapeU);

                        int[] priorOriginV;
                        priorOriginV = new int[varV.getRank()];
                        priorOriginV[0] = timeDimSize - 1;
                        aV = varV.read(priorOriginV, shapeV);
                    }
                    else
                    {
                        aU = varU.read(originU, shapeU);
                        aV = varV.read(originV, shapeV);
                    }
                    Index uIndex = aU.getIndex();
                    Index vIndex = aV.getIndex();
                    for (int i = 0; i < ncellDimSize; i++)
                    {
                        double xLon = lonVals.getDouble(lonIndex.set(i));
                        double yLat = latVals.getDouble(latIndex.set(i));
                        double uValu = aU.getDouble(uIndex.set(0,i));
                        double vValu = aV.getDouble(vIndex.set(0, i));

                        while (xLon > 360f)
                        {
                            xLon -= 360f;
                        }
                        if (uValu != 0 && uValu != -9999)
                        {
                            NetCDFJSON netcdfObj = new NetCDFJSON { };
                            NetCDFObjAGOL.Geometry netcdfGeom = new NetCDFObjAGOL.Geometry();
                            NetCDFObjAGOL.Attributes netcdfAttr = new NetCDFObjAGOL.Attributes();
                            netcdfGeom.spatialReference = new NetCDFObjAGOL.Spatialref();

                            netcdfGeom.x = Math.Round(xLon, 4);
                            netcdfGeom.y = Math.Round(yLat, 4);
                            netcdfAttr.DateTime = dataTime.Year.ToString() + "-" + paddingDate(dataTime.Month) + "-" + paddingDate(dataTime.Day) + " " + paddingDate(dataTime.Hour) + ":" + paddingDate(dataTime.Minute) + ":00";
                            netcdfAttr.SCENARIO_ID = Path.GetFileNameWithoutExtension(ncFileName_);
                            netcdfAttr.ncells = i.ToString();
                            //netcdfAttr.U = Math.Round(uValu, 4).ToString();
                            //netcdfAttr.V = Math.Round(vValu, 4).ToString();
                            //calculate Speed
                            netcdfAttr.Speed = Math.Round(Math.Sqrt(uValu * uValu + vValu * vValu), 3).ToString();
                            //calculate direction and convert from radians
                            //Double dir = vValu / uValu;
                            //Double dir2 = (Math.Atan(dir) * 180 / Math.PI) + 360;
                            //netcdfAttr.Direction = Math.Round(dir2, 2).ToString();

                            //(y,x)
                            double dir = Math.Atan2(vValu, uValu) * (180.0 / Math.PI);

                            // Covernt to compass coords
                            dir = 90.0 - dir;

                            if (dir < 0)
                            {
                                dir = 360.0 + dir;
                            }
                            netcdfAttr.Direction = Math.Round(dir, 2).ToString();

                            netcdfObj.geometry = netcdfGeom;
                            netcdfObj.attributes = netcdfAttr;
                            postNetCDFGroup.Add(netcdfObj);

                            if (postNetCDFGroup.Count > 4500)
                            {
                                //post2AGOL(postNetCDFGroup, serviceIDType, ncFileName_);
                                InsertFeatures(serviceIDType.ToString(), new JavaScriptSerializer().Serialize(postNetCDFGroup).ToString(), GetAGOToken());
                                postNetCDFGroup.Clear();
                            }
                        }
                    }
                }

                //post2AGOL(postNetCDFGroup, serviceIDType, ncFileName_);
                InsertFeatures(serviceIDType.ToString(), new JavaScriptSerializer().Serialize(postNetCDFGroup).ToString(), GetAGOToken());
            }
            catch (Exception ex)
            {
                string t = ex.ToString();
            }
        }

        public void post2AGOL(Object DataObj, int serviceNumber, string urlName)
        {
            string postLineData = "layerID=" + serviceNumber + "&features=" + new JavaScriptSerializer().Serialize(DataObj);
            //string postLineData = string.Format("f=json&features={0}", new JavaScriptSerializer().Serialize(DataObj));
            
            byte[] byteArray;
            byteArray = Encoding.UTF8.GetBytes(postLineData);

            //Construct Post request
            HttpWebRequest request = HttpWebRequest.Create(ConfigurationManager.AppSettings["AGOLProxyInsert"]) as HttpWebRequest;
            //var url = ConfigurationManager.AppSettings["urlOilMapFeatureService"] + serviceNumber + "/addFeatures?token=" + GetAGOToken();
            
            //HttpWebRequest request = HttpWebRequest.Create(url) as HttpWebRequest;
            
            request.Method = "POST";
            request.ContentType = "application/x-www-form-urlencoded";
            request.ContentLength = postLineData.Length;
            //request.ContentLength = byteArray.Length;

            //using (StreamWriter requestWriter2 = new StreamWriter(request.GetRequestStream()))
            using (Stream requestWriter2 = request.GetRequestStream())
            {
                //requestWriter2.Write(postLineData);
                requestWriter2.Write(byteArray, 0, byteArray.Length);
                //streamWriter.Close();
            }
            //var httpResponse = (HttpWebResponse)request.GetResponse();
            //using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            //{
            //    var result = streamReader.ReadToEnd();
            //    //Write out to LogFile
            //    string[] delimiters = new string[] { "\\WORLD" };
            //    string[] urlBeginning = urlName.Split(delimiters, StringSplitOptions.None);
            //    using (StreamWriter sw = new StreamWriter(urlBeginning[0]+"\\LogFile\\LogFile.txt", true))
            //    {
            //        sw.WriteLine(DateTime.Now.ToString() + ":" + result + postLineData);
            //    }
            //    //for Microsoft EventViewer Log
            //    //EventLog.WriteEntry("ModelAGOLRUN", result + postLineData, EventLogEntryType.Error);
            //}
        }

        public static String GetAGOToken()
        {
            //testing
            string myToken = HttpRuntime.Cache["AGO_Token"] as string;
            if (string.IsNullOrEmpty(myToken))
            {
                myToken = GenerateAGOToken();
            }

            return myToken;
        }

        public static void ReportRemovedAGOTokenCallback(String key, object value,
            System.Web.Caching.CacheItemRemovedReason removedReason)
        {
            GenerateAGOToken();
        }

        public static string DoPostForString(string url, string postData)
        {
            // create the POST request
            HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
            webRequest.Method = "POST";
            webRequest.ContentType = "application/x-www-form-urlencoded";
            webRequest.ContentLength = postData.Length;

            // POST the data
            using (StreamWriter requestWriter2 = new StreamWriter(webRequest.GetRequestStream()))
            {
                requestWriter2.Write(postData);
            }

            //  This actually does the request and gets the response back
            HttpWebResponse resp = (HttpWebResponse)webRequest.GetResponse();

            string responseData = string.Empty;

            using (StreamReader responseReader = new StreamReader(webRequest.GetResponse().GetResponseStream()))
            {
                // dumps the HTML from the response into a string variable
                responseData = responseReader.ReadToEnd();
            }

            return responseData;
        }

        //this is for more asyn
        public void DoPostForStringInsert(string url, string postData)
        {
            // create the POST request
            HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
            webRequest.Method = "POST";
            webRequest.ContentType = "application/x-www-form-urlencoded";
            webRequest.ContentLength = postData.Length;

            // POST the data
            using (StreamWriter requestWriter2 = new StreamWriter(webRequest.GetRequestStream()))
            {
                requestWriter2.Write(postData);
            }

            //  This actually does the request and gets the response back
            //HttpWebResponse resp = (HttpWebResponse)webRequest.GetResponse();

            //string responseData = string.Empty;

            //using (StreamReader responseReader = new StreamReader(webRequest.GetResponse().GetResponseStream()))
            //{
            //    // dumps the HTML from the response into a string variable
            //    responseData = responseReader.ReadToEnd();
            //}

            //return responseData;
        }

        public static string GenerateAGOToken()
        {
            string postData = string.Format("username={0}&password={1}&referer=https://www.arcgis.com&expiration=524160", ConfigurationManager.AppSettings["agoUser"], ConfigurationManager.AppSettings["agoPassword"]);

            //urlPortalRoot
            //agoTokenService
            var serviceTokenURL = ConfigurationManager.AppSettings["urlPortalRoot"] + ConfigurationManager.AppSettings["agoTokenService"];
            string agoTokenData = DoPostForString(serviceTokenURL, postData);

            JavaScriptSerializer js = new JavaScriptSerializer();

            Token agoToken = js.Deserialize<Token>(agoTokenData);

            //set cache item to expire 2 minutes before token expiration (usually 2 hours)
            HttpRuntime.Cache.Insert(
                "AGO_Token",
                agoToken.token,
                null,
                Cache.NoAbsoluteExpiration,
                new TimeSpan(23, 58, 0),
                CacheItemPriority.Default,
                new CacheItemRemovedCallback(ReportRemovedAGOTokenCallback));

            return agoToken.token;
        }

        private static string paddingDate(int num)
        {
            if (num < 10)
            {
                return "0" + num;
            }
            else
            {
                return num.ToString();
            }
        }

        public static String GetAGSToken()
        {
            //testing
            string myToken = HttpRuntime.Cache["AGS_Token"] as string;
            if (string.IsNullOrEmpty(myToken))
            {
                myToken = GenerateAGSToken();
            }

            return myToken;
        }

        public static void ReportRemovedAGSTokenCallback(String key, object value,
            System.Web.Caching.CacheItemRemovedReason removedReason)
        {
            GenerateAGSToken();
        }

        public static string GenerateAGSToken()
        {
            //expiration=524160 (364 days)
            string postData = string.Format("f=json&username={0}&password={1}&client=requestip&expiration=524160", agsUser, agsPassword);

            string agsTokenData = DoPostForString(agsTokenService, postData);
            //{"token":"C4_fVBfIE8ULhZXrMuvFkwJ-i-u2E-XozErt8fhOqfy-3SHpeeoQStBDQN_NNtH4","expires":1382387566490}

            JavaScriptSerializer js = new JavaScriptSerializer();

            //Token oAuth2Token = js.Deserialize<Token>(responseData);
            Token agsToken = js.Deserialize<Token>(agsTokenData);

            //set cache item to expire 2 minutes before token expiration (usually 2 hours)
            //expiration=524160 (364 days)
            HttpRuntime.Cache.Insert(
                "AGS_Token",
                agsToken.token,
                null,
                Cache.NoAbsoluteExpiration,
                new TimeSpan(363, 23, 58, 0),
                CacheItemPriority.Default,
                new CacheItemRemovedCallback(ReportRemovedAGSTokenCallback));

            return agsToken.token;
        }

        //insert features (layer ID, feature JSON)
        public void InsertFeatures(string layerID, string features, string agoToken)
        {
            string token = "";
            //get fs URL from config
            if (publishMode.Equals("ago"))
            {
                if (String.IsNullOrEmpty(agoToken))
                {
                    //TEST: IF NO AGOTOKEN SENT IN, CREATE ONE
                    token = GetAGOToken();
                    if (string.IsNullOrEmpty(token))
                    {
                        throw new WebException("No AGO token available; Tried to generate token but failed.", WebExceptionStatus.TrustFailure);
                    }
                }
                else
                {
                    token = agoToken;
                }
            }
            else
            {
                //get ags token
                string agsToken = GetAGSToken();
                if (string.IsNullOrEmpty(agsToken))
                {
                    throw new WebException("No ArcGIS Server token available", WebExceptionStatus.TrustFailure);
                }
                token = agsToken;
            }

            string responseString = "";
            
            string postUrl = string.Format("{0}/{1}/addFeatures?token={2}", urlOilMapFeatureService, layerID, token);
            //string postUrl = string.Format("{0}/{1}/addFeatures?", urlOilMapFeatureService, layerID);
            string postData = string.Format("f=json&features={0}", features);

            //call insert features on fs
            try
            {
                //responseString = DoPostForString(string.Concat(postUrl, token), postData);
                //DoPostForStringInsert(string.Concat(postUrl, token), postData);
                DoPostForStringInsert(postUrl, postData);
                //WHILE EXPLORING BUG OF INVALID TOKENS, ASSUMING ALL ERRORS ARE TOKEN RELATED AND FOR NOW, 
                //REGENERATING TOKEN REGARDLESS OF UNDERLYING CAUSE; SEND REST BACK TO CLIENT
                if (responseString.ToLower().IndexOf("error") > -1)
                {
                    // _log.Error("Caught error in response: " + responseString);

                    //token in cache is invalid... regenerate and store in cache
                    if (publishMode.Equals("ago"))
                    {
                        //use AGO admin credentials to generate new token
                        token = GenerateAGOToken();
                    }
                    else
                    {
                        token = GenerateAGSToken();
                    }
                    //_log.Error("Caught invalid token error; generated new token: " + token);

                    //try again
                    responseString = DoPostForString(string.Concat(postUrl, token), postData);
                }
            }
            catch (Exception ex)
            {
                responseString = "error"; // LogExceptionReturnJSON(500, ex.Message, ex.StackTrace);
            }
            //return responseString;
        }
    }
}