using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Text;
using System.Runtime.InteropServices;

/// <summary>
/// Summary description for ModelEngine
/// </summary>
public class ModelEngine
{

    #region Dll Calls
    [DllImport("KERNEL32.DLL", EntryPoint = "GetPrivateProfileIntW", CharSet = CharSet.Ansi)]
    public static extern int GetPrivateProfileInt(string lpApplicationName, string lpKeyName, int nDefault, string lpFileName);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool WritePrivateProfileString(string lpAppName,
       string lpKeyName, string lpString, string lpFileName);
    [DllImport("KERNEL32.DLL", EntryPoint = "GetPrivateProfileStringW", CharSet = CharSet.Ansi)]
    public static extern int GetPrivateProfileString(string lpApplicationName, string lpKeyName, string lpDefault, StringBuilder lpReturnedString, int nSize, string lpFileName);
    #endregion

	public ModelEngine()
	{
		//
		// TODO: Add constructor logic here
		//
	}
}
