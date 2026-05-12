# 📘 دليل التطوير التقني - MagnetometerSim

## Technical Development Guide

---

## 📚 فهرس المحتويات

1. [بنية النظام](#1-بنية-النظام)
2. [المعادلات الفيزيائية](#2-المعادلات-الفيزيائية)
3. [دليل الـ API](#3-دليل-ال-api)
4. [أمثلة برمجية](#4-أمثلة-برمجية)
5. [استكشاف الأخطاء](#5-استكشاف-الأخطاء)

---

## 1. بنية النظام

### 1.1 المكونات الرئيسية

```
┌─────────────────────────────────────────────────┐
│              MagnetometerSim                    │
├─────────────────────────────────────────────────┤
│  Python Engine          │    Unity App          │
│  ─────────────          │    ───────────        │
│  • Physics Core         │    • 3D Visualization │
│  • Geological Models    │    • Real-time Updates│
│  • Data Generation      │    • User Interface   │
│  • Plotting             │    • Interaction      │
└─────────────────────────┴───────────────────────┘
              │                        │
              └────────┬───────────────┘
                       │
                 JSON Files
```

### 1.2 تدفق البيانات

```
User Input → SimulationManager → PhysicsEngine → Measurements
                                      ↓
                              GeologicalModel
                                      ↓
                              SurveyEngine
                                      ↓
                              DataManager (JSON)
                                      ↓
                              Visualization
```

---

## 2. المعادلات الفيزيائية

### 2.1 المجال المغناطيسي للثنائي القطب (Dipole)

**المعادلة الأساسية:**
```
B(r) = (μ₀/4π) × [3(m·r̂)r̂ - m] / r³
```

**حيث:**
- `B`: متجه المجال المغناطيسي (Tesla)
- `μ₀`: نفاذية الفراغ = 4π × 10⁻⁷ H/m
- `m`: العزم المغناطيسي (A·m²)
- `r`: متجه الموقع من المصدر إلى نقطة القياس
- `r̂`: متجه الوحدة في اتجاه r
- `r³`: مكعب المسافة

**التنفيذ في الكود:**
```python
def calculate_dipole_field(self, position, moment, source_pos):
    r = position - source_pos
    r_mag = np.linalg.norm(r)
    r_hat = r / r_mag
    
    factor = self.mu0 / (4 * np.pi * r_mag**3)
    m_dot_r = np.dot(moment, r_hat)
    
    B = factor * (3 * m_dot_r * r_hat - moment)
    return B * 1e9  # تحويل إلى nT
```

### 2.2 جهد الثنائي القطب

**المعادلة:**
```
V = (m · r) / (4π r³)
```

**العلاقة مع المجال:**
```
B = -∇V
```

### 2.3 نموذج المنشور (Prism Model)

**المبدأ:** تقسيم المنشور إلى عناصر صغيرة ومعاملة كل عنصر كثنائي قطب

```python
def calculate_prism_field(self, position, prism):
    total_field = np.zeros(3)
    divisions = 5
    
    dx = prism.size_x / divisions
    dy = prism.size_y / divisions
    dz = prism.size_z / divisions
    
    for i in range(divisions):
        for j in range(divisions):
            for k in range(divisions):
                sub_pos = prism.center + np.array([
                    (i - divisions/2) * dx,
                    (j - divisions/2) * dy,
                    (k - divisions/2) * dz
                ])
                
                moment = np.array([0, prism.susceptibility * 1000, 0])
                total_field += self.calculate_dipole_field(position, moment, sub_pos)
    
    return total_field / divisions
```

### 2.4 المجال الإقليمي (Regional Field)

```
B_regional = IGRF(latitude, longitude, altitude)
```

**تبسيط:**
```python
def get_regional_field(self, lat, lon, alt):
    # قيمة تقريبية للمجال الإقليمي
    strength = 45000  # nT
    inclination = 60  # degrees
    declination = 5   # degrees
    
    return self._convert_to_components(strength, inclination, declination)
```

### 2.5 الضوضاء والانحراف

**الضوضاء العشوائية:**
```
B_measured = B_true + N(0, σ²)
```

**الانحراف الزمني:**
```
B_drift = B_0 + rate × t
```

**التنفيذ:**
```python
def add_noise_and_drift(self, value, timestamp):
    noise = np.random.normal(0, self.noise_level)
    drift = self.drift_rate * timestamp
    return value + noise + drift
```

---

## 3. دليل الـ API

### 3.1 Python Engine

#### MagnetometerPhysics

```python
class MagnetometerPhysics:
    def __init__(self, settings: dict)
    
    def calculate_total_field(self, position: np.ndarray) -> MagneticMeasurement
    def calculate_dipole_field(self, pos, moment, source) -> np.ndarray
    def calculate_prism_field(self, pos, prism) -> np.ndarray
    def add_noise(self, value: float) -> float
    def add_drift(self, value: float, time: float) -> float
```

#### GeologicalEngine

```python
class GeologicalEngine:
    def __init__(self)
    
    def create_prism(id, center, size, susceptibility) -> GeologicalBody
    def create_fault(id, center, size, angle) -> GeologicalBody
    def create_pipe(id, center, radius, length) -> GeologicalBody
    def load_scenario(scenario_name: str) -> GeologicalModel
```

#### SurveyEngine

```python
class SurveyEngine:
    def __init__(self, physics: MagnetometerPhysics)
    
    def generate_grid(area_size, resolution) -> List[Position]
    def generate_line(start, end, spacing) -> List[Position]
    def execute_survey(path, model) -> List[MagneticMeasurement]
    def export_json(data, filename) -> None
```

### 3.2 Unity App

#### SimulationManager

```csharp
public class SimulationManager : MonoBehaviour
{
    // الخصائص العامة
    public SimulationSettings settings;
    public MagneticPhysicsEngine physicsEngine;
    public SurveyEngine surveyEngine;
    
    // الدوال الرئيسية
    public void LoadScenario(string scenarioFile);
    public void StartSurvey();
    public void StopSurvey();
    public void ChangeBodyDepth(string bodyId, double depth);
    public void ChangeSusceptibility(string bodyId, double sus);
    public void TogglePerformanceMode(PerformanceMode mode);
}
```

#### MagneticPhysicsEngine

```csharp
public class MagneticPhysicsEngine : MonoBehaviour
{
    public Vector3 CalculateDipoleField(Vector3 pos, Vector3 moment, Vector3 source);
    public Vector3 CalculatePrismField(Vector3 pos, GeologicalBody prism);
    public MagneticMeasurement CalculateTotalField(Vector3 pos, GeologicalBody[] bodies, double time);
    public float AddNoise(float value, float level);
    public float AddDrift(float value, float rate, double time);
}
```

#### DataManager

```csharp
public class DataManager : MonoBehaviour
{
    public static DataManager Instance { get; }
    
    public GeologicalModel LoadGeologicalModel(string fileName);
    public SurveyData LoadSurveyData(string fileName);
    public void SaveSurveyData(SurveyData data, string fileName);
    public SimulationSettings LoadSettings(string fileName);
}
```

---

## 4. أمثلة برمجية

### 4.1 Python: إنشاء مسح كامل

```python
from physics_engine.magnetometer_physics import MagnetometerPhysics
from physics_engine.geological_engine import GeologicalEngine
from physics_engine.survey_engine import SurveyEngine

# تهيئة المحركات
physics = MagnetometerPhysics({
    'noise_level': 5.0,
    'drift_rate': 0.1,
    'regional_field': 45000
})

geology = GeologicalEngine()
survey = SurveyEngine(physics)

# تحميل سيناريو التعدين
model = geology.load_scenario('mining')

# توليد مسار شبكي
path = survey.generate_grid(area_size=100, resolution=20)

# تنفيذ المسح
measurements = survey.execute_survey(path, model)

# تصدير النتائج
survey.export_json({
    'measurements': measurements,
    'model': model.to_dict()
}, 'survey_results.json')

print(f"تم جمع {len(measurements)} قراءة")
```

### 4.2 Unity: تشغيل المحاكاة

```csharp
using MagnetometerSim.Core;
using MagnetometerSim.Physics;

public class ExampleUsage : MonoBehaviour
{
    void Start()
    {
        // الحصول على المدير
        var simManager = SimulationManager.Instance;
        
        // تحميل سيناريو
        simManager.LoadScenario("mining_model.json");
        
        // بدء المسح
        simManager.StartSurvey();
    }
    
    void Update()
    {
        // تغيير عمق الجسم عند الضغط على مفتاح
        if (Input.GetKeyDown(KeyCode.D))
        {
            SimulationManager.Instance.ChangeBodyDepth("ore_body_1", 25.0);
        }
        
        // تبديل وضع الأداء
        if (Input.GetKeyDown(KeyCode.M))
        {
            var current = SimulationManager.Instance.settings.mode;
            var newMode = current == SimulationSettings.PerformanceMode.Dev 
                ? SimulationSettings.PerformanceMode.Full 
                : SimulationSettings.PerformanceMode.Dev;
            
            SimulationManager.Instance.TogglePerformanceMode(newMode);
        }
    }
}
```

### 4.3 Unity: قراءة البيانات

```csharp
void OnMeasurementTaken(MagneticMeasurement measurement)
{
    Debug.Log($"المجال الكلي: {measurement.totalField:F1} nT");
    Debug.Log($"الشذوذ: {measurement.anomaly:F2} nT");
    Debug.Log($"الموقع: ({measurement.x}, {measurement.y}, {measurement.z})");
    
    // تحديث واجهة المستخدم
    totalFieldText.text = $"{measurement.totalField:F1}";
    anomalyText.text = $"{measurement.anomaly:+0.0;-0.0;0.0}";
}
```

---

## 5. استكشاف الأخطاء

### 5.1 مشاكل شائعة وحلولها

| المشكلة | السبب المحتمل | الحل |
|---------|---------------|------|
| قراءات خاطئة | وحدات قياس غير متوافقة | تحقق من التحويل إلى nT |
| بطء الأداء | دقة عالية جدًا | استخدم Dev Mode |
| ملف JSON لا يُحمّل | تنسيق غير صحيح | تحقق من صحة JSON |
| انحراف كبير في القيم | drift_rate عالي | خفّض drift_rate في الإعدادات |
| ضوضاء مفرطة | noise_level عالي | اضبط noiseLevel < 10 |

### 5.2 أدوات التشخيص

**Python:**
```python
# تفعيل سجل التفاصيل
import logging
logging.basicConfig(level=logging.DEBUG)

# فحص النموذج الجيولوجي
print(model.summary())

# التحقق من المسار
survey.validate_path(path)
```

**Unity:**
```csharp
// تفعيل Debug
SimulationManager.Instance.debugMode = true;

// عرض معلومات الأداء
Debug.Log($"FPS: {1f/Time.deltaTime:F1}");
Debug.Log($"Points: {settings.CurrentGridResolution}x{settings.CurrentGridResolution}");
```

### 5.3 التحقق من صحة الفيزياء

```python
# اختبار بسيط للثنائي القطب
physics = MagnetometerPhysics()
moment = np.array([0, 1000, 0])
source = np.array([0, 0, 10])
pos = np.array([0, 0, 0])

B = physics.calculate_dipole_field(pos, moment, source)
print(f"B = {B} nT")

# القيمة المتوقعة: مجال يشير للأسفل (سلبي Y)
assert B[1] < 0, "الاتجاه خاطئ!"
```

---

## 📎 الملاحق

### أ. ثوابت فيزيائية

```python
MU_0 = 4 * np.pi * 1e-7      # H/m
PI = np.pi                   # 3.14159...
EARTH_RADIUS = 6371000       # m
```

### ب. وحدات القياس

| الكمية | الوحدة | التحويل |
|--------|--------|---------|
| المجال المغناطيسي | Tesla (T) | 1 T = 10⁹ nT |
| العزم المغناطيسي | A·m² | - |
| القابلية المغناطيسية | SI (لا وحدة) | - |
| المسافة | متر (m) | - |

### ج. مراجع علمية

1. Blakely, R.J. (1995). *Potential Theory in Gravity and Magnetic Applications*
2. Telford, W.M. et al. (1990). *Applied Geophysics*
3. Hinze, W.J. et al. (2013). *Gravity and Magnetic Exploration*

---

**آخر تحديث:** 2024  
**الإصدار:** 1.0
