# Magnetometer Simulation Platform - Unity Application

## 🎯 نظرة عامة

تطبيق Unity لمحاكاة جهاز Magnetometer ثلاثي الأبعاد مع دعم:
- **Proton Precession Magnetometer (PPM)**
- **Cesium Vapor Magnetometer**
- **Fluxgate Magnetometer**

---

## 📂 هيكلة المشروع

```
unity_app/
├── Assets/
│   ├── Scripts/
│   │   ├── Core/
│   │   │   ├── SimulationSettings.cs      # إعدادات المحاكاة
│   │   │   ├── SimulationManager.cs       # المدير الرئيسي
│   │   │   └── DataManager.cs             # إدارة البيانات JSON
│   │   ├── Physics/
│   │   │   ├── MagneticData.cs            # هياكل البيانات
│   │   │   └── MagneticPhysicsEngine.cs   # محرك الفيزياء
│   │   ├── Survey/
│   │   │   └── SurveyEngine.cs            # محرك المسح
│   │   ├── Visualization/
│   │   │   └── MagneticHeatmap.cs         # الخريطة الحرارية
│   │   └── UI/
│   │       ├── LocalizationManager.cs     # تعدد اللغات
│   │       └── SimulationUI.cs            # واجهة المستخدم
│   ├── Data/
│   │   ├── settings.json                  # إعدادات التطبيق
│   │   ├── mining_model.json              # سيناريو التعدين
│   │   ├── oil_gas_model.json             # سيناريو النفط
│   │   └── archaeology_model.json         # سيناريو الآثار
│   ├── Scenes/
│   ├── Materials/
│   └── Models/
└── ProjectSettings/
```

---

## 🔧 متطلبات التشغيل

### الحد الأدنى:
- Unity 2020.3 LTS أو أحدث
- .NET Framework 4.x
- Newtonsoft.Json (via Package Manager)

### الموصى به:
- Unity 2021.3 LTS
- 8GB RAM
- GPU يدعم DirectX 11

---

## 🚀 خطوات التثبيت

### 1. فتح المشروع في Unity
```bash
# افتح Unity Hub
# انقر على "Add" → اختر مجلد unity_app
```

### 2. تثبيت الحزم المطلوبة
1. افتح **Window → Package Manager**
2. ثبت الحزم التالية:
   - **Newtonsoft.Json** (لـ JSON serialization)
   - **TextMeshPro** (للنصوص)

### 3. إعداد المشهد
1. أنشئ مشهدًا جديدًا: `MainScene`
2. أضف الكائنات التالية:

```
Hierarchy:
├── GameManager (Empty)
│   └── SimulationManager (script)
├── DataManager (Empty)
├── LocalizationManager (Empty)
├── MagnetometerSensor (Sphere/Capsule)
├── Terrain (Plane)
├── HeatmapVisualizer (Quad)
└── Canvas (UI)
    ├── ReadingDisplay (Text)
    ├── AnomalyDisplay (Text)
    ├── ProgressBar (Slider)
    ├── StartButton (Button)
    ├── StopButton (Button)
    └── ScenarioDropdown (Dropdown)
```

---

## 🎮 استخدام التطبيق

### 1. تحميل سيناريو
```csharp
// من SimulationManager
simManager.LoadScenario("mining_model.json");
```

### 2. بدء المسح
```csharp
simManager.StartSurvey();
```

### 3. تغيير وضع الأداء
```csharp
// Dev Mode: شبكة 10x10 (خفيف)
// Full Mode: شبكة 50x50 (دقة عالية)
simManager.TogglePerformanceMode(SimulationSettings.PerformanceMode.Full);
```

### 4. تعديل الأجسام الجيولوجية
```csharp
// تغيير العمق
simManager.ChangeBodyDepth("ore_body_1", 25.0);

// تغيير القابلية المغناطيسية
simManager.ChangeSusceptibility("ore_body_1", 0.08);
```

---

## 🌐 دعم اللغات

يدعم التطبيق 3 لغات:
- **English** (افتراضي)
- **Français**
- **العربية**

```csharp
// تغيير اللغة
LocalizationManager.Instance.SetLanguage(LocalizationManager.Language.Arabic);
```

---

## 📊 المعادلات الفيزيائية المُطبقة

### Dipole Model:
```
B = (μ₀/4π) × [3(m·r̂)r̂ - m] / r³
```

### Prism Model:
```
تقسيم المنشور إلى نقاط متعددة وحساب المجال كمجموع ثنائيات قطبية
```

### Regional Field:
```
B_regional = direction × strength
```

### Noise & Drift:
```
B_measured = B_true + noise(t) + drift_rate × time
```

---

## 🎨 السيناريوهات المتاحة

### 1. Mining Exploration
- أجسام خام حديدية (Ore bodies)
- فوالق جيولوجية (Faults)
- قابلية مغناطيسية عالية

### 2. Oil & Gas
- قبب ملحية (Salt domes)
- مصائد بترولية (Anticline traps)
- ارتفاعات القاعدة الصخرية (Basement highs)

### 3. Archaeology
- جدران قديمة (Ancient walls)
- فخار مدفون (Buried pottery)
- قطع معدنية أثرية (Metal artifacts)

---

## 🔍 ميزات متقدمة

### نظام الهجين (Hybrid System):
- **Precomputed**: حساب مسبق للمسح الكامل
- **Real-time**: تحديث لحظي أثناء الحركة

### وضعي الأداء:
| الميزة | Dev Mode | Full Mode |
|--------|----------|-----------|
| دقة الشبكة | 10×10 | 50×50 |
| عدد النقاط | 121 | 2601 |
| الاستهلاك | منخفض | عالي |
| الاستخدام | تطوير | عرض نهائي |

---

## 📝 ملاحظات التطوير

### إضافة جهاز جديد:
1. أضف نوعًا جديدًا في `SimulationSettings.MagnetometerType`
2. طبق خصائص الجهاز في `MagneticPhysicsEngine`
3. أضف نموذج 3D في مجلد `Models/`

### إضافة نموذج جيولوجي:
1. أنشئ ملف JSON جديد في `Assets/Data/`
2. اتبع هيكل `GeologicalBody`
3. حمّل عبر `LoadScenario()`

---

## 🐛 استكشاف الأخطاء

### المشكلة: لا تظهر البيانات
**الحل:** تحقق من وجود ملفات JSON في `Assets/Data/`

### المشكلة: بطء الأداء
**الحل:** استخدم Dev Mode بدلاً من Full Mode

### المشكلة: خطأ في Newtonsoft.Json
**الحل:** ثبت الحزمة عبر Package Manager

---

## 📞 الدعم

للاستفسارات التقنية:
- راجع ملف `README.md` الرئيسي
- تحقق من توثيق كل Script

---

**الإصدار:** 1.0  
**التاريخ:** 2024  
**المطور:** MagnetometerSim Team
