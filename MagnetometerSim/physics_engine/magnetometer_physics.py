"""
Magnetometer Physics Engine - Core Module
==========================================
محرك فيزيائي لمحاكاة مقياس المغناطيسية (Magnetometer)

يدعم:
- Proton Precession Magnetometer (PPM)
- Cesium Magnetometer  
- Fluxgate Magnetometer

المعادلات الأساسية:
- B = -∇V
- V = (M · r) / (4π r³)

Author: AI Assistant
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json


class MagnetometerType(Enum):
    """أنواع أجهزة المغناطيسية المدعومة"""
    PPM = "proton_precession"
    CESIUM = "cesium_vapor"
    FLUXGATE = "fluxgate"


class SurveyMode(Enum):
    """أنماط المسح المتاحة"""
    GRID = "grid"
    LINE = "line"
    WALKING = "walking"
    DRONE = "drone"


class PerformanceMode(Enum):
    """أوضاع الأداء"""
    DEV = "dev"
    FULL = "full"


@dataclass
class GeologicalBody:
    """تمثيل جسم جيولوجي مغناطيسي"""
    id: str
    body_type: str  # 'prism', 'dipole', 'layer', 'fault', 'pipe'
    position: Tuple[float, float, float]  # x, y, z (center)
    dimensions: Tuple[float, float, float]  # dx, dy, dz
    susceptibility: float  # χ (chi)
    magnetization: Optional[np.ndarray] = None  # M vector
    rotation: Tuple[float, float, float] = (0, 0, 0)  # Euler angles
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'body_type': self.body_type,
            'position': self.position,
            'dimensions': self.dimensions,
            'susceptibility': self.susceptibility,
            'magnetization': self.magnetization.tolist() if self.magnetization is not None else None,
            'rotation': self.rotation
        }


@dataclass
class SensorReading:
    """قراءة من جهاز المغناطيسية"""
    timestamp: float
    position: Tuple[float, float, float]
    total_field: float  # Total magnetic field intensity (nT)
    bx: float  # X component (nT)
    by: float  # Y component (nT)
    bz: float  # Z component (nT)
    noise: float  # Added noise (nT)
    drift: float  # Instrument drift (nT)


class MagneticFieldCalculator:
    """
    حاسبة المجال المغناطيسي الرئيسية
    
    تحسب المجال المغناطيسي الناتج عن أجسام مختلفة
    باستخدام نماذج فيزيائية دقيقة
    """
    
    # ثوابت فيزيائية
    MU_0 = 4 * np.pi * 1e-7  # Permeability of free space (H/m)
    EARTH_FIELD_NORTH = 50000  # nT (typical mid-latitude value)
    
    def __init__(self, regional_field: float = 50000):
        """
        Initialize the magnetic field calculator
        
        Args:
            regional_field: Regional magnetic field intensity in nT
        """
        self.regional_field = regional_field
        self.bodies: List[GeologicalBody] = []
        
    def add_body(self, body: GeologicalBody):
        """إضافة جسم جيولوجي للنموذج"""
        self.bodies.append(body)
        
    def remove_body(self, body_id: str):
        """إزالة جسم جيولوجي من النموذج"""
        self.bodies = [b for b in self.bodies if b.id != body_id]
        
    def clear_bodies(self):
        """مسح جميع الأجسام"""
        self.bodies.clear()
    
    def dipole_field(self, observation_point: np.ndarray, 
                     dipole_position: np.ndarray,
                     dipole_moment: np.ndarray) -> np.ndarray:
        """
        حساب المجال المغناطيسي لثنائي قطب (Dipole)
        
        المعادلة:
        B = (μ₀/4π) * [3(m·r̂)r̂ - m] / r³
        
        Args:
            observation_point: نقطة القياس [x, y, z]
            dipole_position: موقع الثنائي القطب [x, y, z]
            dipole_moment: عزم الثنائي القطب [mx, my, mz]
            
        Returns:
            Vector magnetic field [Bx, By, Bz] in Tesla
        """
        r_vec = observation_point - dipole_position
        r = np.linalg.norm(r_vec)
        
        if r < 0.1:  # تجنب القسمة على صفر
            return np.zeros(3)
            
        r_hat = r_vec / r
        m_dot_r = np.dot(dipole_moment, r_hat)
        
        # Dipole field equation
        B = (self.MU_0 / (4 * np.pi)) * (3 * m_dot_r * r_hat - dipole_moment) / (r ** 3)
        
        return B
    
    def prism_field(self, observation_point: np.ndarray,
                    prism_center: np.ndarray,
                    prism_dims: np.ndarray,
                    susceptibility: float,
                    inducing_field: np.ndarray) -> np.ndarray:
        """
        حساب المجال المغناطيسي لمنشور مستطيل (Rectangular Prism)
        
        باستخدام نموذج Bhattacharyya (1964)
        
        Args:
            observation_point: نقطة القياس [x, y, z]
            prism_center: مركز المنشور [x, y, z]
            prism_dims: أبعاد المنشور [dx, dy, dz]
            susceptibility: القابلية المغناطيسية χ
            inducing_field: مجال الحث [Bx, By, Bz]
            
        Returns:
            Vector magnetic field [Bx, By, Bz] in Tesla
        """
        # Simplified prism model using equivalent dipole approximation
        # For more accuracy, use full integral formulation
        
        volume = np.prod(prism_dims)
        
        # Induced magnetization: M = χ * H = χ * B / μ₀
        magnetization = susceptibility * inducing_field / self.MU_0
        
        # Equivalent dipole moment: m = M * V
        dipole_moment = magnetization * volume
        
        return self.dipole_field(observation_point, prism_center, dipole_moment)
    
    def calculate_total_field(self, position: np.ndarray,
                             include_noise: bool = True,
                             include_drift: bool = True,
                             noise_level: float = 0.5,
                             drift_rate: float = 0.01,
                             time: float = 0) -> Tuple[np.ndarray, float]:
        """
        حساب المجال المغناطيسي الكلي في نقطة معينة
        
        Args:
            position: نقطة القياس [x, y, z] في المتر
            include_noise: إضافة ضوضاء محاكاة
            include_drift: إضافة انحراف زمني
            noise_level: مستوى الضوضاء (nT)
            drift_rate: معدل الانحراف (nT/s)
            time: الوقت الحالي (seconds)
            
        Returns:
            Tuple of (vector_field, total_intensity) in nT
        """
        # Start with regional field (Earth's main field)
        # Assuming inclination ~60°, declination ~0° for mid-latitudes
        inclination = np.radians(60)
        regional_vector = np.array([
            self.regional_field * np.cos(inclination),
            0,
            self.regional_field * np.sin(inclination)
        ])
        
        total_anomaly = np.zeros(3)
        
        # Calculate contribution from each geological body
        for body in self.bodies:
            body_pos = np.array(body.position)
            body_dims = np.array(body.dimensions)
            
            if body.body_type == 'dipole':
                if body.magnetization is not None:
                    dipole_moment = body.magnetization
                else:
                    # Create dipole moment from susceptibility
                    volume = np.prod(body_dims)
                    induced_m = body.susceptibility * regional_vector / self.MU_0 * volume
                    dipole_moment = induced_m
                    
                anomaly = self.dipole_field(position, body_pos, dipole_moment)
                
            elif body.body_type == 'prism':
                anomaly = self.prism_field(
                    position, body_pos, body_dims,
                    body.susceptibility, regional_vector
                )
                
            elif body.body_type == 'layer':
                # Horizontal layer approximation
                depth = body_pos[2]
                if position[2] > depth:  # Above the layer
                    # Simple infinite slab approximation
                    layer_thickness = body_dims[2]
                    anomaly_z = (self.MU_0 / 2) * body.susceptibility * \
                               (regional_vector[2] / self.MU_0) * layer_thickness
                    anomaly = np.array([0, 0, anomaly_z])
                else:
                    anomaly = np.zeros(3)
                    
            else:
                anomaly = np.zeros(3)
            
            total_anomaly += anomaly
        
        # Convert to nT (1 T = 10^9 nT)
        total_vector = (regional_vector + total_anomaly) * 1e9
        total_intensity = np.linalg.norm(total_vector)
        
        # Add noise
        if include_noise:
            noise = np.random.normal(0, noise_level, 3)
            total_vector += noise
            total_intensity = np.linalg.norm(total_vector)
        
        # Add drift
        if include_drift:
            drift = drift_rate * time
            total_intensity += drift
        
        return total_vector, total_intensity


class MagnetometerSimulator:
    """
    محاكي جهاز المغناطيسية الكامل
    
    يدمج بين:
    - حسابات فيزيائية دقيقة
    - محاكاة خصائص الجهاز
    - أنظمة المسح المختلفة
    """
    
    def __init__(self, 
                 mag_type: MagnetometerType = MagnetometerType.PPM,
                 performance_mode: PerformanceMode = PerformanceMode.DEV):
        """
        Initialize the magnetometer simulator
        
        Args:
            mag_type: Type of magnetometer to simulate
            performance_mode: Performance mode (DEV or FULL)
        """
        self.mag_type = mag_type
        self.performance_mode = performance_mode
        self.calculator = MagneticFieldCalculator()
        
        # Device-specific parameters
        self.device_params = self._get_device_parameters()
        
        # Survey parameters
        self.survey_mode = SurveyMode.GRID
        self.survey_lines: List[List[Tuple[float, float, float]]] = []
        self.current_position = np.array([0, 0, 1])  # Default height 1m
        
        # Time series data
        self.readings: List[SensorReading] = []
        self.start_time = 0
        
        # Grid resolution based on performance mode
        if performance_mode == PerformanceMode.DEV:
            self.grid_resolution = 10  # Coarse grid
        else:
            self.grid_resolution = 50  # Fine grid
    
    def _get_device_parameters(self) -> Dict:
        """Get device-specific simulation parameters"""
        params = {
            MagnetometerType.PPM: {
                'sampling_rate': 1.0,  # Hz
                'accuracy': 0.1,  # nT
                'noise_std': 0.5,  # nT
                'drift_rate': 0.01,  # nT/s
                'measurement_time': 2.5,  # seconds per reading
                'range': [20000, 80000],  # nT
                'description': "Proton Precession Magnetometer"
            },
            MagnetometerType.CESIUM: {
                'sampling_rate': 10.0,  # Hz
                'accuracy': 0.01,  # nT
                'noise_std': 0.1,  # nT
                'drift_rate': 0.001,  # nT/s
                'measurement_time': 0.1,  # seconds per reading
                'range': [20000, 80000],  # nT
                'description': "Cesium Vapor Magnetometer"
            },
            MagnetometerType.FLUXGATE: {
                'sampling_rate': 100.0,  # Hz
                'accuracy': 0.5,  # nT
                'noise_std': 1.0,  # nT
                'drift_rate': 0.1,  # nT/s
                'measurement_time': 0.01,  # seconds per reading
                'range': [-100000, 100000],  # nT (vector)
                'description': "Fluxgate Magnetometer"
            }
        }
        return params.get(self.mag_type, params[MagnetometerType.PPM])
    
    def set_position(self, x: float, y: float, z: float):
        """تحديد موقع الجهاز"""
        self.current_position = np.array([x, y, z])
    
    def move_to(self, x: float, y: float, z: float, 
                duration: float = 1.0) -> SensorReading:
        """
        Move the sensor to a new position and take a reading
        
        Args:
            x, y, z: Target position
            duration: Time to move (seconds)
            
        Returns:
            SensorReading at the new position
        """
        current_time = len(self.readings) * self.device_params['measurement_time']
        current_time += duration
        
        self.current_position = np.array([x, y, z])
        
        vector_field, total_intensity = self.calculator.calculate_total_field(
            self.current_position,
            include_noise=True,
            include_drift=True,
            noise_level=self.device_params['noise_std'],
            drift_rate=self.device_params['drift_rate'],
            time=current_time
        )
        
        reading = SensorReading(
            timestamp=current_time,
            position=(x, y, z),
            total_field=total_intensity,
            bx=vector_field[0],
            by=vector_field[1],
            bz=vector_field[2],
            noise=self.device_params['noise_std'],
            drift=self.device_params['drift_rate'] * current_time
        )
        
        self.readings.append(reading)
        return reading
    
    def take_reading(self) -> SensorReading:
        """
        Take a measurement at current position
        
        Returns:
            SensorReading object
        """
        current_time = len(self.readings) * self.device_params['measurement_time']
        
        vector_field, total_intensity = self.calculator.calculate_total_field(
            self.current_position,
            include_noise=True,
            include_drift=True,
            noise_level=self.device_params['noise_std'],
            drift_rate=self.device_params['drift_rate'],
            time=current_time
        )
        
        reading = SensorReading(
            timestamp=current_time,
            position=tuple(self.current_position),
            total_field=total_intensity,
            bx=vector_field[0],
            by=vector_field[1],
            bz=vector_field[2],
            noise=self.device_params['noise_std'],
            drift=self.device_params['drift_rate'] * current_time
        )
        
        self.readings.append(reading)
        return reading
    
    def setup_grid_survey(self, 
                         x_range: Tuple[float, float],
                         y_range: Tuple[float, float],
                         z_height: float = 1.0,
                         nx: int = None,
                         ny: int = None):
        """
        Setup a grid survey pattern
        
        Args:
            x_range: (xmin, xmax) in meters
            y_range: (ymin, ymax) in meters
            z_height: Survey height in meters
            nx: Number of points in x direction
            ny: Number of points in y direction
        """
        if nx is None:
            nx = self.grid_resolution
        if ny is None:
            ny = self.grid_resolution
            
        x_vals = np.linspace(x_range[0], x_range[1], nx)
        y_vals = np.linspace(y_range[0], y_range[1], ny)
        
        self.survey_lines = []
        
        # Create snake pattern
        for i, y in enumerate(y_vals):
            line = []
            if i % 2 == 0:
                x_iter = x_vals
            else:
                x_iter = x_vals[::-1]
                
            for x in x_iter:
                line.append((x, y, z_height))
            
            self.survey_lines.append(line)
        
        self.survey_mode = SurveyMode.GRID
    
    def setup_line_survey(self,
                         start: Tuple[float, float, float],
                         end: Tuple[float, float, float],
                         n_points: int = None):
        """
        Setup a linear survey
        
        Args:
            start: Start position (x, y, z)
            end: End position (x, y, z)
            n_points: Number of measurement points
        """
        if n_points is None:
            n_points = self.grid_resolution
            
        start_arr = np.array(start)
        end_arr = np.array(end)
        
        line = []
        for i in range(n_points):
            t = i / (n_points - 1) if n_points > 1 else 0
            pos = start_arr + t * (end_arr - start_arr)
            line.append(tuple(pos))
        
        self.survey_lines = [line]
        self.survey_mode = SurveyMode.LINE
    
    def execute_survey(self, progress_callback=None) -> List[SensorReading]:
        """
        Execute the configured survey
        
        Args:
            progress_callback: Optional callback function(current, total)
            
        Returns:
            List of SensorReading objects
        """
        readings = []
        total_points = sum(len(line) for line in self.survey_lines)
        current_point = 0
        
        for line_idx, line in enumerate(self.survey_lines):
            for point_idx, pos in enumerate(line):
                reading = self.move_to(*pos)
                readings.append(reading)
                current_point += 1
                
                if progress_callback:
                    progress_callback(current_point, total_points)
        
        return readings
    
    def get_data_as_dict(self) -> Dict:
        """Export survey data as dictionary"""
        return {
            'device_type': self.mag_type.value,
            'performance_mode': self.performance_mode.value,
            'device_params': self.device_params,
            'survey_mode': self.survey_mode.value,
            'readings': [
                {
                    'timestamp': r.timestamp,
                    'position': r.position,
                    'total_field': r.total_field,
                    'bx': r.bx,
                    'by': r.by,
                    'bz': r.bz,
                    'noise': r.noise,
                    'drift': r.drift
                }
                for r in self.readings
            ],
            'geological_bodies': [b.to_dict() for b in self.calculator.bodies]
        }
    
    def export_to_json(self, filename: str):
        """Export all data to JSON file"""
        data = self.get_data_as_dict()
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data exported to {filename}")
    
    def clear_readings(self):
        """Clear all recorded readings"""
        self.readings.clear()


def create_scenario(scenario_name: str) -> MagnetometerSimulator:
    """
    Create predefined geological scenarios
    
    Args:
        scenario_name: Name of scenario ('mining', 'oil_gas', 'archaeology')
        
    Returns:
        Configured MagnetometerSimulator
    """
    sim = MagnetometerSimulator(
        mag_type=MagnetometerType.PPM,
        performance_mode=PerformanceMode.DEV
    )
    
    if scenario_name == 'mining':
        # Mining scenario: Ore body at depth
        ore_body = GeologicalBody(
            id='ore_1',
            body_type='prism',
            position=(0, 0, -20),  # 20m deep
            dimensions=(15, 10, 8),  # 15x10x8 meters
            susceptibility=0.05  # High susceptibility (iron ore)
        )
        sim.calculator.add_body(ore_body)
        
        # Add smaller vein
        vein = GeologicalBody(
            id='vein_1',
            body_type='prism',
            position=(25, 10, -15),
            dimensions=(5, 20, 5),
            susceptibility=0.03
        )
        sim.calculator.add_body(vein)
        
    elif scenario_name == 'oil_gas':
        # Oil & Gas scenario: Deep structure with fault
        basement = GeologicalBody(
            id='basement_1',
            body_type='layer',
            position=(0, 0, -500),
            dimensions=(1000, 1000, 100),
            susceptibility=0.001
        )
        sim.calculator.add_body(basement)
        
        fault_zone = GeologicalBody(
            id='fault_1',
            body_type='prism',
            position=(50, 0, -300),
            dimensions=(20, 200, 150),
            susceptibility=0.002
        )
        sim.calculator.add_body(fault_zone)
        
    elif scenario_name == 'archaeology':
        # Archaeology scenario: Buried structures
        wall_1 = GeologicalBody(
            id='wall_1',
            body_type='prism',
            position=(-5, 0, -2),
            dimensions=(0.5, 10, 1.5),
            susceptibility=0.01
        )
        sim.calculator.add_body(wall_1)
        
        wall_2 = GeologicalBody(
            id='wall_2',
            body_type='prism',
            position=(5, 0, -2),
            dimensions=(0.5, 10, 1.5),
            susceptibility=0.01
        )
        sim.calculator.add_body(wall_2)
        
        # Buried metal object
        metal_obj = GeologicalBody(
            id='metal_1',
            body_type='dipole',
            position=(0, 5, -1.5),
            dimensions=(0.3, 0.3, 0.3),
            susceptibility=0.5  # Very high (metal)
        )
        sim.calculator.add_body(metal_obj)
    
    else:
        # Default scenario: Simple buried prism
        prism = GeologicalBody(
            id='prism_1',
            body_type='prism',
            position=(0, 0, -10),
            dimensions=(10, 10, 5),
            susceptibility=0.02
        )
        sim.calculator.add_body(prism)
    
    return sim


if __name__ == '__main__':
    print("=" * 60)
    print("Magnetometer Physics Engine - Test Run")
    print("محرك فيزيائي لمحاكاة مقياس المغناطيسية")
    print("=" * 60)
    
    # Create a mining scenario
    print("\n[1] Creating Mining Scenario...")
    sim = create_scenario('mining')
    
    print(f"Device Type: {sim.device_params['description']}")
    print(f"Performance Mode: {sim.performance_mode.value}")
    print(f"Number of geological bodies: {len(sim.calculator.bodies)}")
    
    # Setup grid survey
    print("\n[2] Setting up Grid Survey...")
    sim.setup_grid_survey(
        x_range=(-50, 50),
        y_range=(-50, 50),
        z_height=1.0,
        nx=11,  # Small for testing
        ny=11
    )
    
    # Execute survey
    print("\n[3] Executing Survey...")
    readings = sim.execute_survey()
    print(f"Total readings: {len(readings)}")
    
    # Show sample readings
    print("\n[4] Sample Readings:")
    for i, r in enumerate(readings[:5]):
        print(f"  Point {i+1}: Position={r.position}, Total Field={r.total_field:.2f} nT")
    
    # Export to JSON
    print("\n[5] Exporting Data...")
    sim.export_to_json('/workspace/MagnetometerSim/data/survey_data.json')
    
    # Calculate statistics
    print("\n[6] Statistics:")
    fields = [r.total_field for r in readings]
    print(f"  Min Field: {min(fields):.2f} nT")
    print(f"  Max Field: {max(fields):.2f} nT")
    print(f"  Mean Field: {np.mean(fields):.2f} nT")
    print(f"  Std Dev: {np.std(fields):.2f} nT")
    
    print("\n" + "=" * 60)
    print("Physics Engine Test Complete!")
    print("=" * 60)
