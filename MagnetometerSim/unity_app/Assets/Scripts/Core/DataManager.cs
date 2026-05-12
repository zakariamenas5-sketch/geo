using UnityEngine;
using System.IO;
using Newtonsoft.Json;
using MagnetometerSim.Physics;

namespace MagnetometerSim.Core
{
    /// <summary>
    /// مدير تحميل وحفظ بيانات JSON
    /// </summary>
    public class DataManager : MonoBehaviour
    {
        public static DataManager Instance { get; private set; }
        
        [Header("مسار البيانات")]
        public string dataPath = "Assets/Data";
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        /// <summary>
        /// تحميل نموذج جيولوجي من JSON
        /// </summary>
        public GeologicalModel LoadGeologicalModel(string fileName)
        {
            string path = Path.Combine(dataPath, fileName);
            
            if (!File.Exists(path))
            {
                Debug.LogError($"ملف النموذج غير موجود: {path}");
                return null;
            }
            
            try
            {
                string json = File.ReadAllText(path);
                GeologicalModel model = JsonConvert.DeserializeObject<GeologicalModel>(json);
                Debug.Log($"تم تحميل النموذج: {model?.scenarioName}");
                return model;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"خطأ في تحميل الملف: {e.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// تحميل بيانات مسح من JSON
        /// </summary>
        public SurveyData LoadSurveyData(string fileName)
        {
            string path = Path.Combine(dataPath, fileName);
            
            if (!File.Exists(path))
            {
                Debug.LogError($"ملف البيانات غير موجود: {path}");
                return null;
            }
            
            try
            {
                string json = File.ReadAllText(path);
                SurveyData data = JsonConvert.DeserializeObject<SurveyData>(json);
                Debug.Log($"تم تحميل بيانات المسح: {data?.surveyType}, النقاط: {data?.measurements?.Length}");
                return data;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"خطأ في تحميل الملف: {e.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// حفظ بيانات مسح إلى JSON
        /// </summary>
        public void SaveSurveyData(SurveyData data, string fileName)
        {
            string path = Path.Combine(dataPath, fileName);
            
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                string json = JsonConvert.SerializeObject(data, Formatting.Indented);
                File.WriteAllText(path, json);
                Debug.Log($"تم حفظ بيانات المسح: {path}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"خطأ في حفظ الملف: {e.Message}");
            }
        }
        
        /// <summary>
        /// تحميل إعدادات المحاكاة من ملف
        /// </summary>
        public SimulationSettings LoadSettings(string fileName = "settings.json")
        {
            string path = Path.Combine(dataPath, fileName);
            
            if (!File.Exists(path))
            {
                Debug.LogWarning("ملف الإعدادات غير موجود، سيتم استخدام الإعدادات الافتراضية");
                return new SimulationSettings();
            }
            
            try
            {
                string json = File.ReadAllText(path);
                SimulationSettings settings = JsonConvert.DeserializeObject<SimulationSettings>(json);
                return settings ?? new SimulationSettings();
            }
            catch
            {
                return new SimulationSettings();
            }
        }
    }
}
