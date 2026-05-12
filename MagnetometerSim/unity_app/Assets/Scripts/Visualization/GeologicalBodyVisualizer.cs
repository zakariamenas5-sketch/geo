using UnityEngine;

namespace MagSim.Visualization
{
    /// <summary>
    /// يولد مكعبات ثلاثية الأبعاد (Voxels) تحت الأرض لتمثيل الأجسام الجيولوجية.
    /// يستخدم لتصور مواقع الخامات والفوالق بشكل مباشر في المشهد.
    /// </summary>
    public class GeologicalBodyVisualizer : MonoBehaviour
    {
        [Header("Visualization Settings")]
        public float voxelSize = 2f;
        public float transparency = 0.6f;
        
        private Material voxelMaterial;

        void Start()
        {
            CreateVoxelMaterial();
            // سيتم استدعاء DrawGeologicalBodies من SimulationManager عند تحميل البيانات
        }

        void CreateVoxelMaterial()
        {
            Shader transparentShader = Shader.Find("Standard");
            voxelMaterial = new Material(transparentShader);
            voxelMaterial.SetFloat("_Mode", 3); // Transparent mode
            voxelMaterial.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            voxelMaterial.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            voxelMaterial.SetInt("_ZWrite", 0);
            voxelMaterial.DisableKeyword("_ALPHATEST_ON");
            voxelMaterial.EnableKeyword("_ALPHABLEND_ON");
            voxelMaterial.DisableKeyword("_ALPHAPREMULTIPLY_ON");
            voxelMaterial.renderQueue = 3000;
        }

        /// <summary>
        /// يرسم الجسم الجيولوجي كمجموعة من المكعبات الشفافة
        /// </summary>
        public void DrawPrismBody(GeologicalPrism prism)
        {
            GameObject bodyGroup = new GameObject($"GeoBody_{prism.id}");
            bodyGroup.transform.parent = this.transform;
            
            Color baseColor = GetColorBySusceptibility(prism.susceptibility);
            Color finalColor = new Color(baseColor.r, baseColor.g, baseColor.b, transparency);
            
            // حساب حدود الجسم
            float minX = prism.centerX - prism.widthX / 2;
            float maxX = prism.centerX + prism.widthX / 2;
            float minZ = prism.centerZ - prism.widthZ / 2;
            float maxZ = prism.centerZ + prism.widthZ / 2;
            float minY = -prism.depthTop;
            float maxY = -prism.depthBottom; // أعمق يعني Y أصغر (سالب أكثر)

            // تبسيط الرسم: مكعب واحد يمثل الجسم كله للأداء
            // في وضع Full Mode يمكن تقسيمه لعدة فوكسلز
            GameObject voxel = GameObject.CreatePrimitive(PrimitiveType.Cube);
            voxel.transform.parent = bodyGroup.transform;
            
            float centerX = (minX + maxX) / 2;
            float centerY = (minY + maxY) / 2;
            float centerZ = (minZ + maxZ) / 2;
            
            voxel.transform.position = new Vector3(centerX, centerY, centerZ);
            voxel.transform.localScale = new Vector3(prism.widthX, Mathf.Abs(maxY - minY), prism.widthZ);
            
            Renderer rend = voxel.GetComponent<Renderer>();
            rend.material = new Material(voxelMaterial);
            rend.material.color = finalColor;
            
            Destroy(voxel.GetComponent<Collider>()); // إزالة التصادم للأداء
            
            Debug.Log($"[GeoVisualizer] Drew body {prism.id} at depth {prism.depthTop}m - {prism.depthBottom}m");
        }

        Color GetColorBySusceptibility(float k)
        {
            // ألوان تقريبية للقابلية المغناطيسية
            if (k < 0.001f) return Color.gray;      // رواسب عادية
            if (k < 0.01f) return Color.yellow;     // خامات ضعيفة
            if (k < 0.05f) return Color.red;        // خامات حديدية قوية
            return Color.magenta;                   // مغناطيسية جداً
        }

        /// <summary>
        /// يرسم خطاً لتمثيل الفالق
        /// </summary>
        public void DrawFault(FaultModel fault)
        {
            GameObject faultObj = new GameObject($"Fault_{fault.id}");
            faultObj.transform.parent = this.transform;
            
            LineRenderer lr = faultObj.AddComponent<LineRenderer>();
            lr.material = new Material(Shader.Find("Sprites/Default"));
            lr.startWidth = 0.5f;
            lr.endWidth = 0.5f;
            lr.positionCount = 2;
            
            lr.startColor = Color.blue;
            lr.endColor = Color.blue;
            
            // رسم خط الفالق على السطح
            lr.SetPosition(0, new Vector3(fault.startX, 0.05f, fault.startZ));
            lr.SetPosition(1, new Vector3(fault.endX, 0.05f, fault.endZ));
            
            // إضافة مستوى مائل للفالق (اختياري)
            if (fault.dipAngle > 0)
            {
                // يمكن إضافة Plane مائل هنا في النسخ المتقدمة
            }
            
            Debug.Log($"[GeoVisualizer] Drew Fault {fault.id} with dip {fault.dipAngle}°");
        }
    }

    // هياكل بيانات مساعدة لاستقبال البيانات من JSON
    [System.Serializable]
    public class GeologicalPrism
    {
        public string id;
        public float centerX, centerZ;
        public float widthX, widthZ;
        public float depthTop, depthBottom;
        public float susceptibility;
        public string type; // ore, pipe, salt_dome, etc.
    }

    [System.Serializable]
    public class FaultModel
    {
        public string id;
        public float startX, startZ;
        public float endX, endZ;
        public float dipAngle;
        public float throwDistance;
    }
}
