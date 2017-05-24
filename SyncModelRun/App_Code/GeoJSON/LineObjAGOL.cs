using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

/// <summary>
///Line Object for GeoJSON
/// [{"geometry": {"paths" : [[[143.400640869141, 52.4135502624512],[143.400793187758, 52.404691920561],[143.399529956636, 52.3934223538353],[143.396036376953, 52.3815179443359],[143.391316300732, 52.3747698250463],[143.386348895173, 52.3765598126312],[143.380777994792, 52.3890848286947],[143.375484103248, 52.4115781329927],[143.371558479641, 52.438455581665],[143.369929351807, 52.4641050338745]]]}, "attributes": {"DATIMETIME": "2013-10-16 11:00:00", "HOURS": 0,"SCENARIO_ID": "Sak_demo_2hr_31820141547"}}]
/// </summary>
namespace LineObjAGOL
{
    public class Spatialref
    {
        public int wkid = 4326;
    }

    public class Geometry
    {
        public List<List<List<double>>> paths { get; set; }
        public Object spatialReference { get; set; }
    }

    public class Attributes
    {
        public string DATIMETIME { get; set; }
        //public int HOURS { get; set; }
        public string SCENARIO_ID { get; set; }
        //public string ORG_ID { get; set; }
    }

    public class LineObjJSON
    {
        public Geometry geometry { get; set; }
        public Attributes attributes { get; set; }
    }
}