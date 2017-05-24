using ASA.EDS.Data.ASAnc;
using ASA.EDS.Data;
using ASA.EDS.Common;
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.IO;
using System.Text;

using ucar.ma2;
using ucar.nc2;
using java.util;


namespace Aggregator2
{
    /**
     * 
     * @author Eric Bernier <ebernier@asascience.com>
     */
    public class CellFileAggregator
    {
        //private const int HOUR_MINS = 60;

        private int timeDimSize = -1;
        private int latDimSize = -1;
        private int lonDimSize = -1;
        private int ncellDimSize = -1; 
        private int nCells = -1;

        private List<float> lon;
        private List<float> lat;

        private string timeName = "";
        private string lonName = "";
        private string latName = "";
        private string uName = "";
        private string vName = "";
        //private Util util_ = new Util();

        private bool scalar = false;
        private string origUnits = "";

        public DateTime startDate;
        public DateTime endDate;
        private DateTime timeOrigin;
        private DateTime firstFileDate;

        private Dimension timeDim;
        private Dimension cellDim;

        private bool areaWindowOn = false;
        public double aoiNorth = 0;
        public double aoiSouth = 0;
        public double aoiEast = 0;
        public double aoiWest = 0;

        private double startTimeMin = -1;
        private double endTimeMin = -1;
        private int waterOrWind = -1;

        private string timeUnits = "";
        private string timeUnitG = "";
        private string curTimeUnit = "";
        public string outUnits = "";

        private double[] tDurHr;
        private double[] tStart;
        private double[] tEnd;
        private double tStart0 = 0;
        private double tEnd0 = 0;
        private int[] nTsteps;
        private int[] fOrder;

        private double dTstep = 0;
        private double fileTimeStep = 0;
        private int outTimeStepHrs = 1;

        //private const short MISSING_VALUE = -9999;
        //private const float MISSING_VALUE_F = -9999f;
        //private const float MISSING_VAL_CHECK = -999F;
        //private const float SCALE_FACTOR = 1000f; 
        //private float offset = 0;
        private float scaleFactor = 1F;
        private float missingVal = -9999F;

        private List<string> fileList = new List<string>();
        public string error = "";

        [DllImport("kernel32", SetLastError = true)]
        static extern IntPtr LoadLibrary(string IpFileName);

        //*****************************************************************************************
        // Method: CellFileAggregator
        //
        /// <summary>
        ///     Constructor for a CellFileAggregator
        /// </summary>
        //*****************************************************************************************
        public CellFileAggregator()
        {

        }

        
     //***************************************************************************************
       // Method: ImportJavaLibrary
       /// <summary>
       ///     This method is responsible for importing the vjsnativ.dll, which is not
       ///     supported in the .NET 4.0 framework. With this import, we can make use of
       ///     the NetCDF API provided by UNIDATA
       /// </summary>
       //***************************************************************************************
       public void ImportJavaLibrary(string javaDLL_)
       {
           if (Environment.Version.Major >= 4)
           {
               //string javaDllLoc = javaDLL_+"vjsnativ.dll";

               //string folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), javaDLL_);

               //folder = Path.GetFullPath(folder);
               LoadLibrary(Path.Combine(javaDLL_, "vjsnativ.dll"));
           }
       }

        //*****************************************************************************************
        // Method: ReadCellFile
        //
        /// <summary>
        ///     Method that reads a cell file that is in-line to be aggregated, verifying
        ///     that the file is valid, and can indeed be aggregated with the other files
        /// </summary>
        /// <param name="asaNC"></param>
        /// <param name="fileToRead"></param>
        /// <param name="source"></param>
        /// <returns></returns>
        //*****************************************************************************************
       public void sendASANetCDF2AGOL(string fileToRead, string libPath)
       {
           ImportJavaLibrary(libPath);

           DataSource source = new DataSource();
           ASANetCdf asaNC = new ASANetCdf();

           string varName;
           int dimSize;
           double timeOffset = 0;

           NetcdfFile currentFile = new NetcdfFile(fileToRead);

           Iterator dimensions = currentFile.getDimensionIterator();
           Iterator variables = currentFile.getVariableIterator();
           Iterator attributes = currentFile.getGlobalAttributeIterator();

           ucar.nc2.Attribute[] atts = new ucar.nc2.Attribute[1];
           Dimension dim;

           timeName = source.TimeVariableName;
           lonName = source.LonVariableName;
           latName = source.LatVariableName;
           uName = source.UVariableName;
           vName = source.VVariableName;

           scalar = source.Scalar;

           scaleFactor = source.ScaleFactor;
           //this.waterOrWind = Convert.ToInt32(source.DataType.ToUpper().StartsWith("W"));

           while (dimensions.hasNext())
           {
               dim = (Dimension)dimensions.next();

               varName = dim.getName();
               dimSize = dim.getLength();

               if (varName.Equals(timeName))
               {
                   timeDimSize = dimSize;
               }
               else if (varName.Equals(lonName))
               {
                   lonDimSize = dimSize;
               }
               else if (varName.Equals(latName))
               {
                   latDimSize = dimSize;
               }
               else if (varName.Equals("ncell") || varName.Equals("ncells"))
               {
                   ncellDimSize = dimSize;
               }
           }

           Variable var;
           int numVars = 0;
           while (variables.hasNext())
           {
               var = (Variable)variables.next();
               varName = var.getName();

               if (varName.Equals(timeName))
               {
                   numVars += 1;
               }
               else if (varName.Equals(timeName))
               {
                   numVars += 1;
               }
               else if (varName.Equals(timeName))
               {
                   numVars += 1;
               }
               else if (varName.Equals(timeName))
               {
                   numVars += 1;
               }
               else if (varName.Equals(timeName))
               {
                   numVars += 1;
               }
           }

           Variable varTime = currentFile.findVariable(timeName);
           ucar.ma2.Array timeArray = varTime.read();
           Index timeIndex = timeArray.getIndex();

           double t1 = (double)timeArray.getDouble(timeIndex.set(0));
           double t2 = (double)timeArray.getDouble(timeIndex.set(timeDimSize - 1));

           ucar.nc2.Attribute tUnits = varTime.findAttribute("units");
           timeUnits = tUnits.getStringValue();

           int idx = timeUnits.IndexOf("since");
           string timeString = timeUnits.Substring(idx + 6);
           DateTime date0 = DateTime.Parse(timeString);

           timeOrigin = date0;
           DateTime oldOrigin = timeOrigin;

           DateTime date1 = date0;
           DateTime date2 = date0;

           TimeSpan tSpan;
           TimeSpan tSpan2;
           if (timeUnits.ToUpper().Contains("DAYS"))
           {
               tSpan = TimeSpan.FromDays(t1);
               tSpan2 = TimeSpan.FromDays(t2);
           }
           else if (timeUnits.ToUpper().Contains("HOURS"))
           {
               tSpan = TimeSpan.FromHours(t1);
               tSpan2 = TimeSpan.FromHours(t2);
           }
           else if (timeUnits.ToUpper().Contains("MINUTES"))
           {
               tSpan = TimeSpan.FromMinutes(t1);
               tSpan2 = TimeSpan.FromMinutes(t2);
           }
           else if (timeUnits.ToUpper().Contains("SECONDS"))
           {
               tSpan = TimeSpan.FromSeconds(t1);
               tSpan2 = TimeSpan.FromSeconds(t2);
           }
           else
           {
               tSpan = TimeSpan.FromHours(t1);
               tSpan2 = TimeSpan.FromHours(t2);
           }

           date1 = date1.Add(tSpan);
           date2 = date2.Add(tSpan2);

           if (endDate > startDate)
           {
               // Time window is on
               if (startTimeMin < 0)
               {
                   tSpan = startDate - date0;
                   startTimeMin = (int)tSpan.TotalHours;
                   tSpan = endDate - date0;
                   endTimeMin = (int)tSpan.TotalHours;
               }

               if (date1 > endDate || date2 < startDate)
               {
                   timeOrigin = oldOrigin;
                   error = "CellFileAggregator.GetDimsAndVars - Invalid dates!";
                   currentFile.close();
                   //return false;
               }
           }

           if (curTimeUnit.Length > 0)
           {
               if (!timeUnits.Equals(curTimeUnit))
               {
                   error = "CellFileAggregator.GetDimsAndVars - Time Units conflict!" +
                           fileToRead;
                   currentFile.close();

                   timeOrigin = oldOrigin;
                   //return false;
               }
           }

           if (timeUnitG.Length > 0)
           {
               if (!timeUnits.Equals(timeUnitG))
               {
                   tSpan = date0 - firstFileDate;

                   if (timeUnits.ToUpper().Contains("DAYS"))
                   {
                       timeOffset = (double)tSpan.TotalDays;
                   }
                   else if (timeUnits.ToUpper().Contains("HOURS"))
                   {
                       timeOffset = (double)tSpan.TotalHours;
                   }
                   else if (timeUnits.ToUpper().Contains("MINUTES"))
                   {
                       timeOffset = (double)tSpan.TotalMinutes;
                   }
                   else if (timeUnits.ToUpper().Contains("SECONDS"))
                   {
                       timeOffset = (double)tSpan.TotalSeconds;
                   }
                   else
                   {
                       timeOffset = (double)tSpan.TotalMinutes;
                   }
               }
           }

           int numFiles = fileList.Count;
           if (numFiles == 0)
           {
               lat = new List<float>();
               lon = new List<float>();

               timeUnitG = timeUnits;
               firstFileDate = date0;

               tStart = new double[1];
               tEnd = new double[1];
               tDurHr = new double[1];
               nTsteps = new int[1];

               // Read the various variables
               Variable varLat = currentFile.findVariable(latName);
               ucar.ma2.Array latVals = varLat.read();
               Index latIndex = latVals.getIndex();
               int[] shapeLats = latVals.getShape();

               Variable varLon = currentFile.findVariable(lonName);
               ucar.ma2.Array lonVals = varLon.read();
               Index lonIndex = lonVals.getIndex();
               int[] shapeLons = lonVals.getShape();

               nCells = 0;
               areaWindowOn = false;

               if (aoiEast != aoiWest && aoiNorth != aoiSouth)
               {
                   areaWindowOn = true;
               }

               for (int c = 0; c < ncellDimSize; c++)
               {
                   double xLon = lonVals.getDouble(lonIndex.set(c));
                   double yLat = latVals.getDouble(latIndex.set(c));

                   
                   if (areaWindowOn)
                   {
                       if (xLon < aoiWest || xLon > aoiEast || yLat < aoiSouth ||
                           yLat > aoiNorth || double.IsNaN(xLon) || double.IsNaN(yLat))
                       {
                           continue;
                       }
                       else
                       {
                           nCells += 1;

                           lat.Add((float)yLat);
                           lon.Add((float)xLon);
                       }
                   }
                   else if (!double.IsNaN(xLon) && !double.IsNaN(yLat))
                   {
                       nCells += 1;

                       lat.Add((float)yLat);
                       lon.Add((float)xLon);
                   }
               }

               if (nCells <= 0)
               {
                   error = "CellFileAggregator.GetDimsAndVars: No data in the given AOI!";
                   currentFile.close();

                   timeOrigin = oldOrigin;
                   //return false;
               }
           }
           else
           {
               // This is not the first file, therefore we have must less processing to handle              
               //util_.ResizeDouble(ref tStart, numFiles + 1);
               //util_.ResizeDouble(ref tEnd, numFiles + 1);
               //util_.ResizeDouble(ref tDurHr, numFiles + 1);
               //util_.ResizeInt(ref nTsteps, numFiles + 1);
           }

           tStart[numFiles] = (double)timeArray.getDouble(timeIndex.set(0)) + timeOffset;
           tEnd[numFiles] = (double)timeArray.getDouble(timeIndex.set(timeDimSize - 1)) + timeOffset;
           tDurHr[numFiles] = tEnd[numFiles] - tStart[numFiles];
           nTsteps[numFiles] = timeDimSize;

           tStart0 = Math.Min(tStart0, tStart[numFiles]);
           tEnd0 = Math.Max(tEnd0, tEnd[numFiles]);
           
           currentFile.close();
           //return true;
       }


        //*****************************************************************************************
        // Method: FillNetCDF
        //
        /// <summary>
        ///     
        /// </summary>
        /// <param name="asaNC"></param>
        /// <param name="fileToRead"></param>
        /// <param name="source"></param>
        //*****************************************************************************************
        //public bool FillNetCDF(ref ASANetCdf asaNC, DataSource source, ref Order edsOrder)
        //{
        //    int[] timeIndex = new int[1];
        //    int[] oriOut = new int[2];
        //    int[] shpOut = new int[2];

        //    timeIndex[0] = -1;
        //    shpOut[0] = 1;
        //    shpOut[1] = nCells;

        //    double tMinLast = 0;
        //    int priorTimeStep = -1;

        //    // Time Interpolation variables
        //    bool doInterp = source.InterpData;
        //    double tMin0 = 0;

        //    int interpSteps = 1;
        //    if (outTimeStepHrs > 1 && doInterp)
        //    {
        //        interpSteps = outTimeStepHrs;
        //    }

        //    try
        //    {
        //        int numFiles = fileList.Count;
        //        for (int nf = 0; nf < numFiles; nf++)
        //        {
        //            // First, update the status queue for the number of files processed
        //            //edsOrder.Progress = (((nf + 1) * 100) / numFiles) / 2;
        //            //util_.SendQueMsg(Config.StatusQue, edsOrder);

        //            int nfo = fOrder[nf];
        //            int nf2 = 0;

        //            if (nfo < 0)
        //            {
        //                continue;
        //            }

        //            if (nf < numFiles - 1)
        //            {
        //                nf2 = fOrder[nf + 1];
        //            }

        //            string ncFile = fileList[nfo];
        //            NetcdfFile CDF = new NetcdfFile(ncFile);

        //            // Read the various variables that make up a Cell file
        //            Variable vTime = CDF.findVariable(source.TimeVariableName);
        //            ucar.ma2.Array aTime = vTime.read();
        //            Index timeInd = aTime.getIndex();

        //            ucar.nc2.Attribute tUnits = vTime.findAttribute("units");
        //            timeUnits = tUnits.getStringValue();

        //            Variable vLon = CDF.findVariable(source.LonVariableName);
        //            ucar.ma2.Array aLons = vLon.read();
        //            Index lonIndex = aLons.getIndex();
        //            int[] shapeLons = aLons.getShape();

        //            Variable vLat = CDF.findVariable(source.LatVariableName);
        //            ucar.ma2.Array aLats = vLat.read();
        //            Index latIndex = aLats.getIndex();
        //            int[] shapeLats = aLats.getShape();

        //            Variable vU = CDF.findVariable(source.UVariableName);
        //            Variable vV = CDF.findVariable(source.VVariableName);

        //            string origUnits = vU.findAttribute("units").ToString();

        //            int[] shapeU = vU.getShape();
        //            int[] shapeV = vV.getShape();

        //            int[] originU = new int[vU.getRank()];
        //            int[] originV = new int[vV.getRank()];
        //            int[] originU2 = new int[vU.getRank()];
        //            int[] originV2 = new int[vV.getRank()];

        //            int[] shapeU2;
        //            int[] shapeV2;

        //            int timeDimSize = shapeU[0];

        //            double tMin1 = tStart[nfo] - fileTimeStep;
        //            double tMin2 = tStart[nfo];

        //            if (nf == 0)
        //            {
        //                tMin0 = tStart[nfo] - (fileTimeStep / interpSteps);
        //            }

        //            for (int t = 0; t < timeDimSize; t++)
        //            {
        //                tMin1 += fileTimeStep;
        //                tMin2 += fileTimeStep;

        //                double tMin = 0;
        //                if (timeDimSize == 1)
        //                {
        //                    tMin = tStart[nfo];
        //                }
        //                else
        //                {
        //                    tMin = (double)aTime.getDouble(timeInd.set(t));
        //                }
        //                if (timeUnits.ToUpper().Contains("DAYS"))
        //                {
        //                    tMin = tMin * 24;
        //                }
        //                else if (timeUnits.ToUpper().Contains("MINUTES"))
        //                {
        //                    tMin = tMin / 60;
        //                }
        //                else if (timeUnits.ToUpper().Contains("SECONDS"))
        //                {
        //                    tMin = tMin / 360;
        //                }

        //                if (tMin <= tMinLast)
        //                {
        //                    if (timeDimSize > 1 || nf > 0)
        //                    {
        //                        tMin0 += fileTimeStep;
        //                        continue;
        //                    }
        //                }

        //                // If the file next in order has the time "tMin", skip the rest
        //                // and move onto the next file, except the last file
        //                if (nf < numFiles - 1)
        //                {
        //                    if (tStart[fOrder[nf + 1]] <= tMin && tEnd[fOrder[nf + 1]] > tMin)
        //                    {
        //                        tMin0 = tMin0 + ((timeDimSize - t) * fileTimeStep);
        //                        break;
        //                    }
        //                }

        //                if (endDate > startDate)
        //                {
        //                    int timeCheck = (int)(tMin);
        //                    double timeMin = Convert.ToDouble(timeCheck);

        //                    if (tMin < startTimeMin)
        //                    {
        //                        tMin0 += fileTimeStep;
        //                        continue;
        //                    }

        //                    if (timeMin > endTimeMin)
        //                    {
        //                        tMin0 += fileTimeStep;
        //                        continue;
        //                    }
        //                }

        //                for (int x = 0; x < interpSteps; x++)
        //                {
        //                    tMin0 += (fileTimeStep / interpSteps);

        //                    timeIndex[0]++;
        //                    tMinLast = tMin;
        //                    ArrayDouble.D1 aTimeD1 = new ArrayDouble.D1(1);

        //                    double dataTimeMins = tMin * 60;
        //                    DateTime dataTime = timeOrigin.AddMinutes(dataTimeMins);
        //                    dataTime = dataTime.AddMinutes(30);
        //                    if (dataTime.Minute != 0)
        //                    {
        //                        int minOffset = dataTime.Minute;
        //                        dataTime = dataTime.AddMinutes(-minOffset);
        //                    }

        //                    if (dataTime.Second != 0)
        //                    {
        //                        int secOffset = dataTime.Second;
        //                        dataTime = dataTime.AddSeconds(-secOffset);
        //                    }

        //                    DateTime ncEpoch = new DateTime(2000, 01, 01, 00, 00, 00);
        //                    TimeSpan duration = dataTime - ncEpoch;
        //                    int durationMins = (int)duration.TotalMinutes;

        //                    DateTime dateCheck = ncEpoch.AddMinutes(durationMins);
        //                    if ((dateCheck > endDate || priorTimeStep == durationMins) && !doInterp)
        //                    {
        //                        // If our date passed the checks above, but is somehow beyond our
        //                        // end date we do not want to process this data
        //                        timeIndex[0]--;
        //                        continue;
        //                    }

        //                    durationMins += HOUR_MINS * x;
        //                    DateTime checkDate = ncEpoch.AddMinutes(durationMins);
        //                    if (checkDate > edsOrder.EndDT)
        //                    {
        //                        break;
        //                    }

        //                    aTimeD1.set(0, durationMins);

        //                    try
        //                    {
        //                        priorTimeStep = durationMins;
        //                        asaNC.file.write("time", timeIndex, aTimeD1);
        //                    }
        //                    catch (Exception ex)
        //                    {
        //                        error = ex.ToString();
        //                        return false;
        //                    }

        //                    oriOut[0] = timeIndex[0];

        //                    // Fix the first index
        //                    originU[0] = t;
        //                    shapeU[0] = 1;
        //                    originV[0] = t;
        //                    shapeV[0] = 1;

        //                    ArrayShort.D2 aUD2 = null;
        //                    ArrayShort.D2 aVD2 = null;
        //                    Index imaU = null;
        //                    Index imaV = null;

        //                    ArrayFloat.D2 aUD2f = null;
        //                    ArrayFloat.D2 aVD2f = null;

        //                    if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                    {
        //                        aUD2 = new ArrayShort.D2(1, cellDim.getLength());
        //                        aVD2 = new ArrayShort.D2(1, cellDim.getLength()); ;
        //                        imaU = aUD2.getIndex();
        //                        imaV = aVD2.getIndex();
        //                    }
        //                    else
        //                    {
        //                        aUD2f = new ArrayFloat.D2(1, cellDim.getLength());
        //                        aVD2f = new ArrayFloat.D2(1, cellDim.getLength()); ;
        //                        imaU = aUD2.getIndex();
        //                        imaV = aVD2.getIndex();
        //                    }

        //                    ArrayShort.D2 fidD2 = new ArrayShort.D2(1, cellDim.getLength());
        //                    Index fidIndex = fidD2.getIndex();

        //                    // Arrays that will hold our first and second sets of data
        //                    // The second set is used for time interpolation, if necessary
        //                    ucar.ma2.Array aU1 = null;
        //                    ucar.ma2.Array aV1 = null;
        //                    ucar.ma2.Array aU2 = null;
        //                    ucar.ma2.Array aV2 = null;

        //                    try
        //                    {
        //                        // Read U and V from our files
        //                        aU1 = vU.read(originU, shapeU);
        //                        aV1 = vV.read(originV, shapeV);

        //                        shapeU2 = aU1.getShape();
        //                        Index idxU = aU1.getIndex();
        //                        shapeV2 = aV1.getShape();
        //                        Index idxV = aV1.getIndex();
        //                        int nc = 0;

        //                        long nlons = aLons.getSize();
        //                        long nlats = aLats.getSize();

        //                        int timeCheck = timeDimSize - 1;
        //                        float wt1 = 1;
        //                        float wt2 = 0;

        //                        if (doInterp)
        //                        {
        //                            wt1 = (float)((tMin2 - tMin0) / (tMin2 - tMin1));
        //                            wt2 = 1 - wt1;

        //                            if (t < timeCheck)
        //                            {
        //                                originU2[0] = t + 1;
        //                                originV2[0] = t + 1;
        //                            }
        //                            else
        //                            {
        //                                originU2[0] = t;
        //                                originV2[0] = t;
        //                            }

        //                            aU2 = vU.read(originU2, shapeU);
        //                            aV2 = vV.read(originV2, shapeV);
        //                        }
        //                        else
        //                        {
        //                            aU2 = aU1;
        //                            aV2 = aV1;
        //                        }

        //                        for (int c = 0; c < nCells; c++)
        //                        {
        //                            float sourceLon = aLons.getFloat(lonIndex.set(c));

        //                            // If this Longitude is in bounds, check Latitude
        //                            if (aoiWest <= sourceLon && sourceLon <= aoiEast)
        //                            {
        //                                float sourceLat = aLats.getFloat(latIndex.set(c));

        //                                // If this Latitude is in bounds lets fetch the data
        //                                if (aoiSouth <= sourceLat && sourceLat <= aoiNorth)
        //                                {
        //                                    float Uval;
        //                                    float Vval;

        //                                    float Uval1 = aU1.getFloat(idxV.set(0, c)); ;
        //                                    float Vval1 = aV1.getFloat(idxV.set(0, c)); ;
        //                                    float Uval2 = aU2.getFloat(idxV.set(0, c)); ;
        //                                    float Vval2 = aV2.getFloat(idxV.set(0, c)); ;

        //                                    if (util_.checkIsValid(Uval1) && util_.checkIsValid(Uval2) &&
        //                                            util_.checkIsValid(Vval1) && util_.checkIsValid(Vval2))
        //                                    {
        //                                        if (waterOrWind == 1 && source.ReverseWinds)
        //                                        {
        //                                            Uval1 = -Uval1;
        //                                            Vval1 = -Vval1;
        //                                            Uval2 = -Uval2;
        //                                            Vval2 = -Vval2;
        //                                        }

        //                                        Uval = Uval1 * wt1 + Uval2 * wt2;
        //                                        Vval = Vval1 * wt1 + Vval2 * wt2;

        //                                        Uval = util_.AdjustUsingScaleAndOffset(Uval, scaleFactor, offset) *
        //                                                util_.ConversionFactors(origUnits, "KNOTS");
        //                                        Vval = util_.AdjustUsingScaleAndOffset(Vval, scaleFactor, offset) *
        //                                                util_.ConversionFactors(origUnits, "KNOTS");

        //                                        Uval = Uval * SCALE_FACTOR;
        //                                        Vval = Vval * SCALE_FACTOR;
        //                                        short shortU = Convert.ToInt16(Uval);
        //                                        short shortV = Convert.ToInt16(Vval);

        //                                        if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                        {
        //                                            aUD2.setShort(imaU.set(0, nc), shortU);
        //                                            aVD2.setShort(imaV.set(0, nc), shortV);
        //                                        }
        //                                        else
        //                                        {
        //                                            aUD2f.setFloat(imaU.set(0, nc), Uval);
        //                                            aVD2f.setFloat(imaV.set(0, nc), Vval);
        //                                        }
        //                                    }
        //                                    else
        //                                    {
        //                                        if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                        {
        //                                            aUD2.setShort(imaU.set(0, nc), MISSING_VALUE);
        //                                            aVD2.setShort(imaV.set(0, nc), MISSING_VALUE);
        //                                        }
        //                                        else
        //                                        {
        //                                            aUD2f.setFloat(imaU.set(0, nc), MISSING_VALUE_F);
        //                                            aVD2f.setFloat(imaV.set(0, nc), MISSING_VALUE_F);
        //                                        }
        //                                    }

        //                                    fidD2.setShort(fidIndex.set(0, nc), 0);
        //                                    nc++;
        //                                }
        //                            }
        //                        }

        //                        try
        //                        {
        //                            if (waterOrWind == 1)
        //                            {
        //                                if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                {
        //                                    asaNC.file.write("wind_u", oriOut, aUD2);
        //                                }
        //                                else
        //                                {
        //                                    asaNC.file.write("wind_u", oriOut, aUD2f);
        //                                }
        //                            }
        //                            else
        //                            {
        //                                if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                {
        //                                    asaNC.file.write("U", oriOut, aUD2);
        //                                }
        //                                else
        //                                {
        //                                    asaNC.file.write("U", oriOut, aUD2f);
        //                                }
        //                            }
        //                        }
        //                        catch (Exception ex)
        //                        {
        //                            error = ex.ToString();
        //                            return false;
        //                        }

        //                        try
        //                        {
        //                            if (waterOrWind == 1)
        //                            {
        //                                if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                {
        //                                    asaNC.file.write("wind_v", oriOut, aVD2);
        //                                }
        //                                else
        //                                {
        //                                    asaNC.file.write("wind_v", oriOut, aVD2f);
        //                                }
        //                            }
        //                            else
        //                            {
        //                                if (edsOrder.OutputType == Global.COMPRESS_OUTPUT)
        //                                {
        //                                    asaNC.file.write("V", oriOut, aVD2);
        //                                }
        //                                else
        //                                {
        //                                    asaNC.file.write("V", oriOut, aVD2f);
        //                                }
        //                            }
        //                        }
        //                        catch (Exception ex)
        //                        {
        //                            error = ex.ToString();
        //                            return false;
        //                        }
        //                    }
        //                    catch (Exception ex)
        //                    {
        //                        error = ex.ToString();
        //                        return false;
        //                    }
        //                }
        //            }

        //            CDF.close();
        //        }

        //        asaNC.file.close();
        //        return true;
        //    }
        //    catch (Exception ex)
        //    {
        //        error = ex.StackTrace;
        //        return false;
        //    }
        //    finally
        //    {
        //        string ncLogFile = asaNC.file.name;
        //        ncLogFile = ncLogFile.ToLower().Replace(".nc", ".log");

        //        using (StreamWriter writer = new StreamWriter(ncLogFile, true))
        //        {
        //            if (error.Equals(""))
        //            {
        //                writer.WriteLine("Successfully filled the NetCDF");
        //            }
        //            else
        //            {
        //                writer.WriteLine("Could not fill the NetCDF. There were errors: " + error);
        //            }
        //        }

        //        error = "";
        //    }
        //}


        //public bool AddFile(ref ASANetCdf asaNC, string fileToRead, DataSource source)
        //{
        //    try
        //    {
        //        bool success = ReadCellFile(ref asaNC, fileToRead, source);

        //        if (success)
        //        {
        //            fileList.Add(fileToRead);
        //        }

        //        return success;
        //    }
        //    catch (Exception ex)
        //    {
        //        return false;
        //    }
        //    finally
        //    {
        //        string ncLogFile = asaNC.file.name;
        //        ncLogFile = ncLogFile.ToLower().Replace(".nc", ".log");

        //        using (StreamWriter writer = new StreamWriter(ncLogFile, true))
        //        {
        //            writer.WriteLine("\nProcessed and read: " + fileToRead);

        //            if (error.Equals(""))
        //            {
        //                writer.WriteLine(fileToRead + " to be used.");
        //            }
        //            else
        //            {
        //                writer.WriteLine("There were errors reading the file " + fileToRead);
        //                writer.WriteLine(error);
        //            }
        //        }

        //        error = "";
        //    }
        //}


        public int GetFileListSize()
        {
            return fileList.Count;
        }
    }
}
