#!/usr/bin/env python3
"""
Survey Engine - Complete Survey Planning and Execution
=======================================================
محرك المسح - تخطيط وتنفيذ المسوحات المغناطيسية

يدعم:
- Grid Survey (مسح شبكي)
- Line Survey (مسح خطي)
- Walking Mode (وضع المشي)
- Drone Mode (وضع الطائرة بدون طيار)

Author: AI Assistant
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import sys

# Add physics engine to path
sys.path.append('/workspace/MagnetometerSim/physics_engine')
from magnetometer_physics import (
    MagnetometerSimulator, 
    MagnetometerType, 
    PerformanceMode,
    SensorReading,
    GeologicalBody
)
from geological_engine import GeologicalModel


class SurveyType(Enum):
    """أنواع المسح"""
    GRID = "grid"
    LINE = "line"
    RANDOM = "random"
    PROFILE = "profile"
    RECONNAISSANCE = "reconnaissance"


class NavigationMode(Enum):
    """أنماط الملاحة"""
    WALKING = "walking"
    VEHICLE = "vehicle"
    DRONE = "drone"
    MARINE = "marine"


@dataclass
class SurveyParameters:
    """معايير المسح"""
    survey_type: SurveyType
    navigation_mode: NavigationMode
    area_bounds: Tuple[float, float, float, float]  # xmin, xmax, ymin, ymax
    line_spacing: float  # meters
    station_spacing: float  # meters
    survey_height: float  # meters above ground
    tie_line_spacing: float = 0.0  # 0 = no tie lines
    base_station_interval: int = 0  # 0 = no base station readings
    
    def to_dict(self) -> Dict:
        return {
            'survey_type': self.survey_type.value,
            'navigation_mode': self.navigation_mode.value,
            'area_bounds': self.area_bounds,
            'line_spacing': self.line_spacing,
            'station_spacing': self.station_spacing,
            'survey_height': self.survey_height,
            'tie_line_spacing': self.tie_line_spacing,
            'base_station_interval': self.base_station_interval
        }


@dataclass
class SurveyLine:
    """تمثيل خط مسح"""
    id: str
    line_type: str  # 'main', 'tie', 'base'
    stations: List[Tuple[float, float, float]]  # x, y, z coordinates
    length: float  # meters
    azimuth: float  # degrees from North
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'line_type': self.line_type,
            'stations': self.stations,
            'length': self.length,
            'azimuth': self.azimuth
        }


class SurveyPlanner:
    """
    مخطط المسح
    
    يولد أنماط مسح مختلفة بناءً على المعايير المحددة
    """
    
    def __init__(self, params: SurveyParameters):
        """
        Initialize survey planner
        
        Args:
            params: Survey parameters
        """
        self.params = params
        self.lines: List[SurveyLine] = []
        self.total_stations = 0
        self.estimated_time = 0.0  # seconds
    
    def generate_grid_survey(self) -> List[SurveyLine]:
        """
        Generate grid survey pattern
        
        Returns:
            List of survey lines
        """
        xmin, xmax, ymin, ymax = self.params.area_bounds
        line_spacing = self.params.line_spacing
        station_spacing = self.params.station_spacing
        height = self.params.survey_height
        
        self.lines = []
        line_id = 0
        
        # Main lines (parallel to x-axis)
        y_current = ymin
        direction = 1  # 1 = east, -1 = west
        
        while y_current <= ymax:
            if direction == 1:
                x_start, x_end = xmin, xmax
            else:
                x_start, x_end = xmax, xmin
            
            # Generate stations along line
            n_stations = int(abs(x_end - x_start) / station_spacing) + 1
            x_vals = np.linspace(x_start, x_end, n_stations)
            
            stations = [(x, y_current, height) for x in x_vals]
            line_length = abs(x_end - x_start)
            azimuth = 90 if direction == 1 else 270
            
            self.lines.append(SurveyLine(
                id=f"L{line_id:03d}",
                line_type='main',
                stations=stations,
                length=line_length,
                azimuth=azimuth
            ))
            
            line_id += 1
            y_current += line_spacing
            direction *= -1  # Reverse direction (snake pattern)
        
        # Tie lines (parallel to y-axis) if specified
        if self.params.tie_line_spacing > 0:
            tie_spacing = self.params.tie_line_spacing
            x_current = xmin
            line_id_tie = 1000
            
            while x_current <= xmax:
                n_stations = int((ymax - ymin) / station_spacing) + 1
                y_vals = np.linspace(ymin, ymax, n_stations)
                
                stations = [(x_current, y, height) for y in y_vals]
                line_length = ymax - ymin
                
                self.lines.append(SurveyLine(
                    id=f"T{line_id_tie:03d}",
                    line_type='tie',
                    stations=stations,
                    length=line_length,
                    azimuth=0
                ))
                
                line_id_tie += 1
                x_current += tie_spacing
        
        self.total_stations = sum(len(line.stations) for line in self.lines)
        self._estimate_time()
        
        return self.lines
    
    def generate_line_survey(self, 
                            start: Tuple[float, float],
                            end: Tuple[float, float]) -> List[SurveyLine]:
        """
        Generate linear survey between two points
        
        Args:
            start: Start point (x, y)
            end: End point (x, y)
            
        Returns:
            List of survey lines (single line)
        """
        height = self.params.survey_height
        station_spacing = self.params.station_spacing
        
        start_arr = np.array(start)
        end_arr = np.array(end)
        
        # Calculate line properties
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = np.sqrt(dx**2 + dy**2)
        azimuth = np.degrees(np.arctan2(dx, dy)) % 360
        
        # Generate stations
        n_stations = int(length / station_spacing) + 1
        t_vals = np.linspace(0, 1, n_stations)
        
        stations = []
        for t in t_vals:
            x = start[0] + t * dx
            y = start[1] + t * dy
            stations.append((x, y, height))
        
        self.lines = [SurveyLine(
            id="L001",
            line_type='main',
            stations=stations,
            length=length,
            azimuth=azimuth
        )]
        
        self.total_stations = len(stations)
        self._estimate_time()
        
        return self.lines
    
    def generate_random_survey(self, 
                              n_stations: int,
                              seed: int = None) -> List[SurveyLine]:
        """
        Generate random survey stations (reconnaissance)
        
        Args:
            n_stations: Number of stations
            seed: Random seed
            
        Returns:
            List of survey lines
        """
        if seed is not None:
            np.random.seed(seed)
        
        xmin, xmax, ymin, ymax = self.params.area_bounds
        height = self.params.survey_height
        
        # Generate random positions
        x_rand = np.random.uniform(xmin, xmax, n_stations)
        y_rand = np.random.uniform(ymin, ymax, n_stations)
        
        stations = [(x, y, height) for x, y in zip(x_rand, y_rand)]
        
        self.lines = [SurveyLine(
            id="R001",
            line_type='random',
            stations=stations,
            length=0,
            azimuth=0
        )]
        
        self.total_stations = n_stations
        self._estimate_time()
        
        return self.lines
    
    def _estimate_time(self):
        """Estimate survey time based on navigation mode"""
        # Average speeds (m/s)
        speeds = {
            NavigationMode.WALKING: 1.0,
            NavigationMode.VEHICLE: 5.0,
            NavigationMode.DRONE: 10.0,
            NavigationMode.MARINE: 3.0
        }
        
        speed = speeds.get(self.params.navigation_mode, 1.0)
        
        # Time per station (seconds)
        station_times = {
            MagnetometerType.PPM: 3.0,
            MagnetometerType.CESIUM: 0.5,
            MagnetometerType.FLUXGATE: 0.2
        }
        
        # Assume PPM for estimation
        station_time = station_times[MagnetometerType.PPM]
        
        # Total line distance
        total_distance = sum(line.length for line in self.lines)
        
        # Travel time + measurement time
        travel_time = total_distance / speed
        measurement_time = self.total_stations * station_time
        
        self.estimated_time = travel_time + measurement_time
    
    def export_to_json(self, filename: str):
        """Export survey plan to JSON"""
        data = {
            'parameters': self.params.to_dict(),
            'lines': [line.to_dict() for line in self.lines],
            'total_stations': self.total_stations,
            'estimated_time_seconds': self.estimated_time,
            'estimated_time_hours': self.estimated_time / 3600
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Survey plan exported to {filename}")
    
    def get_statistics(self) -> Dict:
        """Get survey statistics"""
        return {
            'total_lines': len(self.lines),
            'main_lines': sum(1 for l in self.lines if l.line_type == 'main'),
            'tie_lines': sum(1 for l in self.lines if l.line_type == 'tie'),
            'total_stations': self.total_stations,
            'total_distance_m': sum(line.length for line in self.lines),
            'estimated_time_hours': self.estimated_time / 3600,
            'navigation_mode': self.params.navigation_mode.value
        }


class SurveyExecutor:
    """
    منفذ المسح
    
    ينفذ المسح المخطط ويسجل القراءات
    """
    
    def __init__(self, 
                 simulator: MagnetometerSimulator,
                 geological_model: GeologicalModel = None):
        """
        Initialize survey executor
        
        Args:
            simulator: Magnetometer simulator
            geological_model: Optional geological model
        """
        self.simulator = simulator
        self.geological_model = geological_model
        self.readings: List[SensorReading] = []
        self.current_line = None
        self.current_station = 0
        self.start_time = None
        self.end_time = None
    
    def execute_survey(self, 
                      planner: SurveyPlanner,
                      progress_callback: Callable = None) -> List[SensorReading]:
        """
        Execute planned survey
        
        Args:
            planner: Survey planner with generated lines
            progress_callback: Optional callback(current, total)
            
        Returns:
            List of sensor readings
        """
        self.readings = []
        self.start_time = datetime.now()
        
        total_stations = sum(len(line.stations) for line in planner.lines)
        current_station = 0
        
        for line in planner.lines:
            self.current_line = line
            
            for station_idx, position in enumerate(line.stations):
                # Move to station and take reading
                if self.geological_model:
                    # Use geological model for field calculation
                    field, intensity = self.geological_model.calculate_field_at_point(
                        *position
                    )
                    
                    # Create reading manually
                    reading = SensorReading(
                        timestamp=current_station * 3.0,  # Approximate
                        position=position,
                        total_field=float(intensity),
                        bx=float(field[0]),
                        by=float(field[1]),
                        bz=float(field[2]),
                        noise=self.simulator.device_params['noise_std'],
                        drift=self.simulator.device_params['drift_rate'] * current_station * 3.0
                    )
                else:
                    # Use simulator
                    self.simulator.set_position(*position)
                    reading = self.simulator.take_reading()
                
                self.readings.append(reading)
                current_station += 1
                self.current_station = station_idx
                
                if progress_callback:
                    progress_callback(current_station, total_stations)
        
        self.end_time = datetime.now()
        
        return self.readings
    
    def add_base_station_reading(self, 
                                 base_position: Tuple[float, float, float],
                                 interval: int):
        """
        Add base station readings at regular intervals
        
        Args:
            base_position: Base station location
            interval: Reading interval (number of stations)
        """
        # Implementation for base station corrections
        pass
    
    def get_quality_control_stats(self) -> Dict:
        """Calculate quality control statistics"""
        if len(self.readings) < 2:
            return {}
        
        fields = [r.total_field for r in self.readings]
        
        return {
            'min_field': min(fields),
            'max_field': max(fields),
            'mean_field': np.mean(fields),
            'std_dev': np.std(fields),
            'range': max(fields) - min(fields),
            'n_readings': len(self.readings),
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        }
    
    def export_readings(self, filename: str):
        """Export readings to JSON"""
        data = {
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
            'qc_stats': self.get_quality_control_stats()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Readings exported to {filename}")


def create_typical_grid_survey() -> Tuple[SurveyPlanner, SurveyExecutor, MagnetometerSimulator]:
    """
    Create a typical grid survey setup
    
    Returns:
        Tuple of (planner, executor, simulator)
    """
    # Create survey parameters
    params = SurveyParameters(
        survey_type=SurveyType.GRID,
        navigation_mode=NavigationMode.WALKING,
        area_bounds=(-50, 50, -50, 50),
        line_spacing=10,
        station_spacing=5,
        survey_height=1.0,
        tie_line_spacing=50
    )
    
    # Create planner
    planner = SurveyPlanner(params)
    planner.generate_grid_survey()
    
    # Create simulator
    simulator = MagnetometerSimulator(
        mag_type=MagnetometerType.PPM,
        performance_mode=PerformanceMode.DEV
    )
    
    # Create executor
    executor = SurveyExecutor(simulator)
    
    return planner, executor, simulator


if __name__ == '__main__':
    print("=" * 60)
    print("Survey Engine - Test Run")
    print("محرك المسح")
    print("=" * 60)
    
    # Create survey planner
    print("\n[1] Creating Survey Plan...")
    params = SurveyParameters(
        survey_type=SurveyType.GRID,
        navigation_mode=NavigationMode.WALKING,
        area_bounds=(-50, 50, -50, 50),
        line_spacing=10,
        station_spacing=5,
        survey_height=1.0,
        tie_line_spacing=50
    )
    
    planner = SurveyPlanner(params)
    lines = planner.generate_grid_survey()
    
    stats = planner.get_statistics()
    print(f"Total Lines: {stats['total_lines']}")
    print(f"Main Lines: {stats['main_lines']}")
    print(f"Tie Lines: {stats['tie_lines']}")
    print(f"Total Stations: {stats['total_stations']}")
    print(f"Total Distance: {stats['total_distance_m']:.1f} m")
    print(f"Estimated Time: {stats['estimated_time_hours']:.2f} hours")
    
    # Export survey plan
    print("\n[2] Exporting Survey Plan...")
    planner.export_to_json('/workspace/MagnetometerSim/data/survey_plan.json')
    
    # Create simulator with geological model
    print("\n[3] Setting up Geological Model...")
    from geological_engine import create_mining_scenario
    geo_model = create_mining_scenario()
    
    simulator = MagnetometerSimulator(
        mag_type=MagnetometerType.PPM,
        performance_mode=PerformanceMode.DEV
    )
    
    # Create executor
    executor = SurveyExecutor(simulator, geological_model=geo_model)
    
    # Execute survey
    print("\n[4] Executing Survey...")
    def progress_callback(current, total):
        if current % 20 == 0 or current == total:
            print(f"  Progress: {current}/{total} ({100*current/total:.1f}%)")
    
    readings = executor.execute_survey(planner, progress_callback=progress_callback)
    print(f"Total Readings: {len(readings)}")
    
    # Quality control
    print("\n[5] Quality Control Statistics:")
    qc = executor.get_quality_control_stats()
    for key, value in qc.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Export readings
    print("\n[6] Exporting Readings...")
    executor.export_readings('/workspace/MagnetometerSim/data/survey_execution.json')
    
    print("\n" + "=" * 60)
    print("Survey Engine Test Complete!")
    print("=" * 60)
