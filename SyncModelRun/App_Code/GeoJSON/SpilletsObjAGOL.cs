using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

/// <summary>
///Poly Object for GeoJSON
/// {"geometry": {"x": 143.392730712891, "y": 52.4115562438965}, "attributes": {"DATETIME": "2014-03-12 21:00:00", "HOURS": "0", "SCENARIO_ID": "Sak_demo_2hr_31820141547", }}, {"geometry": {"x": 143.392730712891, "y": 52.4115562438965}, "attributes": {"DATETIME": "2014-03-12 21:00:00", "HOURS": "0", "SCENARIO_ID": "Sak_demo_2hr_31820141547", }}
/// </summary>
namespace SpilletsObjAGOL
{
    public class Spatialref
    {
        public int wkid = 4326;
    }

    public class Geometry
    {
        public double x { get; set; }
        public double y { get; set; }
        public Object spatialReference { get; set; }
    }

    public class Attributes
    {
        public string DATETIME { get; set; }
        public string HOURS { get; set; }
        public string SCENARIO_ID { get; set; }
    }

    public class SpilletsJSON
    {
        public Geometry geometry { get; set; }
        public Attributes attributes { get; set; }
    }
}