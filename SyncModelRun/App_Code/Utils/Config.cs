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

/// <summary>
/// Summary description for Config
/// </summary>
public class Config
{
    #region Private Members
    private static string _AppPath;
    #endregion

    #region Public Properties
    #endregion

    #region Constructors
    public Config()
	{
        _AppPath = HttpContext.Current.Request.MapPath(HttpContext.Current.Request.ApplicationPath);

    }
    #endregion

    #region Private Methods
    #endregion

    #region Public Methods
    #endregion
}
