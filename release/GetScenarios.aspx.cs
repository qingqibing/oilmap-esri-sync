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

public partial class GetScenarios : System.Web.UI.Page
{
    private string _ModelType;
    private string _WebPath;
    private string _sLocation;

    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            //Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ClientName=None&ModelType=OILSPILL&Location=Wuhan&Time=true");
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ModelType=OILSPILL&Location=World&TIME=true");
        //TO BE REPLACED WITH SOMTHING MORE SECURE

        _ModelType = "OILSPILL";
        if (Request.QueryString["ModelType"] != null)
            _ModelType = Request.QueryString["ModelType"];

        _sLocation = "World";
        if (Request.QueryString["Location"] != null)
            _sLocation = Request.QueryString["Location"];

        _WebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt")) + "\\ModelData\\" + _sLocation;
        
        FileScraper scraper = new FileScraper(_ModelType, _WebPath);

        bool bWithTime = false;
        if (Request.QueryString["Time"] != null)
            bWithTime = bool.Parse(Request.QueryString["Time"]);

        if (bWithTime)
            Response.Write(scraper.getModelFileNamesWithTime(_WebPath));            
        else
            Response.Write(scraper.getModelFileNames(_WebPath));
    }
}
