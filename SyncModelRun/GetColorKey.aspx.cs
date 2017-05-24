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

public partial class GetColorKey : System.Web.UI.Page
{
    private string _ClientName;
    private string _ModelType;
    private string _OutputType;
    private string _WebPath;
    private string _sLocation;

    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ClientName=None&ModelType=CHEMSPILL&OutputType=Dissolved&Location=Wuhan");
        //TO BE REPLACED WITH SOMTHING MORE SECURE
        _ClientName = Request.QueryString["ClientName"];
        _ModelType = Request.QueryString["ModelType"];
        _OutputType = Request.QueryString["OutputType"];
        _sLocation = Request.QueryString["Location"];
        _WebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));

        //Set the proper paths for the aggregator based off of the model type
        string keyPath = "";
        string outputPath = "\\ModelData\\" + _sLocation;
        switch (_ModelType)
        {
            case "OILSPILL": 
                switch (_OutputType.ToUpper())
                {
                    case "PARTICLES":
                        keyPath = _WebPath + outputPath + "\\keys\\oilmaptrj.kew";
                        break;
                    case "THICKNESS":
                        keyPath = _WebPath + outputPath + "\\keys\\oilmaptk.kew";
                        break;
                }
                break;
            case "CHEMSPILL": 
                switch (_OutputType.ToUpper())
                {
                    case "PARTICLES":
                        keyPath = _WebPath + outputPath + "\\keys\\chemtraj.kew";
                        break;
                    case "DISSOLVED":
                        keyPath = _WebPath + outputPath + "\\keys\\dissolved.dwt";
                        break;
                    case "CONCENTRATIONS":
                        keyPath = _WebPath + outputPath + "\\keys\\surfaceslick.ssk";
                        break;
                }
                break;
            default:
                Response.Write("ERROR: Unrecognized ModelType");
                return;
        }
        ColorKey myKey = new ColorKey(keyPath);

        string myResult = myKey.ToString();
        Response.Write(myResult);
    }
}
