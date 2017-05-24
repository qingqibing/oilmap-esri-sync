using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Drawing;

    public enum ShapeFileType
    {
        SHAPE_TYPE_POINTS = 1,
        SHAPE_TYPE_LINES = 3,
        SHAPE_TYPE_POLYGONS = 5
    }

    public struct Line
    {
        public double[] box;
        public int numParts;
        public int numPoints;
        public int[] parts;
        public PointF[] points;
    }


    public struct Polygon
    {
        public double[] box;
        public int numParts;
        public int numPoints;
        public int[] parts;
        public PointF[] points;
    }


public class ShapeFile
{
    private string m_sFilename;
    private List<PointF> m_aPoints;
    private List<Line> m_aLines;
    private List<Polygon> m_aPolygons;
    private ShapeFileType m_eShapeType;

    private int m_iFilecode;
    private int m_iFileLength;
    private int m_iVersion;
    private double m_dxMin;
    private double m_dyMin;
    private double m_dxMax;
    private double m_dyMax;
    private double m_dzMin;
    private double m_dzMax;
    private double m_dmMin;
    private double m_dmMax;

    public string Filename
    {
        get { return m_sFilename; }
        set { m_sFilename = value; }
    }

    public List<PointF> Points
    {
        get { return m_aPoints; }
        set { m_aPoints = value; }
    }

    public List<Line> Lines
    {
        get { return m_aLines; }
        set { m_aLines = value; }
    }

    public List<Polygon> Polygons
    {
        get { return m_aPolygons; }
        set { m_aPolygons = value; }
    }

    public ShapeFileType ShapeType
    {
        get { return m_eShapeType; }
        set { m_eShapeType = value; }
    }

    public ShapeFile()
    {
        m_aPoints = new List<PointF>();
        m_aLines = new List<Line>();
        m_aPolygons = new List<Polygon>();
    }

    public void LoadShapeFile(string sFilename)
    {
        m_sFilename = sFilename;
        LoadShapeFile();
    }

    public void LoadShapeFile()
    {
        readShapeFile();
    }

    private void readShapeFile()
    {
        FileStream fs = new FileStream(m_sFilename, FileMode.Open);
        long fileLength = fs.Length;
        Byte[] data = new Byte[fileLength];
        fs.Read(data, 0, (int)fileLength);
        fs.Close();
        m_iFilecode = readIntBig(data, 0);
        m_iFileLength = readIntBig(data, 24);
        m_iVersion = readIntLittle(data, 28);
        m_eShapeType = (ShapeFileType)readIntLittle(data, 32);
        m_dxMin = readDoubleLittle(data, 36);
        m_dyMin = readDoubleLittle(data, 44);
        m_dyMin = 0 - m_dyMin;
        m_dxMax = readDoubleLittle(data, 52);
        m_dyMax = readDoubleLittle(data, 60);
        m_dyMax = 0 - m_dyMax;
        m_dzMin = readDoubleLittle(data, 68);
        m_dzMax = readDoubleLittle(data, 76);
        m_dmMin = readDoubleLittle(data, 84);
        m_dmMax = readDoubleLittle(data, 92);
        int currentPosition = 100;
        while (currentPosition < m_iFileLength)
        {
            int recordStart = currentPosition;
            int recordNumber = readIntBig(data, recordStart);
            int contentLength = readIntBig(data, recordStart + 4);
            int recordContentStart = recordStart + 8;
            if (m_eShapeType == ShapeFileType.SHAPE_TYPE_POINTS)
            {
                PointF point = new PointF();
                int recordShapeType = readIntLittle(data, recordContentStart);
                point.X = (float)readDoubleLittle(data, recordContentStart + 4);
                point.Y = 0 - (float)readDoubleLittle(data, recordContentStart + 12);
                m_aPoints.Add(point);
            }
            if (m_eShapeType == ShapeFileType.SHAPE_TYPE_LINES)
            {
                Line line = new Line();
                int recordShapeType = readIntLittle(data, recordContentStart);
                line.box = new Double[4];
                line.box[0] = readDoubleLittle(data, recordContentStart + 4);
                line.box[1] = readDoubleLittle(data, recordContentStart + 12);
                line.box[2] = readDoubleLittle(data, recordContentStart + 20);
                line.box[3] = readDoubleLittle(data, recordContentStart + 28);
                line.numParts = readIntLittle(data, recordContentStart + 36);
                line.parts = new int[line.numParts];
                line.numPoints = readIntLittle(data, recordContentStart + 40);
                line.points = new PointF[line.numPoints];
                int partStart = recordContentStart + 44;
                for (int i = 0; i < line.numParts; i++)
                {
                    line.parts[i] = readIntLittle(data, partStart + i * 4);
                }
                int pointStart = recordContentStart + 44 + 4 * line.numParts;
                for (int i = 0; i < line.numPoints; i++)
                {
                    line.points[i].X = (float)readDoubleLittle(data, pointStart + (i * 16));
                    line.points[i].Y = (float)readDoubleLittle(data, pointStart + (i * 16) + 8);
                    line.points[i].Y = 0 - line.points[i].Y;
                }
                m_aLines.Add(line);
            }
            if (m_eShapeType == ShapeFileType.SHAPE_TYPE_POLYGONS)
            {
                Polygon polygon = new Polygon();
                int recordShapeType = readIntLittle(data, recordContentStart);
                polygon.box = new Double[4];
                polygon.box[0] = readDoubleLittle(data, recordContentStart + 4);
                polygon.box[1] = readDoubleLittle(data, recordContentStart + 12);
                polygon.box[2] = readDoubleLittle(data, recordContentStart + 20);
                polygon.box[3] = readDoubleLittle(data, recordContentStart + 28);
                polygon.numParts = readIntLittle(data, recordContentStart + 36);
                polygon.parts = new int[polygon.numParts];
                polygon.numPoints = readIntLittle(data, recordContentStart + 40);
                polygon.points = new PointF[polygon.numPoints];
                int partStart = recordContentStart + 44;
                for (int i = 0; i < polygon.numParts; i++)
                {
                    polygon.parts[i] = readIntLittle(data, partStart + i * 4);
                }
                int pointStart = recordContentStart + 44 + 4 * polygon.numParts;
                for (int i = 0; i < polygon.numPoints; i++)
                {
                    polygon.points[i].X = (float)readDoubleLittle(data, pointStart + (i * 16));
                    polygon.points[i].Y = (float)readDoubleLittle(data, pointStart + (i * 16) + 8);
                    //polygon.points[i].Y = 0 - polygon.points[i].Y;
                }
                m_aPolygons.Add(polygon);
            }
            currentPosition = recordStart + (4 + contentLength) * 2;
        }
    }

    private int readIntBig(byte[] data, int pos)
    {
        byte[] bytes = new byte[4];
        bytes[0] = data[pos];
        bytes[1] = data[pos + 1];
        bytes[2] = data[pos + 2];
        bytes[3] = data[pos + 3];
        Array.Reverse(bytes);
        return BitConverter.ToInt32(bytes, 0);
    }

    private int readIntLittle(byte[] data, int pos)
    {
        byte[] bytes = new byte[4];
        bytes[0] = data[pos];
        bytes[1] = data[pos + 1];
        bytes[2] = data[pos + 2];
        bytes[3] = data[pos + 3];
        return BitConverter.ToInt32(bytes, 0);
    }

    private double readDoubleLittle(byte[] data, int pos)
    {
        byte[] bytes = new byte[8];
        bytes[0] = data[pos];
        bytes[1] = data[pos + 1];
        bytes[2] = data[pos + 2];
        bytes[3] = data[pos + 3];
        bytes[4] = data[pos + 4];
        bytes[5] = data[pos + 5];
        bytes[6] = data[pos + 6];
        bytes[7] = data[pos + 7];
        return BitConverter.ToDouble(bytes, 0);
    }
}
