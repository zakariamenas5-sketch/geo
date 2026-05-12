using UnityEngine;
using MagnetometerSim.Physics;
using MagnetometerSim.Survey;
using MagnetometerSim.Visualization;

namespace MagnetometerSim.Core
{
    /// <summary>
    /// المدير الرئيسي للمحاكاة - يربط جميع الأنظمة
    /// </summary>
    public class SimulationManager : MonoBehaviour
    {
        [Header("المكونات")]
        public SimulationSettings settings;
        public MagneticPhysicsEngine physicsEngine;
        public SurveyEngine surveyEngine;
        public MagneticHeatmap heatmap;
        
        [Header("البيانات")]
        public GeologicalModel currentModel;
        public MagneticMeasurement[] currentMeasurements;
        
        [Header("الجهاز المغناطيسي")]
        public Transform magnetometerSensor;
        public GameObject ppmDeviceModel;
        
        [Header("واجهة المستخدم")]
        public UnityEngine.UI.Text readingDisplay;
        public UnityEngine.UI.Text anomalyDisplay;
        public UnityEngine.UI.ProgressBar progressBar;
        
        private bool isRunning = false;
        private double simulationStartTime;
        
        public static SimulationManager Instance { get; private set; }
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
                return;
            }
            
            InitializeComponents();
        }
        
        /// <summary>
        /// تهيئة جميع المكونات
        /// </summary>
        private void InitializeComponents()
        {
            settings.Validate();
            
            if (physicsEngine != null)
                physicsEngine.Initialize(settings);
            
            if (surveyEngine != null)
                surveyEngine.Initialize(settings, physicsEngine);
            
            if (heatmap != null)
                heatmap.Initialize(settings.CurrentGridResolution, settings.surveyAreaSize);
            
            Debug.Log("تم تهيئة مدير المحاكاة بنجاح");
        }
        
        /// <summary>
        /// تحميل سيناريو جيولوجي
        /// </summary>
        public void LoadScenario(string scenarioFile)
        {
            DataManager dataManager = DataManager.Instance;
            if (dataManager == null)
            {
                Debug.LogError("DataManager غير موجود!");
                return;
            }
            
            currentModel = dataManager.LoadGeologicalModel(scenarioFile);
            if (currentModel != null)
            {
                Debug.Log($"تم تحميل السيناريو: {currentModel.scenarioName}");
                UpdateVisualization();
            }
        }
        
        /// <summary>
        /// بدء المسح
        /// </summary>
        public void StartSurvey()
        {
            if (currentModel == null)
            {
                Debug.LogWarning("لم يتم تحميل نموذج جيولوجي!");
                return;
            }
            
            isRunning = true;
            simulationStartTime = Time.time;
            surveyEngine.StartSurvey();
            
            Debug.Log("بدأ المسح المغناطيسي");
        }
        
        /// <summary>
        /// إيقاف المسح
        /// </summary>
        public void StopSurvey()
        {
            isRunning = false;
            surveyEngine.StopSurvey();
        }
        
        private void Update()
        {
            if (!isRunning) return;
            
            // تحديث موقع الجهاز
            UpdateMagnetometerPosition();
            
            // أخذ قراءة
            TakeMeasurement();
            
            // تحديث واجهة المستخدم
            UpdateUI();
            
            // التحقق من اكتمال المسح
            if (surveyEngine.GetProgress() >= 0.99f)
            {
                CompleteSurvey();
            }
        }
        
        /// <summary>
        /// تحديث موقع جهاز المغناطيسومتر
        /// </summary>
        private void UpdateMagnetometerPosition()
        {
            if (magnetometerSensor != null && surveyEngine != null)
            {
                Vector3 targetPos = surveyEngine.GetCurrentPosition();
                magnetometerSensor.position = targetPos;
            }
        }
        
        /// <summary>
        /// أخذ قراءة مغناطيسية
        /// </summary>
        private void TakeMeasurement()
        {
            if (surveyEngine == null || currentModel == null) return;
            
            var measurement = surveyEngine.TakeMeasurement(currentModel.bodies);
            
            // تحديث القراءة الحالية
            if (readingDisplay != null)
            {
                readingDisplay.text = $"{measurement.totalField:F1} nT";
            }
            
            if (anomalyDisplay != null)
            {
                string sign = measurement.anomaly >= 0 ? "+" : "";
                anomalyDisplay.text = $"{sign}{measurement.anomaly:F2} nT";
            }
        }
        
        /// <summary>
        /// تحديث واجهة المستخدم
        /// </summary>
        private void UpdateUI()
        {
            if (progressBar != null && surveyEngine != null)
            {
                progressBar.value = surveyEngine.GetProgress();
            }
        }
        
        /// <summary>
        /// إكمال المسح وتوليد التصور
        /// </summary>
        private void CompleteSurvey()
        {
            StopSurvey();
            
            if (surveyEngine != null && currentModel != null)
            {
                currentMeasurements = surveyEngine.ExecuteFullSurvey(currentModel.bodies);
                UpdateVisualization();
                Debug.Log("اكتمل المسح بنجاح!");
            }
        }
        
        /// <summary>
        /// تحديث التصور البصري
        /// </summary>
        public void UpdateVisualization()
        {
            if (heatmap == null || currentMeasurements == null) return;
            
            int res = settings.CurrentGridResolution;
            float[,] values = new float[res, res];
            
            // تحويل القياسات إلى مصفوفة
            int index = 0;
            for (int y = 0; y < res; y++)
            {
                for (int x = 0; x < res; x++)
                {
                    if (index < currentMeasurements.Length)
                    {
                        values[x, y] = (float)currentMeasurements[index].anomaly;
                        index++;
                    }
                }
            }
            
            // تحديث نطاق الألوان
            float minVal = float.MaxValue;
            float maxVal = float.MinValue;
            
            foreach (var m in currentMeasurements)
            {
                if (m.anomaly < minVal) minVal = (float)m.anomaly;
                if (m.anomaly > maxVal) maxVal = (float)m.anomaly;
            }
            
            heatmap.minValue = minVal;
            heatmap.maxValue = maxVal;
            
            heatmap.UpdateHeatmapColors(values);
        }
        
        /// <summary>
        /// تغيير عمق الجسم الجيولوجي
        /// </summary>
        public void ChangeBodyDepth(string bodyId, double newDepth)
        {
            if (currentModel == null || currentModel.bodies == null) return;
            
            foreach (var body in currentModel.bodies)
            {
                if (body.id == bodyId)
                {
                    body.centerZ = newDepth;
                    Debug.Log($"تم تغيير عمق {bodyId} إلى {newDepth}م");
                    break;
                }
            }
        }
        
        /// <summary>
        /// تغيير القابلية المغناطيسية
        /// </summary>
        public void ChangeSusceptibility(string bodyId, double newSusceptibility)
        {
            if (currentModel == null || currentModel.bodies == null) return;
            
            foreach (var body in currentModel.bodies)
            {
                if (body.id == bodyId)
                {
                    body.susceptibility = newSusceptibility;
                    Debug.Log($"تم تغيير القابلية المغناطيسية لـ {bodyId} إلى {newSusceptibility}");
                    break;
                }
            }
        }
        
        /// <summary>
        /// تبديل وضع الأداء
        /// </summary>
        public void TogglePerformanceMode(SimulationSettings.PerformanceMode newMode)
        {
            settings.mode = newMode;
            InitializeComponents();
            Debug.Log($"تم التبديل إلى وضع: {newMode}");
        }
    }
}
