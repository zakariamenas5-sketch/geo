using UnityEngine;
using System.Collections.Generic;

namespace MagnetometerSim.UI
{
    /// <summary>
    /// نظام إدارة اللغات (عربي، فرنسي، إنجليزي)
    /// </summary>
    public class LocalizationManager : MonoBehaviour
    {
        public enum Language { Arabic, French, English }
        
        public static LocalizationManager Instance { get; private set; }
        
        [Header("اللغة الحالية")]
        public Language currentLanguage = Language.English;
        
        [Header("النصوص المترجمة")]
        public Dictionary<string, string> translations = new Dictionary<string, string>();
        
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
            
            LoadTranslations();
        }
        
        /// <summary>
        /// تحميل الترجمات
        /// </summary>
        private void LoadTranslations()
        {
            translations.Clear();
            
            // نصوص واجهة المستخدم
            translations["survey_start"] = GetLocalizedSurveyStart();
            translations["survey_stop"] = GetLocalizedSurveyStop();
            translations["total_field"] = GetLocalizedTotalField();
            translations["anomaly"] = GetLocalizedAnomaly();
            translations["progress"] = GetLocalizedProgress();
            translations["dev_mode"] = GetLocalizedDevMode();
            translations["full_mode"] = GetLocalizedFullMode();
            translations["mining_scenario"] = GetLocalizedMiningScenario();
            translations["oil_scenario"] = GetLocalizedOilScenario();
            translations["archaeology_scenario"] = GetLocalizedArchaeologyScenario();
        }
        
        /// <summary>
        /// الحصول على نص مترجم
        /// </summary>
        public string Get(string key)
        {
            if (translations.ContainsKey(key))
            {
                return translations[key];
            }
            return key;
        }
        
        /// <summary>
        /// تغيير اللغة
        /// </summary>
        public void SetLanguage(Language lang)
        {
            currentLanguage = lang;
            LoadTranslations();
            Debug.Log($"Language changed to: {lang}");
        }
        
        // ==================== English ====================
        private string GetLocalizedSurveyStart()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "بدء المسح";
                case Language.French: return "Démarrer l'enquête";
                default: return "Start Survey";
            }
        }
        
        private string GetLocalizedSurveyStop()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "إيقاف المسح";
                case Language.French: return "Arrêter l'enquête";
                default: return "Stop Survey";
            }
        }
        
        private string GetLocalizedTotalField()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "المجال الكلي";
                case Language.French: return "Champ total";
                default: return "Total Field";
            }
        }
        
        private string GetLocalizedAnomaly()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "الشذوذ";
                case Language.French: return "Anomalie";
                default: return "Anomaly";
            }
        }
        
        private string GetLocalizedProgress()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "التقدم";
                case Language.French: return "Progrès";
                default: return "Progress";
            }
        }
        
        private string GetLocalizedDevMode()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "وضع التطوير (خفيف)";
                case Language.French: return "Mode Développement (Léger)";
                default: return "Dev Mode (Light)";
            }
        }
        
        private string GetLocalizedFullMode()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "الوضع الكامل (دقة عالية)";
                case Language.French: return "Mode Complet (Haute Précision)";
                default: return "Full Mode (High Precision)";
            }
        }
        
        private string GetLocalizedMiningScenario()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "سيناريو التعدين";
                case Language.French: return "Scénario Minier";
                default: return "Mining Scenario";
            }
        }
        
        private string GetLocalizedOilScenario()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "سيناريو النفط والغاز";
                case Language.French: return "Scénario Pétrole et Gaz";
                default: return "Oil & Gas Scenario";
            }
        }
        
        private string GetLocalizedArchaeologyScenario()
        {
            switch (currentLanguage)
            {
                case Language.Arabic: return "سيناريو الآثار";
                case Language.French: return "Scénario Archéologique";
                default: return "Archaeology Scenario";
            }
        }
    }
}
