using UnityEngine;
using UnityEngine.UI;

namespace MagSim.UI
{
    /// <summary>
    /// شاشة عرض رقمية تحاكي شاشة جهاز PPM الحقيقي.
    /// تعرض القراءات المغناطيسية (nT) مع تأثيرات بصرية للواقعية.
    /// </summary>
    public class DigitalDisplay : MonoBehaviour
    {
        [Header("Display Settings")]
        public Text mainValueText;       // القيمة الرئيسية (Total Field)
        public Text anomalyValueText;    // قيمة الشذوذ
        public Text statusText;          // حالة الجهاز
        public Text timeText;            // الوقت
        
        [Header("Visual Effects")]
        public Color normalColor = Color.green;
        public Color anomalyColor = Color.red;
        public float updateRate = 0.5f;  // تحديث كل نصف ثانية (مثل PPM الحقيقي)
        
        private float lastUpdateTime;
        private float currentField = 0f;
        private float currentAnomaly = 0f;

        void Start()
        {
            if (mainValueText) mainValueText.text = "----";
            if (anomalyValueText) anomalyValueText.text = "----";
            if (statusText) statusText.text = "READY";
            UpdateTime();
        }

        void Update()
        {
            UpdateTime();
            
            // محاكاة تأخير القياس في PPM الحقيقي
            if (Time.time - lastUpdateTime >= updateRate)
            {
                UpdateDisplay();
                lastUpdateTime = Time.time;
            }
        }

        public void SetReading(float totalField, float anomaly)
        {
            currentField = totalField;
            currentAnomaly = anomaly;
        }

        void UpdateDisplay()
        {
            if (!mainValueText || !anomalyValueText) return;

            // تنسيق الرقم ليبدو مثل الشاشة الرقمية
            string fieldStr = currentField.ToString("F1");
            string anomalyStr = currentAnomaly.ToString("F1");

            mainValueText.text = fieldStr + " nT";
            anomalyValueText.text = anomalyStr + " nT";

            // تغيير اللون عند وجود شذوذ قوي
            if (Mathf.Abs(currentAnomaly) > 50f)
            {
                mainValueText.color = anomalyColor;
                if(statusText) statusText.text = "ANOMALY DETECTED";
                statusText.color = Color.red;
            }
            else
            {
                mainValueText.color = normalColor;
                if(statusText) statusText.text = "MEASURING";
                statusText.color = Color.white;
            }
        }

        void UpdateTime()
        {
            if (timeText)
            {
                System.TimeSpan t = System.TimeSpan.FromSeconds(Time.timeSinceLevelLoad);
                timeText.text = string.Format("{0:D2}:{1:D2}:{2:D2}", 
                    (int)t.Hours, (int)t.Minutes, (int)t.Seconds);
            }
        }

        /// <summary>
        /// وميض الشاشة لمحاكاة بدء التشغيل
        /// </summary>
        public void FlashDisplay()
        {
            StartCoroutine(FlashCoroutine());
        }

        System.Collections.IEnumerator FlashCoroutine()
        {
            Color original = mainValueText.color;
            mainValueText.color = Color.white;
            yield return new WaitForSeconds(0.1f);
            mainValueText.color = original;
        }
    }
}
