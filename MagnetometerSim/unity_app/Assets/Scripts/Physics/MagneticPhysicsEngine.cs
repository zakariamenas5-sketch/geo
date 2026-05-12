using UnityEngine;
using MagnetometerSim.Physics;

namespace MagnetometerSim.Physics
{
    /// <summary>
    /// محرك الفيزياء المغناطيسية - تطبيق المعادلات الأساسية
    /// B = -∇V
    /// V = (M · r) / (4π r³)
    /// </summary>
    public class MagneticPhysicsEngine : MonoBehaviour
    {
        [Header("إعدادات الفيزياء")]
        public double mu0 = 4 * Math.PI * 1e-7; // نفاذية الفراغ
        
        private SimulationSettings settings;
        
        public void Initialize(SimulationSettings simSettings)
        {
            settings = simSettings;
        }
        
        /// <summary>
        /// حساب المجال المغناطيسي لجسم مغناطيسي (Dipole Model)
        /// </summary>
        public Vector3 CalculateDipoleField(Vector3 position, Vector3 dipoleMoment, Vector3 dipolePosition)
        {
            Vector3 r = position - dipolePosition;
            double rMagnitude = r.magnitude;
            
            if (rMagnitude < 0.1) return Vector3.zero; // تجنب القسمة على صفر
            
            double r3 = Math.Pow(rMagnitude, 3);
            double r5 = Math.Pow(rMagnitude, 5);
            
            // B = (μ₀/4π) * [3(m·r̂)r̂ - m] / r³
            double factor = mu0 / (4 * Math.PI * r3);
            
            Vector3 rHat = r.normalized;
            double mDotR = Vector3.Dot(dipoleMoment, rHat);
            
            Vector3 B = new Vector3(
                (float)(factor * (3 * mDotR * rHat.x - dipoleMoment.x)),
                (float)(factor * (3 * mDotR * rHat.y - dipoleMoment.y)),
                (float)(factor * (3 * mDotR * rHat.z - dipoleMoment.z))
            );
            
            return B * 1e9f; // تحويل إلى nT
        }
        
        /// <summary>
        /// حساب المجال من جسم مستطيل مدفون (Prism Model)
        /// </summary>
        public Vector3 CalculatePrismField(Vector3 position, GeologicalBody prism)
        {
            // تبسيط: معاملة المنشور كمجموعة من الثنائيات القطبية
            Vector3 totalField = Vector3.zero;
            
            // تقسيم المنشور إلى نقاط متعددة
            int divisions = 3;
            double dx = prism.sizeX / divisions;
            double dy = prism.sizeY / divisions;
            double dz = prism.sizeZ / divisions;
            
            for (int i = 0; i <= divisions; i++)
            {
                for (int j = 0; j <= divisions; j++)
                {
                    for (int k = 0; k <= divisions; k++)
                    {
                        Vector3 subPos = new Vector3(
                            (float)(prism.centerX + (i - divisions/2.0) * dx),
                            (float)(prism.centerY + (j - divisions/2.0) * dy),
                            (float)(prism.centerZ + (k - divisions/2.0) * dz)
                        );
                        
                        // عزم مغناطيسي متناسب مع القابلية
                        Vector3 moment = new Vector3(0, (float)prism.susceptibility * 1000, 0);
                        totalField += CalculateDipoleField(position, moment, subPos);
                    }
                }
            }
            
            return totalField / (divisions + 1);
        }
        
        /// <summary>
        /// حساب المجال الإقليمي
        /// </summary>
        public Vector3 CalculateRegionalField()
        {
            if (settings == null) return new Vector3(0, 45000, 0);
            
            Vector3 direction = settings.regionalFieldDirection.normalized;
            return direction * settings.regionalFieldStrength;
        }
        
        /// <summary>
        /// إضافة ضوضاء محاكاة
        /// </summary>
        public float AddNoise(float value, float noiseLevel)
        {
            if (noiseLevel <= 0) return value;
            float noise = UnityEngine.Random.Range(-noiseLevel, noiseLevel);
            return value + noise;
        }
        
        /// <summary>
        /// إضافة انحراف زمني
        /// </summary>
        public float AddDrift(float value, float driftRate, double elapsedTime)
        {
            return value + (float)(driftRate * elapsedTime);
        }
        
        /// <summary>
        /// حساب المجال المغناطيسي الكلي في نقطة
        /// </summary>
        public MagneticMeasurement CalculateTotalField(Vector3 position, GeologicalBody[] bodies, 
                                                       double timestamp, bool addNoise = true, bool addDrift = true)
        {
            Vector3 regional = CalculateRegionalField();
            Vector3 anomalyField = Vector3.zero;
            
            // جمع مساهمات جميع الأجسام
            if (bodies != null)
            {
                foreach (var body in bodies)
                {
                    if (body.type == "prism" || body.type == "ore")
                    {
                        anomalyField += CalculatePrismField(position, body);
                    }
                    else if (body.type == "dipole")
                    {
                        Vector3 moment = new Vector3(0, (float)body.susceptibility * 1000, 0);
                        Vector3 bodyPos = new Vector3((float)body.centerX, (float)body.centerY, (float)body.centerZ);
                        anomalyField += CalculateDipoleField(position, moment, bodyPos);
                    }
                }
            }
            
            Vector3 totalB = regional + anomalyField;
            
            // إضافة ضوضاء وانحراف
            float bx = totalB.x;
            float by = totalB.y;
            float bz = totalB.z;
            
            if (addNoise && settings != null && settings.enableNoise)
            {
                bx = AddNoise(bx, settings.noiseLevel);
                by = AddNoise(by, settings.noiseLevel);
                bz = AddNoise(bz, settings.noiseLevel);
            }
            
            if (addDrift && settings != null && settings.enableDrift)
            {
                bx = AddDrift(bx, settings.driftRate, timestamp);
                by = AddDrift(by, settings.driftRate, timestamp);
                bz = AddDrift(bz, settings.driftRate, timestamp);
            }
            
            double totalMagnitude = Math.Sqrt(bx * bx + by * by + bz * bz);
            double regionalMagnitude = regional.magnitude;
            double anomaly = totalMagnitude - regionalMagnitude;
            
            return new MagneticMeasurement(
                position.x, position.y, position.z,
                totalMagnitude, bx, by, bz, anomaly, timestamp
            );
        }
    }
}
