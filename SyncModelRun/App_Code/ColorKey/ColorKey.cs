using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
//using System.Web.UI.MobileControls;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Text;

/// <summary>
/// Summary description for ColorKey
/// </summary>
public class ColorKey
{
    private string m_sFilename;
    private string[] m_sKeyTitle = new string[3];
    private List<string> m_sDataText = new List<string>();
    private List<double> m_dDataMin = new List<double>();
    private List<double> m_dDataMax = new List<double>();
    private List<Color> m_pDataColor = new List<Color>();

    public ColorKey(string sFilename)
    {
        LoadColorKey(sFilename);
    }

    public string Filename
    {
        get { return m_sFilename; }
        set { m_sFilename = value; }
    }

    private void LoadColorKey()
    {
        FileStream fs = null;
        TextReader tr = null;
        m_sDataText.Clear();
        m_dDataMin.Clear();
        m_dDataMax.Clear();
        m_pDataColor.Clear();
        try
        {
            fs = new FileStream(m_sFilename, FileMode.Open);
            tr = new StreamReader(fs);
            m_sKeyTitle[0] = tr.ReadLine();
            m_sKeyTitle[1] = tr.ReadLine();
            m_sKeyTitle[2] = tr.ReadLine();
            string msg = tr.ReadLine();
            while (msg != null)
            {
                m_sDataText.Add(msg);
                msg = tr.ReadLine();
                int myValue = Convert.ToInt32(msg);
                msg = "FF" + myValue.ToString("X6").Substring(4, 2) + myValue.ToString("X6").Substring(2, 2) + myValue.ToString("X6").Substring(0, 2);
                myValue = int.Parse(msg, System.Globalization.NumberStyles.HexNumber);
                Color myColor = Color.FromArgb(myValue);
                m_pDataColor.Add(myColor);
                msg = tr.ReadLine();
            }
        }
        catch (Exception ex)
        {
            m_sKeyTitle[0] = "ERROR: " + ex.Message;
        }
        finally
        {
            if (tr != null)
                tr.Close();
            if (fs != null)
                fs.Close();
        }
    }

    private void LoadColorKey(string sFilename)
    {
        m_sFilename = sFilename;
        LoadColorKey();
    }

    public override string ToString()
    {
        StringBuilder Result = new StringBuilder();
        Result.Append(m_sKeyTitle[0] + "|");
        Result.Append(m_sKeyTitle[1] + "|");
        Result.Append(m_sKeyTitle[2] + "|");
        for (int i = 0; i < m_sDataText.Count; i++)
        {
            Result.Append(m_sDataText[i] + "|");
            Result.Append(m_pDataColor[i].R.ToString("X2") + m_pDataColor[i].G.ToString("X2") + m_pDataColor[i].B.ToString("X2") + "|");
        }
        return Result.ToString();
    }
}
