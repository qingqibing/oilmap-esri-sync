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
using System.Collections.Generic;
using System.Text;

public partial class GetEDSSources : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?SubCode=dubai20110301&DataType=currents&bbox=112.05690768945291,-23.858786528244487,119.0551987050776,-19.25729645899828");

        string sSubCode = Request.QueryString["SubCode"];
        string sDataType = Request.QueryString["DataType"];
        string sBBox = Request.QueryString["BBox"];
        string[] sSplit = sBBox.Split(new char[] { ',' });
        EDSProcessor myProcessor = new EDSProcessor();
        string myString = myProcessor.GetDataSources(sSubCode, sDataType, double.Parse(sSplit[0]), double.Parse(sSplit[1]), double.Parse(sSplit[2]), double.Parse(sSplit[3]));
        Response.Write(myString);
    }
}
