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
using System.Diagnostics;

public partial class KillModels : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        if (Request.QueryString.Count == 0)
            Response.Redirect(HttpContext.Current.Request.Url.AbsoluteUri + "?ModelType=OILSPILL");

        //string sWebPath = Path.GetDirectoryName(Server.MapPath("ModelRunMapPath.txt"));
        string sModelType = Request.QueryString["ModelType"].ToUpper();
        string sModelName = "";
        switch (sModelType)
        {
            case "OILSPILL":
                sModelName = "OILMODEL";
                break;

            case "CHEMSPILL":
                sModelName = "CHEMODEL";
                break;
        }

        
        //here we're going to get a list of all running processes on
        //the computer
        foreach (Process clsProcess in Process.GetProcesses())
        {
            //now we're going to see if any of the running processes
            //match the currently running processes by using the StartsWith Method,
            //this prevents us from incluing the .EXE for the process we're looking for.
            //. Be sure to not
            //add the .exe to the name you provide, i.e: NOTEPAD,
            //not NOTEPAD.EXE or false is always returned even if
            //notepad is running
            if (clsProcess.ProcessName.ToUpper().StartsWith(sModelName))
            {
                //since we found the proccess we now need to use the
                //Kill Method to kill the process. Remember, if you have
                //the process running more than once, say IE open 4
                //times the loop thr way it is now will close all 4,
                //if you want it to just close the first one it finds
                //then add a return; after the Kill
                clsProcess.Kill();
                //process killed, return true
            }
        }
    }
}
