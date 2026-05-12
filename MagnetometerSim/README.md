# Magnetometer Simulation Platform
# منصة محاكاة مقياس المغناطيسية

## 🎯 Overview / نظرة عامة

Professional desktop application for simulating 3D Magnetometer surveys used in applied geophysics. This platform combines real physics, interactive 3D visualization, and can be developed into a startup product.

تطبيق سطح مكتب احترافي لمحاكاة مسوحات مقياس المغناطيسية ثلاثية الأبعاد المستخدمة في الجيوفيزياء التطبيقية. تجمع هذه المنصة بين الفيزياء الحقيقية والتصور ثلاثي الأبعاد التفاعلي.

---

## 🏗️ Architecture / البنية المعمارية

```
MagnetometerSim/
│
├── physics_engine/          # Python Physics Calculations
│   ├── magnetometer_physics.py    # Core physics engine
│   ├── geological_engine.py       # Geological modeling
│   └── visualization.py           # 2D/3D data visualization
│
├── unity_app/               # Unity 3D Application (Future)
│   ├── Assets/
│   ├── Scripts/
│   └── Scenes/
│
├── data/                    # Data Storage
│   ├── survey_data.json     # Survey measurements
│   ├── *_model.json         # Geological models
│   └── visualizations/      # Generated plots
│
├── models/                  # 3D Models
│   └── (Unity assets)
│
└── docs/                    # Documentation
    └── (Technical docs)
```

---

## 🔬 Physics Engine / المحرك الفيزيائي

### Supported Magnetometer Types:
- **Proton Precession Magnetometer (PPM)** - Primary focus
- **Cesium Vapor Magnetometer** (Future)
- **Fluxgate Magnetometer** (Future)

### Physical Equations:
- **B = -∇V** (Magnetic field from potential)
- **V = (M · r) / (4π r³)** (Dipole potential)

### Geological Bodies Supported:
- Horizontal layers (طبقات أفقية)
- Faults (فوالق)
- Ore bodies (أجسام معدنية)
- Buried pipes (أنابيب مدفونة)
- Oil & Gas targets (أهداف بترولية)

### Survey Modes:
- Grid survey
- Line survey
- Walking mode
- Drone mode

---

## 📊 Features / الميزات

### Phase 1 (Current - Python Backend):
✅ Core physics calculations
✅ Multiple magnetometer types
✅ Geological modeling
✅ Survey simulation
✅ Data export to JSON
✅ 2D visualization (contour maps, profiles)
✅ Predefined scenarios (Mining, Oil & Gas, Archaeology)

### Phase 2 (Next - Unity Integration):
- [ ] Unity 3D scene setup
- [ ] Real-time sensor visualization
- [ ] Interactive geological model editing
- [ ] Live anomaly display

### Phase 3 (Advanced):
- [ ] Multi-language support (AR/FR/EN)
- [ ] Performance modes (Dev/Full)
- [ ] Advanced interpretation tools
- [ ] Export to industry formats

---

## 🚀 Quick Start / البدء السريع

### Prerequisites / المتطلبات:
```bash
pip install numpy matplotlib scipy
```

### Run Physics Engine:
```bash
cd /workspace/MagnetometerSim
python3 physics_engine/magnetometer_physics.py
```

### Run Geological Engine:
```bash
python3 physics_engine/geological_engine.py
```

### Generate Visualizations:
```bash
python3 physics_engine/visualization.py
```

---

## 📁 Generated Files / الملفات المُنشأة

After running the engines, you'll find:

### In `/data/`:
- `survey_data.json` - Survey measurements
- `mining_model.json` - Mining exploration scenario
- `oil_gas_model.json` - Oil & gas exploration scenario
- `archaeology_model.json` - Archaeological survey scenario

### In `/data/visualizations/`:
- `contour_map.png` - Magnetic field contour map
- `anomaly_map.png` - Magnetic anomaly map
- `components.png` - Field component plots
- `profile.png` - Magnetic profile along survey line
- `surface_3d.png` - 3D surface visualization

---

## 🔧 Configuration / الإعدادات

### Performance Modes:
- **DEV Mode**: Coarse grid (10x10), fast computation
- **FULL Mode**: Fine grid (50x50), high accuracy

### Device Parameters:

| Parameter | PPM | Cesium | Fluxgate |
|-----------|-----|--------|----------|
| Sampling Rate | 1 Hz | 10 Hz | 100 Hz |
| Accuracy | 0.1 nT | 0.01 nT | 0.5 nT |
| Noise | 0.5 nT | 0.1 nT | 1.0 nT |

---

## 📈 Scientific Background / الخلفية العلمية

### Magnetic Susceptibility Values:

| Rock Type | Susceptibility (SI) |
|-----------|---------------------|
| Sedimentary | 0.0001 |
| Igneous | 0.01 |
| Metamorphic | 0.005 |
| Iron Ore | 0.05 - 0.5 |
| Steel | 0.3 - 1.0 |

### Typical Anomaly Magnitudes:

| Target Type | Anomaly Size (nT) |
|-------------|-------------------|
| Iron ore body | 100 - 10,000 |
| Buried pipe | 10 - 500 |
| Archaeological wall | 5 - 50 |
| Oil trap | 1 - 10 |

---

## 🎓 Educational Use / الاستخدام التعليمي

This platform is designed for:
- Geophysics students learning magnetic methods
- Professionals testing survey designs
- Researchers developing new interpretation techniques
- Startup development in geophysical technology

---

## 📝 License / الترخيص

Educational and research use. Commercial licensing available for startup development.

---

## 👥 Authors / المؤلفون

Developed with AI assistance for educational and commercial purposes.

---

## 📧 Contact / للتواصل

For questions, suggestions, or collaboration opportunities.

---

## 🔮 Future Enhancements / التحسينات المستقبلية

1. **Unity 3D Integration** - Real-time visualization
2. **Multi-language UI** - Arabic, French, English
3. **Advanced Inversion** - 3D magnetic inversion
4. **Drone Simulation** - UAV survey planning
5. **Machine Learning** - Automatic target detection
6. **Cloud Integration** - Data sharing and collaboration
7. **VR Support** - Immersive geological exploration

---

*Last Updated: May 2024*
*Version: 1.0.0*
