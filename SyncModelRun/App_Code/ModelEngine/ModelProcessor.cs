using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;

public enum ModelType
{
    OilModel,
    ChemModel
}

/// <summary>
/// Summary description for ModelProcessor
/// </summary>
public class ModelProcessor
{
    private ModelType _ModelType;
    private double _Timeout;

	public ModelProcessor()
	{
		//
		// TODO: Add constructor logic here
		//
	}

    /// <summary>
    /// Preferred Constructor
    /// </summary>
    /// <param name="ModelType">Type of model to run</param>
    public ModelProcessor(ModelType eModelType, double timeout)
    {
        _ModelType = eModelType;
        _Timeout = timeout;
    }

    public string runChemModel(ChemInputData inputData)
    {
        ChemModelEngine chemEngine = new ChemModelEngine(inputData, _Timeout);
        return chemEngine.runModel();
    }

    public string runOilModel(OilInputData inputData)
    {
        OilModelEngine oilEngine = new OilModelEngine(inputData, _Timeout);
        return oilEngine.runModel();
    }
}
