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

public partial class GetTimeSeries : System.Web.UI.Page
{
    private string _ModelType;
    private string _CaseName;
    private string _WebPath;
    private string _sLocation;
    
    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            //Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ClientName=None&ModelType=OILSPILL&CaseName=OILSPILL_5_294_989_12815&Location=World");
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ClientName=dubai20110301&ModelType=OILSPILL&CaseName=SAMPLE_TEST3_153_38209&Location=world&UseEXE=true");
        //TO BE REPLACED WITH SOMTHING MORE SECURE
        _ModelType = "OILSPILL";
        if (Request.QueryString["ModelType"] != null)
            _ModelType = Request.QueryString["ModelType"];

        _CaseName = "";
        if (Request.QueryString["CaseName"] != null)
            _CaseName = Request.QueryString["CaseName"];

        _sLocation = "World";
        if (Request.QueryString["Location"] != null)
            _sLocation = Request.QueryString["Location"];

        _WebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        bool _GetByEXE = true;
        if (Request.QueryString["UseEXE"] != null)
            _GetByEXE = bool.Parse(Request.QueryString["UseEXE"]);

        //Set the proper paths for the aggregator based off of the model type
        string outputPath = "\\ModelData\\" + _sLocation;
        TimeSeries mySeries = null;
        switch (_ModelType)
        {
            case "OILSPILL": 
                mySeries = new OilTimeSeries(_WebPath + outputPath, _CaseName);
                break;
            case "CHEMSPILL": 
                mySeries = new ChemTimeSeries(_WebPath + outputPath, _CaseName);
                break;
            default:
                Response.Write("ERROR: Unrecognized ModelType");
                return;
        }

        string myResult = "";
        if (mySeries != null)
            if (_GetByEXE)
                myResult = mySeries.GetScenarioTimeSeriesFromEXE(_WebPath + "\\ModelData\\FatesReader\\GetFates.exe");
            else
                myResult = mySeries.GetScenarioTimeSeries();

        Response.Write(myResult);
    }
}
