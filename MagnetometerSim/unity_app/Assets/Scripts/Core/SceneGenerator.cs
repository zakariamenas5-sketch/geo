using UnityEngine;
using System.Collections.Generic;

namespace MagSim.Core
{
    /// <summary>
    /// يقوم بتوليد المشهد ثلاثي الأبعاد برمجياً عند البدء.
    /// مفيد للأجهزة الضعيفة ولضمان عمل المشروع بدون Assets خارجية.
    /// </summary>
    public class SceneGenerator : MonoBehaviour
    {
        [Header("Terrain Settings")]
        public int terrainSize = 100;
        public Color groundColor = new Color(0.2f, 0.6f, 0.2f);
        
        [Header("Device Settings")]
        public GameObject ppmDevicePrefab;
        
        [Header("Visualization")]
        public Material heatmapMaterial;

        private void Start()
        {
            GenerateTerrain();
            GenerateSurveyGrid();
            SpawnMagnetometer();
            SetupLighting();
            Debug.Log("[SceneGenerator] Scene generated successfully.");
        }

        void GenerateTerrain()
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Terrain";
            ground.transform.localScale = new Vector3(terrainSize / 10f, 1, terrainSize / 10f);
            
            Renderer rend = ground.GetComponent<Renderer>();
            rend.material = new Material(Shader.Find("Standard"));
            rend.material.color = groundColor;
            rend.material.SetFloat("_Glossiness", 0.1f);
            rend.material.SetFloat("_Metallic", 0.0f);
            
            // إضافة شبكة بسيطة لتمثيل خطوط المسح
            CreateGridLines(terrainSize, 10);
        }

        void CreateGridLines(int size, int step)
        {
            GameObject gridParent = new GameObject("SurveyGridLines");
            Material lineMat = new Material(Shader.Find("Sprites/Default"));
            lineMat.color = Color.white;

            for (int i = -size / 2; i <= size / 2; i += step)
            {
                // خطوط طولية
                CreateLine(gridParent, new Vector3(i, 0.01f, -size / 2), new Vector3(i, 0.01f, size / 2), lineMat);
                // خطوط عرضية
                CreateLine(gridParent, new Vector3(-size / 2, 0.01f, i), new Vector3(size / 2, 0.01f, i), lineMat);
            }
        }

        void CreateLine(GameObject parent, Vector3 start, Vector3 end, Material mat)
        {
            GameObject lineObj = new GameObject("Line");
            lineObj.transform.parent = parent.transform;
            LineRenderer lr = lineObj.AddComponent<LineRenderer>();
            lr.material = mat;
            lr.startWidth = 0.1f;
            lr.endWidth = 0.1f;
            lr.SetPosition(0, start);
            lr.SetPosition(1, end);
            lr.startColor = Color.gray;
            lr.endColor = Color.gray;
        }

        void SpawnMagnetometer()
        {
            // إنشاء نموذج مبسط للجهاز (PPM) باستخدام أشكال هندسية أساسية
            GameObject deviceRoot = new GameObject("PPM_Sensor");
            deviceRoot.transform.position = new Vector3(0, 1.0f, 0);

            // الجسم الرئيسي
            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            body.transform.parent = deviceRoot.transform;
            body.transform.localScale = new Vector3(0.3f, 0.4f, 0.3f);
            body.transform.localPosition = new Vector3(0, 0.2f, 0);
            body.GetComponent<Renderer>().material.color = Color.yellow;
            Destroy(body.GetComponent<Collider>());

            // الشاشة
            GameObject screen = GameObject.CreatePrimitive(PrimitiveType.Cube);
            screen.transform.parent = deviceRoot.transform;
            screen.transform.localScale = new Vector3(0.15f, 0.1f, 0.05f);
            screen.transform.localPosition = new Vector3(0, 0.45f, 0.15f);
            screen.GetComponent<Renderer>().material.color = Color.black;
            Destroy(screen.GetComponent<Collider>());

            // المققب (Handle)
            GameObject handle = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            handle.transform.parent = deviceRoot.transform;
            handle.transform.localScale = new Vector3(0.05f, 0.6f, 0.05f);
            handle.transform.localPosition = new Vector3(0, -0.3f, 0);
            handle.GetComponent<Renderer>().material.color = Color.gray;
            Destroy(handle.GetComponent<Collider>());

            // إضافة مكون التحكم
            deviceRoot.AddComponent<MagnetometerController>();
            
            // كاميرا تتبع الجهاز
            GameObject camObj = new GameObject("FollowCamera");
            camObj.transform.parent = deviceRoot.transform;
            camObj.transform.localPosition = new Vector3(0, 2.5f, -4f);
            camObj.transform.localEulerAngles = new Vector3(20, 0, 0);
            Camera cam = camObj.AddComponent<Camera>();
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.15f);
            
            Debug.Log("[SceneGenerator] PPM Device spawned with FollowCamera.");
        }

        void SetupLighting()
        {
            GameObject lightObj = new GameObject("Sun");
            Light sun = lightObj.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.2f;
            sun.transform.rotation = Quaternion.Euler(50, -30, 0);
            
            RenderSettings.skybox = null; // Skybox بسيط للأداء
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.1f, 0.1f, 0.15f);
            RenderSettings.fogDensity = 0.02f;
        }

        void GenerateSurveyGrid()
        {
            // نقطة مرجعية للشبكة
            GameObject marker = new GameObject("BaseStation");
            marker.transform.position = new Vector3(-terrainSize/2, 0, -terrainSize/2);
            GameObject.CreatePrimitive(PrimitiveType.Sphere).transform.parent = marker.transform;
            marker.transform.GetChild(0).localScale = Vector3.one * 0.5f;
            marker.transform.GetChild(0).GetComponent<Renderer>().material.color = Color.red;
            Destroy(marker.transform.GetChild(0).GetComponent<Collider>());
        }
    }

    /// <summary>
    /// تحكم بسيط في حركة الجهاز للمحاكاة الأولية
    /// </summary>
    public class MagnetometerController : MonoBehaviour
    {
        public float moveSpeed = 5f;
        public float rotateSpeed = 100f;

        void Update()
        {
            float h = Input.GetAxis("Horizontal");
            float v = Input.GetAxis("Vertical");

            Vector3 move = new Vector3(h, 0, v) * moveSpeed * Time.deltaTime;
            transform.Translate(move, Space.World);

            if (Input.GetKey(KeyCode.Q)) transform.Rotate(0, -rotateSpeed * Time.deltaTime, 0);
            if (Input.GetKey(KeyCode.E)) transform.Rotate(0, rotateSpeed * Time.deltaTime, 0);

            // تحديث موقع المحاكاة الفيزيائية
            SimulationManager.Instance?.UpdateSensorPosition(transform.position);
        }
    }
}
