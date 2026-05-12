using UnityEngine;
using MagnetometerSim.Physics;

namespace MagnetometerSim.Visualization
{
    /// <summary>
    /// تصور البيانات المغناطيسية كخريطة حرارية
    /// </summary>
    public class MagneticHeatmap : MonoBehaviour
    {
        [Header("إعدادات الخريطة")]
        public int resolution = 50;
        public float size = 100f;
        public float heightOffset = 0.1f;
        
        [Header("الألوان")]
        public Gradient colorGradient;
        public float minValue = -100f;
        public float maxValue = 100f;
        
        private Texture2D heatmapTexture;
        private MeshRenderer meshRenderer;
        
        public void Initialize(int res, float sz)
        {
            resolution = res;
            size = sz;
            CreateHeatmapTexture();
        }
        
        private void Start()
        {
            SetupMaterial();
        }
        
        /// <summary>
        /// إنشاء نسيج الخريطة الحرارية
        /// </summary>
        public void CreateHeatmapTexture()
        {
            if (heatmapTexture != null) Destroy(heatmapTexture);
            
            heatmapTexture = new Texture2D(resolution, resolution);
            heatmapTexture.filterMode = FilterMode.Bilinear;
            
            // تهيئة بألوان افتراضية
            UpdateHeatmapColors(new float[resolution, resolution]);
        }
        
        /// <summary>
        /// تحديث ألوان الخريطة بناءً على البيانات
        /// </summary>
        public void UpdateHeatmapColors(float[,] values)
        {
            if (heatmapTexture == null) return;
            
            for (int y = 0; y < resolution; y++)
            {
                for (int x = 0; x < resolution; x++)
                {
                    float value = values[x, y];
                    float normalized = Mathf.InverseLerp(minValue, maxValue, value);
                    Color color = colorGradient.Evaluate(normalized);
                    heatmapTexture.SetPixel(x, y, color);
                }
            }
            
            heatmapTexture.Apply();
        }
        
        /// <summary>
        /// إعداد المادة الخام للعرض
        /// </summary>
        private void SetupMaterial()
        {
            meshRenderer = GetComponent<MeshRenderer>();
            if (meshRenderer == null)
            {
                gameObject.AddComponent<MeshFilter>();
                meshRenderer = gameObject.AddComponent<MeshRenderer>();
                
                // إنشاء مستوى بسيط
                MeshFilter filter = GetComponent<MeshFilter>();
                filter.mesh = CreatePlaneMesh();
            }
            
            Material mat = new Material(Shader.Find("Unlit/Texture"));
            mat.mainTexture = heatmapTexture;
            meshRenderer.material = mat;
        }
        
        /// <summary>
        /// إنشاء شبكة مستوية
        /// </summary>
        private Mesh CreatePlaneMesh()
        {
            Mesh mesh = new Mesh();
            
            Vector3[] vertices = new Vector3[4];
            float halfSize = size / 2f;
            
            vertices[0] = new Vector3(-halfSize, 0, -halfSize);
            vertices[1] = new Vector3(halfSize, 0, -halfSize);
            vertices[2] = new Vector3(halfSize, 0, halfSize);
            vertices[3] = new Vector3(-halfSize, 0, halfSize);
            
            mesh.vertices = vertices;
            
            int[] triangles = new int[6];
            triangles[0] = 0;
            triangles[1] = 2;
            triangles[2] = 1;
            triangles[3] = 0;
            triangles[4] = 3;
            triangles[5] = 2;
            
            mesh.triangles = triangles;
            
            Vector2[] uv = new Vector2[4];
            uv[0] = new Vector2(0, 0);
            uv[1] = new Vector2(1, 0);
            uv[2] = new Vector2(1, 1);
            uv[3] = new Vector2(0, 1);
            
            mesh.uv = uv;
            mesh.RecalculateNormals();
            
            return mesh;
        }
        
        /// <summary>
        /// تحويل قيمة مغناطيسية إلى لون
        /// </summary>
        public Color ValueToColor(float value)
        {
            float normalized = Mathf.InverseLerp(minValue, maxValue, value);
            return colorGradient.Evaluate(normalized);
        }
    }
}
