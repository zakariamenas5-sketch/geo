using UnityEngine;
using System;

namespace MagnetometerSim.Physics
{
    /// <summary>
    /// بيانات نقطة قياس مغناطيسي
    /// </summary>
    [Serializable]
    public class MagneticMeasurement
    {
        public double x, y, z;          // الإحداثيات (متر)
        public double totalField;       // المجال الكلي (nT)
        public double bx, by, bz;       // المركبات (nT)
        public double anomaly;          // الشذوذ المغناطيسي (nT)
        public double timestamp;        // الوقت (ثواني)
        
        public MagneticMeasurement() { }
        
        public MagneticMeasurement(double x, double y, double z, double total, 
                                   double bx, double by, double bz, double anomaly, double time)
        {
            this.x = x;
            this.y = y;
            this.z = z;
            this.totalField = total;
            this.bx = bx;
            this.by = by;
            this.bz = bz;
            this.anomaly = anomaly;
            this.timestamp = time;
        }
    }
    
    /// <summary>
    /// جسم جيولوجي في النموذج
    /// </summary>
    [Serializable]
    public class GeologicalBody
    {
        public string id;
        public string type;             // prism, pipe, layer, fault
        public double centerX, centerY, centerZ;
        public double sizeX, sizeY, sizeZ;
        public double susceptibility;   // القابلية المغناطيسية
        public double rotation;         // زاوية الدوران
        
        public GeologicalBody() { }
        
        public GeologicalBody(string id, string type, double cx, double cy, double cz,
                             double sx, double sy, double sz, double sus, double rot = 0)
        {
            this.id = id;
            this.type = type;
            this.centerX = cx;
            this.centerY = cy;
            this.centerZ = cz;
            this.sizeX = sx;
            this.sizeY = sy;
            this.sizeZ = sz;
            this.susceptibility = sus;
            this.rotation = rot;
        }
    }
    
    /// <summary>
    /// بيانات نموذج جيولوجي كامل
    /// </summary>
    [Serializable]
    public class GeologicalModel
    {
        public string scenarioName;
        public GeologicalBody[] bodies;
        public double regionalField;
        
        public GeologicalModel() { }
        
        public GeologicalModel(string name, GeologicalBody[] bodies, double regional)
        {
            this.scenarioName = name;
            this.bodies = bodies;
            this.regionalField = regional;
        }
    }
    
    /// <summary>
    /// بيانات مسح كاملة
    /// </summary>
    [Serializable]
    public class SurveyData
    {
        public string surveyType;       // grid, line
        public int resolution;
        public float areaSize;
        public MagneticMeasurement[] measurements;
        public GeologicalModel model;
        
        public SurveyData() { }
        
        public SurveyData(string type, int res, float size, MagneticMeasurement[] data, GeologicalModel model)
        {
            this.surveyType = type;
            this.resolution = res;
            this.areaSize = size;
            this.measurements = data;
            this.model = model;
        }
    }
}
