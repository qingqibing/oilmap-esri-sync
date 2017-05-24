using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

/// <summary>
///Poly Object for GeoJSON
/// {"geometry": {"rings": [[[143.394074706826, 52.410758972168], [143.394561157009, 52.410758972168], [143.394561157009, 52.4114239502233], [143.394074706826, 52.4114239502233], [143.394074706826, 52.410758972168]]]}, "attributes": {"DATETIME": "2014-03-12 23:00:00", "HOURS": "2", "SCENARIO_ID": "Sak_demo_2hr_31820141547", "THICK_MM": 0.135706871747971, "ORG_ID": "SDRiK3IojFEsZQ2z"}}, {"geometry": {"rings": [[[143.394561157009, 52.410758972168], [143.395047607191, 52.410758972168], [143.395047607191, 52.4114239502233], [143.394561157009, 52.4114239502233], [143.394561157009, 52.410758972168]]]}, "attributes": {"DATETIME": "2014-03-12 23:00:00", "HOURS": "2", "SCENARIO_ID": "Sak_demo_2hr_31820141547", "THICK_MM": 0.156166687607765, "ORG_ID": "SDRiK3IojFEsZQ2z"}}
/// </summary>
namespace PolyObjAGOL
{
    public class Spatialref
    {
        public int wkid = 4326;
    }

    public class Geometry
    {
        public List<List<List<double>>> rings { get; set; }
        public Object spatialReference { get; set; }
    }

    public class Attributes
    {
        public string DATETIME { get; set; }
        //public string HOURS { get; set; }
        public string SCENARIO_ID { get; set; }
        public double THICK_MM { get; set; }
        //public string ORG_ID { get; set; }
    }

    public class PolyObjJSON
    {
        public Geometry geometry { get; set; }
        public Attributes attributes { get; set; }
    }
}