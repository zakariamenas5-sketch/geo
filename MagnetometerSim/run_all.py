#!/usr/bin/env python3
"""
Main Entry Point for Magnetometer Simulation Platform
======================================================
نقطة الدخول الرئيسية لمنصة محاكاة مقياس المغناطيسية

This script runs all engines and generates a complete demonstration.

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add physics engine to path
sys.path.insert(0, '/workspace/MagnetometerSim/physics_engine')

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def run_physics_engine():
    """Run core physics engine"""
    print_header("PHYSICS ENGINE TEST / اختبار المحرك الفيزيائي")
    
    from magnetometer_physics import (
        MagnetometerSimulator, 
        MagnetometerType, 
        PerformanceMode,
        create_scenario
    )
    
    # Create mining scenario
    print("[1] Creating Mining Scenario...")
    sim = create_scenario('mining')
    
    print(f"  Device: {sim.device_params['description']}")
    print(f"  Geological Bodies: {len(sim.calculator.bodies)}")
    
    # Setup survey
    print("\n[2] Setting up Grid Survey...")
    sim.setup_grid_survey(
        x_range=(-50, 50),
        y_range=(-50, 50),
        z_height=1.0,
        nx=11,
        ny=11
    )
    
    # Execute
    print("\n[3] Executing Survey...")
    readings = sim.execute_survey()
    print(f"  Total Readings: {len(readings)}")
    
    # Statistics
    fields = [r.total_field for r in readings]
    print(f"\n[4] Statistics:")
    print(f"  Min: {min(fields):.2f} nT")
    print(f"  Max: {max(fields):.2f} nT")
    print(f"  Mean: {np.mean(fields):.2f} nT")
    
    return sim


def run_geological_engine():
    """Run geological modeling engine"""
    print_header("GEOLOGICAL ENGINE TEST / اختبار المحرك الجيولوجي")
    
    from geological_engine import (
        create_mining_scenario,
        create_oil_gas_scenario,
        create_archaeology_scenario
    )
    
    scenarios = [
        ('Mining', create_mining_scenario),
        ('Oil & Gas', create_oil_gas_scenario),
        ('Archaeology', create_archaeology_scenario)
    ]
    
    models = {}
    
    for name, creator in scenarios:
        print(f"[{name}] Creating Scenario...")
        model = creator()
        models[name.lower()] = model
        
        print(f"  Layers: {len(model.layers)}")
        print(f"  Faults: {len(model.faults)}")
        print(f"  Ore Bodies: {len(model.ore_bodies)}")
        print(f"  Pipes: {len(model.pipes)}")
        print(f"  Targets: {len(model.targets)}")
        
        # Export
        filename = f'/workspace/MagnetometerSim/data/{name.lower().replace(" & ", "_")}_model.json'
        model.export_to_json(filename)
        print()
    
    return models


def run_survey_engine():
    """Run survey planning and execution engine"""
    print_header("SURVEY ENGINE TEST / اختبار محرك المسح")
    
    from survey_engine import (
        SurveyParameters,
        SurveyPlanner,
        SurveyExecutor,
        SurveyType,
        NavigationMode
    )
    from magnetometer_physics import MagnetometerSimulator, MagnetometerType, PerformanceMode
    from geological_engine import create_mining_scenario
    
    # Create survey plan
    print("[1] Creating Survey Plan...")
    params = SurveyParameters(
        survey_type=SurveyType.GRID,
        navigation_mode=NavigationMode.WALKING,
        area_bounds=(-50, 50, -50, 50),
        line_spacing=10,
        station_spacing=5,
        survey_height=1.0
    )
    
    planner = SurveyPlanner(params)
    planner.generate_grid_survey()
    
    stats = planner.get_statistics()
    print(f"  Lines: {stats['total_lines']}")
    print(f"  Stations: {stats['total_stations']}")
    print(f"  Distance: {stats['total_distance_m']:.1f} m")
    print(f"  Est. Time: {stats['estimated_time_hours']:.2f} hours")
    
    # Export plan
    planner.export_to_json('/workspace/MagnetometerSim/data/survey_plan.json')
    
    # Execute with geological model
    print("\n[2] Executing Survey with Geological Model...")
    geo_model = create_mining_scenario()
    simulator = MagnetometerSimulator(
        mag_type=MagnetometerType.PPM,
        performance_mode=PerformanceMode.DEV
    )
    
    executor = SurveyExecutor(simulator, geological_model=geo_model)
    
    def progress(current, total):
        if current % 50 == 0 or current == total:
            print(f"  Progress: {current}/{total} ({100*current/total:.1f}%)")
    
    readings = executor.execute_survey(planner, progress_callback=progress)
    print(f"  Total Readings: {len(readings)}")
    
    # QC Stats
    qc = executor.get_quality_control_stats()
    print(f"\n[3] Quality Control:")
    print(f"  Range: {qc['range']:.2f} nT")
    print(f"  Std Dev: {qc['std_dev']:.2f} nT")
    
    executor.export_readings('/workspace/MagnetometerSim/data/survey_execution.json')
    
    return planner, executor


def run_visualization():
    """Run data visualization"""
    print_header("VISUALIZATION TEST / اختبار التصور")
    
    from visualization import visualize_survey_data
    
    data_file = '/workspace/MagnetometerSim/data/survey_data.json'
    output_dir = '/workspace/MagnetometerSim/data/visualizations'
    
    print(f"[1] Loading Data: {data_file}")
    print(f"[2] Generating Visualizations...")
    
    visualize_survey_data(data_file, output_dir)
    
    print("\n[3] Generated Files:")
    viz_path = Path(output_dir)
    for f in viz_path.glob('*.png'):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.1f} KB")


def summary():
    """Print summary of generated files"""
    print_header("SUMMARY / الملخص")
    
    data_path = Path('/workspace/MagnetometerSim/data')
    
    print("\n📁 Generated Data Files:")
    print("-" * 50)
    
    for f in sorted(data_path.glob('*.json')):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:<30} {size_kb:>8.1f} KB")
    
    print("\n📊 Generated Visualizations:")
    print("-" * 50)
    
    viz_path = data_path / 'visualizations'
    if viz_path.exists():
        for f in sorted(viz_path.glob('*.png')):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.name:<30} {size_kb:>8.1f} KB")
    
    print("\n✅ All Engines Tested Successfully!")
    print("\n📝 Next Steps:")
    print("  1. Review generated JSON files")
    print("  2. Examine visualization PNGs")
    print("  3. Proceed to Unity integration (Phase 2)")


if __name__ == '__main__':
    import numpy as np
    
    print("\n" + "🧲" * 35)
    print(" MAGNETOMETER SIMULATION PLATFORM".center(70))
    print(" منصة محاكاة مقياس المغناطيسية".center(70))
    print("🧲" * 35)
    
    print("\n⚙️  Running Complete System Test...")
    print("   جاري تشغيل اختبار النظام الكامل\n")
    
    try:
        # Run all engines
        sim = run_physics_engine()
        models = run_geological_engine()
        planner, executor = run_survey_engine()
        run_visualization()
        
        # Summary
        summary()
        
        print("\n" + "=" * 70)
        print(" COMPLETE SYSTEM TEST SUCCESSFUL!".center(70))
        print(" نجح اختبار النظام الكامل!".center(70))
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
