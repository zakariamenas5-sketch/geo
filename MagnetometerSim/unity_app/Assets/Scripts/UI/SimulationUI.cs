using UnityEngine;
using UnityEngine.UI;

namespace MagnetometerSim.UI
{
    /// <summary>
    /// واجهة المستخدم الرئيسية للمحاكاة
    /// </summary>
    public class SimulationUI : MonoBehaviour
    {
        [Header("عناصر العرض")]
        public Text totalFieldText;
        public Text anomalyText;
        public Text coordinatesText;
        public Slider progressBar;
        public Text progressText;
        
        [Header="أزرار التحكم"]
        public Button startSurveyButton;
        public Button stopSurveyButton;
        public Button toggleModeButton;
        
        [Header("قائمة السيناريوهات")]
        public Dropdown scenarioDropdown;
        
        [Header("قائمة اللغات")]
        public Dropdown languageDropdown;
        
        [Header("تحكم الأجسام")]
        public Slider depthSlider;
        public Slider susceptibilitySlider;
        public Text depthValueText;
        public Text susValueText;
        
        [Header("معلومات الجهاز")]
        public Text deviceTypeText;
        public Text performanceModeText;
        
        private Core.SimulationManager simManager;
        private LocalizationManager localization;
        
        private void Start()
        {
            simManager = Core.SimulationManager.Instance;
            localization = LocalizationManager.Instance;
            
            SetupButtons();
            SetupDropdowns();
            UpdateLanguage();
        }
        
        private void SetupButtons()
        {
            if (startSurveyButton != null)
                startSurveyButton.onClick.AddListener(OnStartSurveyClicked);
            
            if (stopSurveyButton != null)
                stopSurveyButton.onClick.AddListener(OnStopSurveyClicked);
            
            if (toggleModeButton != null)
                toggleModeButton.onClick.AddListener(OnToggleModeClicked);
        }
        
        private void SetupDropdowns()
        {
            if (scenarioDropdown != null)
            {
                scenarioDropdown.ClearOptions();
                scenarioDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    localization.Get("mining_scenario"),
                    localization.Get("oil_scenario"),
                    localization.Get("archaeology_scenario")
                });
                scenarioDropdown.onValueChanged.AddListener(OnScenarioChanged);
            }
            
            if (languageDropdown != null)
            {
                languageDropdown.ClearOptions();
                languageDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "English",
                    "Français",
                    "العربية"
                });
                languageDropdown.onValueChanged.AddListener(OnLanguageChanged);
            }
        }
        
        private void Update()
        {
            UpdateDisplay();
        }
        
        private void UpdateDisplay()
        {
            // تحديث القراءات يتم من SimulationManager
            // هنا نعرض معلومات إضافية
            
            if (simManager != null && simManager.surveyEngine != null)
            {
                Vector3 pos = simManager.surveyEngine.GetCurrentPosition();
                if (coordinatesText != null)
                {
                    coordinatesText.text = $"X: {pos.x:F2}m, Y: {pos.z:F2}m, Z: {pos.y:F2}m";
                }
                
                if (progressBar != null)
                {
                    float progress = simManager.surveyEngine.GetProgress() * 100f;
                    progressBar.value = progress / 100f;
                    if (progressText != null)
                        progressText.text = $"{progress:F1}%";
                }
            }
        }
        
        private void OnStartSurveyClicked()
        {
            if (simManager != null)
            {
                simManager.StartSurvey();
            }
        }
        
        private void OnStopSurveyClicked()
        {
            if (simManager != null)
            {
                simManager.StopSurvey();
            }
        }
        
        private void OnToggleModeClicked()
        {
            if (simManager != null && simManager.settings != null)
            {
                var currentMode = simManager.settings.mode;
                var newMode = currentMode == Core.SimulationSettings.PerformanceMode.Dev 
                    ? Core.SimulationSettings.PerformanceMode.Full 
                    : Core.SimulationSettings.PerformanceMode.Dev;
                
                simManager.TogglePerformanceMode(newMode);
                UpdateModeDisplay();
            }
        }
        
        private void OnScenarioChanged(int index)
        {
            string[] files = { "mining_model.json", "oil_gas_model.json", "archaeology_model.json" };
            if (index >= 0 && index < files.Length)
            {
                simManager?.LoadScenario(files[index]);
            }
        }
        
        private void OnLanguageChanged(int index)
        {
            LocalizationManager.Language lang = (LocalizationManager.Language)index;
            localization?.SetLanguage(lang);
            UpdateLanguage();
        }
        
        private void UpdateLanguage()
        {
            if (localization == null) return;
            
            if (startSurveyButton != null && startSurveyButton.GetComponentInChildren<Text>() != null)
                startSurveyButton.GetComponentInChildren<Text>().text = localization.Get("survey_start");
            
            if (stopSurveyButton != null && stopSurveyButton.GetComponentInChildren<Text>() != null)
                stopSurveyButton.GetComponentInChildren<Text>().text = localization.Get("survey_stop");
            
            UpdateModeDisplay();
        }
        
        private void UpdateModeDisplay()
        {
            if (simManager == null || simManager.settings == null) return;
            
            if (performanceModeText != null && localization != null)
            {
                var mode = simManager.settings.mode;
                performanceModeText.text = mode == Core.SimulationSettings.PerformanceMode.Dev 
                    ? localization.Get("dev_mode") 
                    : localization.Get("full_mode");
            }
        }
    }
}
