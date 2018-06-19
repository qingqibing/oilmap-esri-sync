using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using ESRI.ArcGIS.Client;
using ESRI.ArcGIS.Client.Geometry;
using ESRI.ArcGIS.Client.Tasks;
using System.Net;
using System.IO;
using System.Web;
using System.Web.Script.Serialization;
using System.Web.Caching;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Web.Script.Serialization;

namespace ManageScenariosWPF
{
    public partial class MainWindow : Window
    {
        private Graphic _lastGraphic;
        private static ESRI.ArcGIS.Client.Projection.WebMercator _mercator =
                new ESRI.ArcGIS.Client.Projection.WebMercator();

        private BackgroundWorker backgroundWorker1;
        public String UrlFeatureService;
        public String UrlFeatureServiceToken;

        public MainWindow()
        {
            InitializeComponent();
            InitializeBackgroundWorker();
        }

        // Set up the BackgroundWorker object by  
        // attaching event handlers.  
        private void InitializeBackgroundWorker()
        {
            backgroundWorker1 = new BackgroundWorker();
            backgroundWorker1.WorkerReportsProgress = true;
            backgroundWorker1.WorkerSupportsCancellation = true;

            backgroundWorker1.DoWork += new DoWorkEventHandler(backgroundWorker1_DoWork);
            backgroundWorker1.RunWorkerCompleted += new RunWorkerCompletedEventHandler(backgroundWorker1_RunWorkerCompleted);
            backgroundWorker1.ProgressChanged += new ProgressChangedEventHandler(backgroundWorker1_ProgressChanged);
        }

        private void FeatureLayer_MouseLeftButtonUp(object sender, GraphicMouseButtonEventArgs e)
        {
            if (_lastGraphic != null)
                _lastGraphic.UnSelect();

            e.Graphic.Select();
            if (e.Graphic.Selected)
                MyDataGrid.ScrollIntoView(e.Graphic, null);

            _lastGraphic = e.Graphic;
            MyMap.ZoomTo(e.Graphic.Geometry);  
        }

        [Serializable]
        public class Token
        {
            //response {"token" : "ShBh03DRIR1e1RbiNmoB-YfqPdMH31bKWY9BxlL5RcrSLRZTFhLw9RSGjbLE-faz-c2xxvq21-lSdSAobxRfEQdOcxAVbmJbm20O_GZHDuLnlJvXMSuOKuj7I23sa45M68Gi51ggAChdyjJgtOAsmg..","expires" : 1367777161054,"ssl" : false}
            public string token { get; set; }
            public long expires { get; set; }
        }

        //void string GenerateAGSToken()
        //{
        //    //expiration=524160 (364 days)
        //    string postData = string.Format("f=json&username={0}&password={1}&client=requestip&expiration=524160", "siteadmin", "woodsideadmin");

        //    string agsTokenData = this.DoPostForString("http://oceansmap.rpsgroup.com/server/tokens/generateToken", postData);
        //    //{"token":"C4_fVBfIE8ULhZXrMuvFkwJ-i-u2E-XozErt8fhOqfy-3SHpeeoQStBDQN_NNtH4","expires":1382387566490}

        //    JavaScriptSerializer js = new JavaScriptSerializer();

        //    //Token oAuth2Token = js.Deserialize<Token>(responseData);
        //    Token agsToken = js.Deserialize<Token>(agsTokenData);

        //    //set cache item to expire 2 minutes before token expiration (usually 2 hours)
        //    //expiration=524160 (364 days)
        //    HttpRuntime.Cache.Insert(
        //        "AGS_Token",
        //        agsToken.token,
        //        null,
        //        Cache.NoAbsoluteExpiration,
        //        new TimeSpan(363, 23, 58, 0),
        //        CacheItemPriority.Default,
        //        new CacheItemRemovedCallback(ReportRemovedAGSTokenCallback));

        //    return agsToken.token;
        //}

        /*void ReportRemovedAGSTokenCallback(String key, object value,
            System.Web.Caching.CacheItemRemovedReason removedReason)
        {
            this.GenerateAGSToken();
        }*/

        private void MyMap_Loaded()
        {
            //trying to get the tokens working with secure data
            //not working
            ////string postData = "f=json&client_id=fvCimp1FzxGGAWrQ&client_secret=7630abe7f8844f90b026f628c171bc31&grant_type=client_credentials&expiration=524160";
            //string postData = string.Format("f=json&username={0}&password={1}&client=requestip&expiration=524160", "stephen_asa", "Imfromnh66");

            //string agsTokenData = DoPostForString("https://www.arcgis.com/sharing/generateToken?", postData);
            ////{"token":"C4_fVBfIE8ULhZXrMuvFkwJ-i-u2E-XozErt8fhOqfy-3SHpeeoQStBDQN_NNtH4","expires":1382387566490}

            //JavaScriptSerializer js = new JavaScriptSerializer();

            ////Token oAuth2Token = js.Deserialize<Token>(responseData);
            //Token agsToken = js.Deserialize<Token>(agsTokenData);
            var layerCollection = new LayerCollection();

            try
            {
                ////a.Map.Layers.Clear();
                UrlFeatureService = urlText.Text;
                var servicewithToken = UrlFeatureService.Split('|');
                
                var mylayer = new FeatureLayer();
                if (servicewithToken.Length > 1)
                {
                    UrlFeatureService = servicewithToken[0];
                    UrlFeatureServiceToken = servicewithToken[1];
                    mylayer.Token = UrlFeatureServiceToken;
                }
                mylayer.Url = UrlFeatureService + "/0";
                mylayer.OutFields = new OutFields() { "*" }; 
                //mylayer.Token = agsToken.token;
                var mylayerBase = this.MyMap.Layers[0] as TiledMapServiceLayer;
                var mylayerGraphic = mylayer as ESRI.ArcGIS.Client.GraphicsLayer;
                layerCollection.Add(mylayerBase);
                //layerCollection.Add(MyMap.Layers[0]);
                layerCollection.Add(mylayerGraphic);
                MyMap.Layers = layerCollection;
                MyDataGrid.Map = MyMap;
                MyDataGrid.GraphicsLayer = MyMap.Layers[1] as ESRI.ArcGIS.Client.GraphicsLayer;
            }
            catch (Exception ex)
            {
                backgroundWorker1.ReportProgress(0, "Please enter valid URL");
                return;
            }
        }

        private void DeleteScenarioButton_Click(object sender, RoutedEventArgs e)
        {
            ClearStatus();

            if (MyDataGrid.SelectedGraphics.Count < 1)
            {
                UpdateStatus("No scenarios selected.");
                return;
            }

            DeleteScenarioButton.IsEnabled = false;
            backgroundWorker1.RunWorkerAsync(MyDataGrid.SelectedGraphics);
        }

        private void RefreshScenarioButton_Click(object sender, RoutedEventArgs e)
        {
            ClearStatus();
            MyMap_Loaded();
        }

        private void UpdateStatus(string text)
        {
            ResponseTextBlock.Text = (text + "\n" + ResponseTextBlock.Text);
        }

        private void ClearStatus()
        {
            ResponseTextBlock.Text = "Manage OilMap Scenarios:  Status Window";
        }

        // Worker Method 
        void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker worker = sender as BackgroundWorker;
            if (worker.CancellationPending == true)
            {
                e.Cancel = true;
                return;
            }

            //get the graphics from calling thread
            IList<Graphic> trajectories = e.Argument as IList<Graphic>;

            string[] layerNames = { "Trajectory", "Particles", "Thickness","SAR BOX", "SAR SEARCH AREA"};
            int i = 0;
            int batchSize = 500;
            //string[] templayerlistfix = { "2015-04-06_625_27413", "Light Crude 500 bbls_272_78240", "Medium Crude-1,000 bbls_284_63507", "ScenarioName_206_93879", "ScenarioName_301_39787", "ScenarioName_556_53855", "ScenarioName_935_84617", "ScenarioName_964_59382" };
            foreach (var trajectory in trajectories)
            {
                i++;
                if (trajectory.Attributes["scenario"] == null)
                {
                    worker.ReportProgress(0, "no SCENARIO_ID found in trajectory " + i);
                    continue;
                }
                if (string.IsNullOrEmpty(trajectory.Attributes["scenario"].ToString()))
                {
                    worker.ReportProgress(0, "SCENARIO_ID in trajectory " + i + " is empty");
                    continue;
                }

                string scenario = trajectory.Attributes["scenario"].ToString();
                string strWhere = string.Format("scenario='{0}'", scenario);
                //string scenario = "OILSPILL_test_";
                //string strWhere = "SCENARIO_ID like 'OILSPILL_test_%'";
                
                //string postData = string.Format("where={0}", WebUtility.UrlEncode(strWhere));

                //process each layer
                for (int layerId = 4; layerId >= 0; layerId--)
                {
                    string noFeaturesAlert = string.Format("No features found in {0}: {1}", scenario, layerNames[layerId]);

                    //get oids
                    FeatureSet featureSet = GetFeatureIds(layerId, strWhere);

                    if (featureSet == null || featureSet.ObjectIDs == null)
                    {
                        worker.ReportProgress(0, noFeaturesAlert);
                        continue;
                    }

                    //split set of oids into sets of comma-delimited up to batch size
                    string delimIds = "";
                    int fCount = 0;
                    foreach (int objectId in featureSet.ObjectIDs)
                    {
                        fCount++;
                        //add batch delimiter
                        string sep = fCount % batchSize == 0 ? ";" : ",";
                        delimIds += objectId + sep;
                    }
                    if (fCount < 1)
                    {
                        worker.ReportProgress(0, noFeaturesAlert);
                        continue;
                    }

                    //truncate last separator
                    delimIds = delimIds.Substring(0, delimIds.Length - 1);
                    string[] aryDelimIds = delimIds.Split(";".ToCharArray());
                    string layerUrl = "";

                    if (UrlFeatureServiceToken != null)
                    {
                        layerUrl = string.Format("{0}/{1}/deleteFeatures?f=json&token={2}", UrlFeatureService, layerId, UrlFeatureServiceToken);
                    }
                    else
                    {
                        layerUrl = string.Format("{0}/{1}/deleteFeatures?f=json", UrlFeatureService, layerId);
                    }
                    

                    foreach (string ids in aryDelimIds)
                    {
                        //batch delete
                        string postDataOIDs = string.Format("objectIds={0}", WebUtility.UrlEncode(ids));
                        try
                        {
                            this.DoPostForString(layerUrl, postDataOIDs);
                        }
                        catch (Exception ex)
                        {
                            worker.ReportProgress(0, ex.Message);
                            e.Cancel = true;
                            return;
                        }

                        //update feature count after delete
                        FeatureSet featureSet2 = GetFeatureIds(layerId, strWhere);
                        int fCount2 = 0;
                        foreach (int objectId2 in featureSet2.ObjectIDs)
                        {
                            fCount2++;
                        }
                        string updateText2 = string.Format("{0}: {1}: remaining: {2}", scenario, layerNames[layerId], fCount2);
                        worker.ReportProgress(0, updateText2);
                    }
                }
            }

        }

        // This event handler updates the progress bar. 
        private void backgroundWorker1_ProgressChanged(object sender,
            ProgressChangedEventArgs e)
        {
            UpdateStatus((string)e.UserState);
            //UpdateStatus(e.ProgressPercentage);
        }

        // Completed Method 
        void backgroundWorker1_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            if (e.Cancelled) 
            { 
                UpdateStatus("Cancelled"); 
            } 
            else if (e.Error != null)
            { 
                UpdateStatus("Exception Thrown"); 
            } 
            else 
            {
                UpdateStatus("Completed");
            }
            DeleteScenarioButton.IsEnabled = true;
        }

        private string DoPostForString(string url, string postData)
        {
            // create the POST request
            HttpWebRequest webRequest = (HttpWebRequest)WebRequest.Create(url);
            webRequest.Method = "POST";
            webRequest.ContentType = "application/x-www-form-urlencoded";
            webRequest.ContentLength = postData.Length;
            webRequest.Timeout = 1000*60*5;

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

            if (responseData.ToLower().Contains("\"error\":"))
            {
                return(string.Format("ERROR in POST TO URL: {0}; POSTDATA: {1} / RESPONSEDATA: {2}", url, postData, responseData));
            }
            return responseData;
        }

        private FeatureSet GetFeatureIds(int layerId, string where)
        {
            Query query = new Query()
            {
                ReturnGeometry = false,
                ReturnIdsOnly = true,
                Where = where
            };
            
            QueryTask queryTask = new QueryTask()
            {
                Url = string.Format("{0}/{1}", UrlFeatureService, layerId)
            };
            if(UrlFeatureServiceToken != null){
                queryTask.Token = UrlFeatureServiceToken;
            }
            try
            {
                return queryTask.Execute(query);
            }
            catch (Exception ex)
            {
                return null;
            }
        }
    }

}
