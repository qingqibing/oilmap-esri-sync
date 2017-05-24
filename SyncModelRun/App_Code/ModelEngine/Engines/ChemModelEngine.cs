using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
//using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Diagnostics;
using System.Timers;
using System.IO;
using System.Drawing;

/// <summary>
/// Summary description for ChemModelEngine
/// </summary>
public class ChemModelEngine:ModelEngine
{
    public delegate void _OnModelError(string errorMessage);
    private Process _ChemmodelProcess;
    private Timer _ProcessTimer;
    private string _TimeoutError;
    private DateTime _LastWrite;
    private ChemInputData _InputData;

    public ChemModelEngine(ChemInputData inputData, double timeout)
	{
        _InputData = inputData;
        _TimeoutError = "";
        _ChemmodelProcess = new Process();
        _ProcessTimer = new Timer();
        _ProcessTimer.Interval = timeout;
        _ProcessTimer.Elapsed += _ProcessTimer_Elapsed;        
	}

    void _ProcessTimer_Elapsed(object sender, ElapsedEventArgs e)
    {
        if (_ChemmodelProcess != null && !_ChemmodelProcess.HasExited)
        {
            bool testFile = false;
            string outputFile = _InputData.outputPath + "\\" + _InputData.fileName + ".CLU";
            if (File.Exists(outputFile))
            {
                testFile = true;
                if (_LastWrite != null)
                {
                    if (File.GetLastWriteTime(outputFile) == _LastWrite)
                        testFile = false;
                }
                _LastWrite = File.GetLastWriteTime(outputFile);
            }
            if (!(testFile))
            {
                _TimeoutError = "ERROR: Chemodel.exe has timed out";
                _ChemmodelProcess.Kill();
                _ProcessTimer.Stop();
            }
        }
    }

    internal string runModel()
    {
        if (Path.GetExtension(_InputData.coastLineFile) == "SHP")
        {
            //Check SHP file to make sure spill point isn't on land.
            PointF incPoint = new PointF((float)_InputData.spillLon, (float)_InputData.spillLat);
            ShapeFile myFile = new ShapeFile();
            myFile.LoadShapeFile(_InputData.coastLineFile);
            bool isPointOnLand = false;
            if (myFile.ShapeType == ShapeFileType.SHAPE_TYPE_POLYGONS)
            {
                foreach (Polygon myPoly in myFile.Polygons)
                {
                    if (Utils.PointInPolygon(incPoint, myPoly))
                    {
                        isPointOnLand = true;
                        break;
                    }
                }
            }

            if (isPointOnLand)
            {
                return "Spill point is on land. Choose another site.";
            }
        }

        //Set the file names
        string origCnpFile = _InputData.cnpPath + "\\" + _InputData.cnpFileName;
        string cnpFile = _InputData.cnpPath + "\\" + _InputData.fileName + ".cnp";
        //Copy Files
        File.Copy(origCnpFile, cnpFile, true);

        //Set up the INP file
        WritePrivateProfileString("Chemical Scenario", "Scenario", _InputData.scenario, cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Spill Lon", _InputData.spillLon.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Spill Lat", _InputData.spillLat.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Start Year", _InputData.start.Year.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Start Month", _InputData.start.Month.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Start Day", _InputData.start.Day.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Start Hour", _InputData.start.Hour.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Start Minute", _InputData.start.Minute.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Run Length", _InputData.simulationLength.ToString(), cnpFile);
        if (_InputData.currentFile != "")
            WritePrivateProfileString("Chemical Scenario", "Current File", Path.GetFileName(_InputData.currentFile), cnpFile);
        else
            WritePrivateProfileString("Chemical Scenario", "Current File", "_NO_DATA.DIR", cnpFile);
        if (_InputData.windsFile != "")
        {
            WritePrivateProfileString("Chemical Scenario", "Number Of Wind Files", "1", cnpFile);
            WritePrivateProfileString("Chemical Scenario", "WindFile1", Path.GetFileName(_InputData.windsFile), cnpFile);
            WritePrivateProfileString("Chemical Scenario", "List Of Wind Files", Path.GetFileName(_InputData.windsFile), cnpFile);
        }
        else
            WritePrivateProfileString("Chemical Scenario", "Number Of Wind Files", "0", cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Oil Name", _InputData.chemType, cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Release Duration", _InputData.spillDuration.ToString(), cnpFile);
        if (_InputData.ModelMethod) //fast method
        {
            WritePrivateProfileString("Chemical Scenario", "Nsp_rls", "100", cnpFile);
            WritePrivateProfileString("Chemical Scenario", "DELTAT", ".33333", cnpFile);
            WritePrivateProfileString("Chemical Scenario", "out_intvl", ".33333", cnpFile);
        }
        else //comprehensive method
        {
            WritePrivateProfileString("Chemical Scenario", "Nsp_rls", "1000", cnpFile);
            WritePrivateProfileString("Chemical Scenario", "DELTAT", ".166667", cnpFile);
            WritePrivateProfileString("Chemical Scenario", "out_intvl", ".166667", cnpFile);
        }
        WritePrivateProfileString("Chemical Scenario", "cas1", _InputData.CAS1.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "cas2", _InputData.CAS2.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "cas3", _InputData.CAS3.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dens25c", _InputData.Dens25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "thk25c", _InputData.Thk25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "partsize", _InputData.Partsize.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dgrda25c", _InputData.Dgrda25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dgrdw25c", _InputData.Dgrdw25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dgrds25c", _InputData.Dgrds25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "chemsticky", _InputData.Chemsticky.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dbulk25c", _InputData.Dbulk25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "concaqu", _InputData.Concaqu.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "concemul", _InputData.Concemul.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "concphob", _InputData.Concphob.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "statecode", _InputData.Statecode.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "fwsol25c", _InputData.Fwsol25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "swsol25c", _InputData.Swsol25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "vapr25c", _InputData.Vapr25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "srft25c", _InputData.Srft25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "visc25c", _InputData.Visc25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "visa", _InputData.VISA.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "visb", _InputData.VISB.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "hlaw25c", _InputData.Hlaw25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "dislv25c", _InputData.Dislv25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "molwt", _InputData.Molwt.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "bpc", _InputData.Bpc.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "mpc", _InputData.Mpc.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "logkow", _InputData.Logkow.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "logkoc", _InputData.Logkoc.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "ccode", _InputData.Ccode.ToString(), cnpFile);

        WritePrivateProfileString("Chemical Scenario", "DensatT", _InputData.DensAtT.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "degCDens", _InputData.DegCDens.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "ViscAtT", _InputData.ViscAtT.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "degCVisc", _InputData.DegCVis.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "VapPrsAtT", _InputData.VapPrsAtT.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "degCVap", _InputData.DegCVap.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "DGRDSurfW25C", _InputData.DgrdSurfW25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "HlawAtT", _InputData.HlawAtT.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "degCHLaw", _InputData.DegChLaw.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "REACT", _InputData.React.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "ReactsWith", _InputData.ReactsWith, cnpFile);
        WritePrivateProfileString("Chemical Scenario", "DIFFUS25C", _InputData.Diffus25c.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Chemname", _InputData.chemType, cnpFile);
        WritePrivateProfileString("Chemical Scenario", "formula", _InputData.Formula, cnpFile);
        WritePrivateProfileString("Chemical Scenario", "UNNO", _InputData.UnNo.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "FORMNO", _InputData.FormNo.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Acid_Base_Cons", _InputData.AcidBaseCons.ToString(), cnpFile);
        WritePrivateProfileString("Chemical Scenario", "Grid File", Path.GetFileName(_InputData.coastLineFile), cnpFile);

        //Try to launch the chemodel exe
        bool prcResult = false;
        try
        {
            char quote = '"';
            string exePath = _InputData.exePath + "\\chemodel.exe";
            if (File.Exists(exePath)) //make sure the exe is there
                _ChemmodelProcess.StartInfo.FileName = quote + exePath + quote;
            else
                return "ERROR: chemodel.exe was not found";
            if (!File.Exists(cnpFile))
                return "ERROR: cnp file not found";

            _ChemmodelProcess.StartInfo.CreateNoWindow = false;
            _ChemmodelProcess.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
            _ChemmodelProcess.StartInfo.ErrorDialog = true;
            _ChemmodelProcess.StartInfo.Arguments = quote + cnpFile + quote;
            prcResult = _ChemmodelProcess.Start();

            _ProcessTimer.Start();
            while (!_ChemmodelProcess.HasExited)
            {
                if (!_ChemmodelProcess.Responding)
                    _ChemmodelProcess.Kill();
            }
            _ChemmodelProcess.Dispose();
            _ProcessTimer.Stop();
        }
        catch (Exception ex)
        {
            return "ERROR: " + ex.Message;
        }
        if (_TimeoutError.Contains("ERROR:"))
            return _TimeoutError;
        else
            return Path.GetFileNameWithoutExtension(_InputData.fileName); //TODO: Return the real filename
    }
}
