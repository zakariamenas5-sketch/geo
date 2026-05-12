using UnityEngine;
using System.Collections.Generic;
using MagnetometerSim.Physics;

namespace MagnetometerSim.Survey
{
    /// <summary>
    /// محرك تخطيط وتنفيذ المسح المغناطيسي
    /// </summary>
    public class SurveyEngine : MonoBehaviour
    {
        [Header("نوع المسح")]
        public enum SurveyType { Grid, Line, Walking, Drone }
        public SurveyType currentSurveyType = SurveyType.Grid;
        
        [Header("إعدادات الشبكة")]
        public float areaSize = 100f;
        public int resolution = 10;
        public float lineSpacing = 10f;
        public float pointSpacing = 2f;
        
        [Header("حركة المسح")]
        public float surveySpeed = 2f; // م/ث
        public bool isSurveying = false;
        
        private List<Vector3> surveyPath = new List<Vector3>();
        private int currentPointIndex = 0;
        private double surveyStartTime = 0;
        
        private MagneticPhysicsEngine physicsEngine;
        private SimulationSettings settings;
        
        public void Initialize(SimulationSettings simSettings, MagneticPhysicsEngine physEngine)
        {
            settings = simSettings;
            physicsEngine = physEngine;
            UpdateSurveyParameters();
        }
        
        /// <summary>
        /// تحديث معاملات المسح حسب الإعدادات
        /// </summary>
        public void UpdateSurveyParameters()
        {
            if (settings != null)
            {
                areaSize = settings.surveyAreaSize;
                resolution = settings.CurrentGridResolution;
            }
            
            GenerateSurveyPath();
        }
        
        /// <summary>
        /// توليد مسار المسح حسب النوع
        /// </summary>
        public void GenerateSurveyPath()
        {
            surveyPath.Clear();
            float halfSize = areaSize / 2f;
            float sensorHeight = settings != null ? settings.sensorHeight : 1.5f;
            
            switch (currentSurveyType)
            {
                case SurveyType.Grid:
                    GenerateGridSurvey(halfSize, sensorHeight);
                    break;
                case SurveyType.Line:
                    GenerateLineSurvey(halfSize, sensorHeight);
                    break;
                case SurveyType.Walking:
                case SurveyType.Drone:
                    GenerateGridSurvey(halfSize, sensorHeight);
                    break;
            }
            
            Debug.Log($"تم توليد مسار المسح: {surveyPath.Count} نقطة");
        }
        
        /// <summary>
        /// توليد مسح شبكي
        /// </summary>
        private void GenerateGridSurvey(float halfSize, float height)
        {
            float step = areaSize / resolution;
            
            for (int i = 0; i <= resolution; i++)
            {
                float x = -halfSize + i * step;
                
                for (int j = 0; j <= resolution; j++)
                {
                    float y = -halfSize + j * step;
                    surveyPath.Add(new Vector3(x, height, y));
                }
            }
        }
        
        /// <summary>
        /// توليد مسح خطي
        /// </summary>
        private void GenerateLineSurvey(float halfSize, float height)
        {
            float step = pointSpacing;
            int numPoints = (int)(areaSize / step);
            
            for (int i = 0; i <= numPoints; i++)
            {
                float x = -halfSize + i * step;
                surveyPath.Add(new Vector3(x, height, 0));
            }
        }
        
        /// <summary>
        /// بدء المسح
        /// </summary>
        public void StartSurvey()
        {
            isSurveying = true;
            currentPointIndex = 0;
            surveyStartTime = Time.time;
        }
        
        /// <summary>
        /// إيقاف المسح
        /// </summary>
        public void StopSurvey()
        {
            isSurveying = false;
        }
        
        /// <summary>
        /// الحصول على النقطة الحالية في المسح
        /// </summary>
        public Vector3 GetCurrentPosition()
        {
            if (surveyPath.Count == 0 || currentPointIndex >= surveyPath.Count)
                return Vector3.zero;
            
            return surveyPath[currentPointIndex];
        }
        
        /// <summary>
        /// التقدم إلى النقطة التالية
        /// </summary>
        public bool MoveToNextPoint()
        {
            if (!isSurveying || currentPointIndex >= surveyPath.Count - 1)
                return false;
            
            currentPointIndex++;
            return true;
        }
        
        /// <summary>
        /// قياس المجال المغناطيسي في النقطة الحالية
        /// </summary>
        public MagneticMeasurement TakeMeasurement(GeologicalBody[] bodies)
        {
            Vector3 pos = GetCurrentPosition();
            double timestamp = Time.time - surveyStartTime;
            
            return physicsEngine.CalculateTotalField(pos, bodies, timestamp);
        }
        
        /// <summary>
        /// تنفيذ مسح كامل وحفظ النتائج
        /// </summary>
        public MagneticMeasurement[] ExecuteFullSurvey(GeologicalBody[] bodies)
        {
            var measurements = new List<MagneticMeasurement>();
            double startTime = Time.time;
            
            for (int i = 0; i < surveyPath.Count; i++)
            {
                Vector3 pos = surveyPath[i];
                double timestamp = Time.time - startTime;
                
                var measurement = physicsEngine.CalculateTotalField(pos, bodies, timestamp);
                measurements.Add(measurement);
            }
            
            Debug.Log($"اكتمل المسح: {measurements.Count} قراءة");
            return measurements.ToArray();
        }
        
        /// <summary>
        /// الحصول على نسبة التقدم في المسح
        /// </summary>
        public float GetProgress()
        {
            if (surveyPath.Count == 0) return 0;
            return (float)currentPointIndex / surveyPath.Count;
        }
        
        /// <summary>
        /// رسم مسار المسح للتصور
        /// </summary>
        public void DrawSurveyPath()
        {
            if (surveyPath.Count < 2) return;
            
            for (int i = 0; i < surveyPath.Count - 1; i++)
            {
                Debug.DrawLine(surveyPath[i], surveyPath[i + 1], Color.yellow, 60f);
            }
        }
    }
}
