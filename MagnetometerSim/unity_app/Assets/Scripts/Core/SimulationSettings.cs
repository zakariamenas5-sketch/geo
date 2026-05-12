using UnityEngine;
using System.Collections.Generic;

namespace MagnetometerSim.Core
{
    /// <summary>
    /// إعدادات المحاكاة - تدعم وضعي Dev و Full
    /// </summary>
    [System.Serializable]
    public class SimulationSettings
    {
        // وضع الأداء
        public enum PerformanceMode
        {
            Dev,      // شبكة خفيفة 10x10
            Full      // شبكة كثيفة 50x50
        }

        [Header("أداء المحاكاة")]
        public PerformanceMode mode = PerformanceMode.Dev;
        public int gridResolutionDev = 10;
        public int gridResolutionFull = 50;
        
        [Header("إعدادات المسح")]
        public float surveyAreaSize = 100f; // متر
        public float sensorHeight = 1.5f;   // متر فوق الأرض
        
        [Header("الفيزياء")]
        public float regionalFieldStrength = 45000f; // nT
        public Vector3 regionalFieldDirection = new Vector3(0.5f, 0.8f, 0.1f);
        
        [Header("الضوضاء والانحراف")]
        public bool enableNoise = true;
        public float noiseLevel = 5f; // nT
        public bool enableDrift = true;
        public float driftRate = 0.1f; // nT/second
        
        [Header("اللغة")]
        public enum Language { Arabic, French, English }
        public Language currentLanguage = Language.English;
        
        [Header("نوع الجهاز")]
        public enum MagnetometerType { PPM, Cesium, Fluxgate }
        public MagnetometerType deviceType = MagnetometerType.PPM;
        
        // خصائص محسوبة
        public int CurrentGridResolution => mode == PerformanceMode.Dev ? gridResolutionDev : gridResolutionFull;
        public float CellSize => surveyAreaSize / CurrentGridResolution;
        
        public void Validate()
        {
            surveyAreaSize = Mathf.Max(10f, surveyAreaSize);
            sensorHeight = Mathf.Max(0.5f, sensorHeight);
            noiseLevel = Mathf.Max(0f, noiseLevel);
        }
    }
}
