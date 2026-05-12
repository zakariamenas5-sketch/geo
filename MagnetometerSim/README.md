# 🧲 Magnetometer Simulation Platform

## منصة محاكاة المغناطيسومتر للجيوفيزياء التطبيقية

---

## 📋 محتويات المشروع

```
MagnetometerSim/
├── physics_engine/          # المحرك الفيزيائي (Python)
│   ├── magnetometer_physics.py
│   ├── geological_engine.py
│   ├── survey_engine.py
│   └── visualization.py
│
├── unity_app/               # تطبيق Unity 3D
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── Core/       # النواة الرئيسية
│   │   │   ├── Physics/    # الفيزياء المغناطيسية
│   │   │   ├── Survey/     # نظام المسح
│   │   │   ├── Visualization/  # التصور البصري
│   │   │   └── UI/         # واجهة المستخدم
│   │   └── Data/           # ملفات JSON
│   └── README.md
│
├── data/                    # بيانات المسح المُولدة
├── models/                  # النماذج الجيولوجية
├── docs/                    # التوثيق
└── run_all.py              # نقطة الدخول الرئيسية
```

---

## 🎯 الميزات الرئيسية

### 1. أنواع الأجهزة المدعومة
- ✅ **Proton Precession Magnetometer (PPM)**
- ✅ **Cesium Vapor Magnetometer**
- ✅ **Fluxgate Magnetometer**

### 2. النماذج الفيزيائية
- Dipole Model: `B = (μ₀/4π) × [3(m·r̂)r̂ - m] / r³`
- Prism Model: حساب المجال للأجسام المستطيلة
- Regional Field: المجال المغناطيسي الإقليمي
- Noise & Drift: محاكاة واقعية

### 3. البيئات الجيولوجية
- طبقات أفقية (Horizontal Layers)
- فوالق (Faults)
- أجسام معدنية (Ore Bodies)
- أنابيب مدفونة (Buried Pipes)
- أهداف بترولية (Oil & Gas Targets)

### 4. أنماط المسح
- Grid Survey (مسح شبكي)
- Line Survey (مسح خطي)
- Walking Mode
- Drone Mode

### 5. أوضاع الأداء
| الوضع | الدقة | النقاط | الاستخدام |
|-------|-------|--------|-----------|
| Dev Mode | 10×10 | 121 | أجهزة ضعيفة |
| Full Mode | 50×50 | 2601 | دقة عالية |

### 6. اللغات
- 🇬🇧 English
- 🇫🇷 Français
- 🇸🇦 العربية

---

## 🚀 البدء السريع

### المرحلة 1: تشغيل المحرك الفيزيائي (Python)

```bash
cd /workspace/MagnetometerSim
python3 run_all.py
```

**المخرجات:**
- ملفات JSON في مجلد `data/`
- رسوميات في `data/visualizations/`

### المرحلة 2: تشغيل تطبيق Unity

```bash
# افتح Unity Hub
# أضف مشروع unity_app/
# شغّل المشهد MainScene
```

---

## 📊 السيناريوهات المتاحة

### 1. التعدين (Mining)
- استكشاف الخامات الحديدية
- تحديد الفوالق الجيولوجية
- قابلية مغناطيسية: 0.01 - 0.15

### 2. النفط والغاز (Oil & Gas)
- القبب الملحية
- المصائد البترولية
- ارتفاعات القاعدة الصخرية

### 3. الآثار (Archaeology)
- الجدران القديمة
- الفخار المدفون
- القطع المعدنية الأثرية

---

## 🔗 الربط بين Python و Unity

### عبر JSON:
```python
# Python: تصدير البيانات
data = {
    "measurements": [...],
    "model": {...}
}
json.dump(data, open("survey_data.json", "w"))
```

```csharp
// Unity: تحميل البيانات
SurveyData data = DataManager.LoadSurveyData("survey_data.json");
```

---

## 📈 المخرجات

### من Python Engine:
- خرائط كونتورية (Contour Maps)
- مقاطع مغناطيسية (Profiles)
- أسطح ثلاثية الأبعاد (3D Surfaces)
- ملفات JSON

### من Unity App:
- تصور ثلاثي الأبعاد في الزمن الحقيقي
- قراءات لحظية للمجال
- خرائط حرارية تفاعلية
- واجهة مستخدم كاملة

---

## 🏗️ البنية المعمارية

```
┌─────────────────────────────────────────────┐
│           SimulationManager                 │
│         (المدير الرئيسي للمحاكاة)            │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼────┐
│Physics│  │Survey │  │  UI   │
│Engine │  │Engine │  │Manager│
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    │    ┌─────▼─────┐    │
    │    │Geological │    │
    │    │   Model   │    │
    │    └───────────┘    │
    │                     │
┌───▼─────────────────────▼───┐
│      DataManager (JSON)     │
└─────────────────────────────┘
```

---

## 🛠️ التطوير المستقبلي

### ميزات مقترحة:
1. [ ] دعم أجهزة VR/AR
2. [ ] تصدير إلى SEG-Y format
3. [ ] تحليل تلقائي للشذوذ
4. [ ] ذكاء اصطناعي للتفسير
5. [ ] multiplayer collaboration
6. [ ] cloud data sync

### تحسينات الأداء:
1. [ ] GPU acceleration (Compute Shaders)
2. [ ] LOD system للنماذج
3. [ ] Async loading للبيانات
4. [ ] Procedural generation

---

## 📝 الترخيص

هذا المشروع مفتوح المصدر لأغراض تعليمية وبحثية.

---

## 👥 الفريق

- **مهندس البرمجيات**: تطوير المحرك الفيزيائي وتطبيق Unity
- **الخبير الجيوفيزيائي**: التحقق من صحة المعادلات والنماذج
- **مطور الرسوميات**: التصور ثلاثي الأبعاد وواجهات المستخدم

---

## 📞 التواصل

للاستفسارات التقنية أو التعاون:
- راجع ملف `README.md` في كل مجلد فرعي
- تحقق من التوثيق في مجلد `docs/`

---

**الإصدار:** 1.0  
**التاريخ:** 2024  
**الحالة:** جاهز للتطوير والاستخدام
