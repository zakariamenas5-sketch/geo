"""
Data Visualization Module for Magnetometer Survey Data
=======================================================
وحدة تصور البيانات لمسوحات المغناطيسية

تنتج:
- خرائط كونتورية (Contour Maps)
- مقاطع مغناطيسية (Magnetic Profiles)
- خرائط حرارية (Heat Maps)

Author: AI Assistant
Version: 1.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class MagneticDataVisualizer:
    """
    محاور بيانات المغناطيسية
    
    ينتج تصورات ثنائية الأبعاد للبيانات المغناطيسية
    """
    
    def __init__(self, data_file: str = None):
        """
        Initialize the visualizer
        
        Args:
            data_file: Path to JSON survey data file
        """
        self.data = None
        self.positions = None
        self.total_fields = None
        self.bx = None
        self.by = None
        self.bz = None
        
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, data_file: str):
        """Load survey data from JSON file"""
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        readings = self.data['readings']
        
        self.positions = np.array([r['position'] for r in readings])
        self.total_fields = np.array([r['total_field'] for r in readings])
        self.bx = np.array([r['bx'] for r in readings])
        self.by = np.array([r['by'] for r in readings])
        self.bz = np.array([r['bz'] for r in readings])
        
        print(f"Loaded {len(readings)} survey points")
    
    def load_from_dict(self, data_dict: Dict):
        """Load survey data from dictionary"""
        self.data = data_dict
        readings = data_dict['readings']
        
        self.positions = np.array([r['position'] for r in readings])
        self.total_fields = np.array([r['total_field'] for r in readings])
        self.bx = np.array([r['bx'] for r in readings])
        self.by = np.array([r['by'] for r in readings])
        self.bz = np.array([r['bz'] for r in readings])
    
    def create_contour_map(self, 
                          output_file: str = None,
                          title: str = "Magnetic Field Contour Map",
                          cmap: str = 'jet',
                          show_colorbar: bool = True,
                          resolution: int = 100):
        """
        Create a contour map of the magnetic field
        
        Args:
            output_file: Output file path (if None, display interactively)
            title: Plot title
            cmap: Colormap name
            show_colorbar: Whether to show colorbar
            resolution: Grid resolution for interpolation
        """
        if self.positions is None:
            raise ValueError("No data loaded")
        
        # Extract x, y coordinates
        x = self.positions[:, 0]
        y = self.positions[:, 1]
        z = self.total_fields
        
        # Create grid for interpolation
        xi = np.linspace(x.min(), x.max(), resolution)
        yi = np.linspace(y.min(), y.max(), resolution)
        XI, YI = np.meshgrid(xi, yi)
        
        # Interpolate data using nearest neighbor
        from scipy.interpolate import griddata
        ZI = griddata((x, y), z, (XI, YI), method='linear')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create contour plot
        levels = np.linspace(z.min(), z.max(), 20)
        contour = ax.contourf(XI, YI, ZI, levels=levels, cmap=cmap, alpha=0.8)
        contour_lines = ax.contour(XI, YI, ZI, levels=levels, colors='black', 
                                   linewidths=0.5, alpha=0.5)
        
        # Add colorbar
        if show_colorbar:
            cbar = plt.colorbar(contour, ax=ax)
            cbar.set_label('Total Magnetic Field (nT)', fontsize=12)
        
        # Add labels
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Add survey points
        ax.scatter(x, y, c='white', s=10, alpha=0.5, edgecolors='black', 
                   linewidths=0.5, label='Survey Points')
        
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Contour map saved to {output_file}")
        else:
            plt.show()
        
        return fig, ax
    
    def create_profile_plot(self,
                           line_index: int = 0,
                           output_file: str = None,
                           title: str = "Magnetic Profile"):
        """
        Create a profile plot along a survey line
        
        Args:
            line_index: Index of survey line to plot
            output_file: Output file path
            title: Plot title
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        survey_lines = []
        current_line = []
        
        readings = self.data['readings']
        
        # Reconstruct survey lines from positions
        if len(readings) > 0:
            current_pos = np.array(readings[0]['position'])
            current_line = [0]
            
            for i in range(1, len(readings)):
                pos = np.array(readings[i]['position'])
                dist = np.linalg.norm(pos - current_pos)
                
                # If distance is large, start new line
                if dist > 5:  # 5m threshold
                    survey_lines.append(current_line)
                    current_line = []
                
                current_pos = pos
                current_line.append(i)
            
            survey_lines.append(current_line)
        
        if line_index >= len(survey_lines):
            raise ValueError(f"Line index {line_index} out of range")
        
        line_points = survey_lines[line_index]
        line_x = self.positions[line_points, 0]
        line_y = self.positions[line_points, 1]
        line_z = self.total_fields[line_points]
        
        # Calculate distance along profile
        distances = np.zeros(len(line_points))
        for i in range(1, len(line_points)):
            dx = line_x[i] - line_x[i-1]
            dy = line_y[i] - line_y[i-1]
            distances[i] = distances[i-1] + np.sqrt(dx**2 + dy**2)
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # Main profile plot
        ax1.plot(distances, line_z, 'b-', linewidth=2, label='Total Field')
        ax1.fill_between(distances, line_z.min(), line_z, alpha=0.3, color='blue')
        ax1.set_ylabel('Total Magnetic Field (nT)', fontsize=12)
        ax1.set_title(f'{title} - Line {line_index + 1}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        
        # Map view inset
        ax2.plot(line_x, line_y, 'ro-', markersize=4, linewidth=1.5, 
                 label=f'Line {line_index + 1}')
        ax2.scatter(self.positions[:, 0], self.positions[:, 1], 
                    c='gray', s=5, alpha=0.3, label='All Points')
        ax2.set_xlabel('X Position (m)', fontsize=12)
        ax2.set_ylabel('Y Position (m)', fontsize=12)
        ax2.set_title('Survey Line Location', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')
        ax2.legend(loc='best')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Profile plot saved to {output_file}")
        else:
            plt.show()
        
        return fig, (ax1, ax2)
    
    def create_component_plots(self,
                              output_file: str = None,
                              title: str = "Magnetic Field Components"):
        """
        Create separate plots for each magnetic field component
        
        Args:
            output_file: Output file path
            title: Plot title
        """
        if self.positions is None:
            raise ValueError("No data loaded")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        
        components = [
            (self.total_fields, 'Total Field', 'jet'),
            (self.bx, 'Bx Component', 'coolwarm'),
            (self.by, 'By Component', 'coolwarm'),
            (self.bz, 'Bz Component', 'coolwarm')
        ]
        
        x = self.positions[:, 0]
        y = self.positions[:, 1]
        
        # Create grid
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        XI, YI = np.meshgrid(xi, yi)
        
        from scipy.interpolate import griddata
        
        for idx, (data, comp_name, cmap_name) in enumerate(components):
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            
            # Interpolate
            ZI = griddata((x, y), data, (XI, YI), method='linear')
            
            # Plot
            im = ax.pcolormesh(XI, YI, ZI, cmap=cmap_name, shading='auto')
            ax.scatter(x, y, c='white', s=5, alpha=0.5, edgecolors='black', linewidths=0.3)
            
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(f'{comp_name} (nT)', fontsize=10)
            
            ax.set_xlabel('X Position (m)', fontsize=10)
            ax.set_ylabel('Y Position (m)', fontsize=10)
            ax.set_title(comp_name, fontsize=12, fontweight='bold')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Component plots saved to {output_file}")
        else:
            plt.show()
        
        return fig, axes
    
    def create_anomaly_map(self,
                          regional_field: float = None,
                          output_file: str = None,
                          title: str = "Magnetic Anomaly Map"):
        """
        Create magnetic anomaly map (residual after removing regional field)
        
        Args:
            regional_field: Regional field value to subtract (default: mean)
            output_file: Output file path
            title: Plot title
        """
        if self.positions is None:
            raise ValueError("No data loaded")
        
        if regional_field is None:
            regional_field = np.mean(self.total_fields)
        
        anomalies = self.total_fields - regional_field
        
        x = self.positions[:, 0]
        y = self.positions[:, 1]
        
        # Create grid
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        XI, YI = np.meshgrid(xi, yi)
        
        from scipy.interpolate import griddata
        ZI = griddata((x, y), anomalies, (XI, YI), method='linear')
        
        # Create plot with diverging colormap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        vmax = max(abs(ZI.min()), abs(ZI.max()))
        levels = np.linspace(-vmax, vmax, 30)
        
        contour = ax.contourf(XI, YI, ZI, levels=levels, cmap='RdBu_r', alpha=0.8)
        contour_lines = ax.contour(XI, YI, ZI, levels=levels, colors='black', 
                                   linewidths=0.5, alpha=0.5)
        
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('Magnetic Anomaly (nT)', fontsize=12)
        
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Zero contour line
        ax.contour(XI, YI, ZI, levels=[0], colors='black', linewidths=2, alpha=0.8)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Anomaly map saved to {output_file}")
        else:
            plt.show()
        
        return fig, ax
    
    def create_3d_surface(self,
                         output_file: str = None,
                         title: str = "3D Magnetic Field Surface"):
        """
        Create 3D surface plot of magnetic field
        
        Args:
            output_file: Output file path
            title: Plot title
        """
        if self.positions is None:
            raise ValueError("No data loaded")
        
        from mpl_toolkits.mplot3d import Axes3D
        
        x = self.positions[:, 0]
        y = self.positions[:, 1]
        z = self.total_fields
        
        # Create grid
        xi = np.linspace(x.min(), x.max(), 50)
        yi = np.linspace(y.min(), y.max(), 50)
        XI, YI = np.meshgrid(xi, yi)
        
        from scipy.interpolate import griddata
        ZI = griddata((x, y), z, (XI, YI), method='linear')
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot surface
        surf = ax.plot_surface(XI, YI, ZI, cmap='jet', alpha=0.8, 
                               edgecolor='none', antialiased=True)
        
        # Add scatter points
        ax.scatter(x, y, z, c='red', s=20, alpha=0.5, label='Survey Points')
        
        # Labels
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_zlabel('Total Field (nT)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Colorbar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label('Total Magnetic Field (nT)', fontsize=10)
        
        ax.legend(loc='upper left')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"3D surface saved to {output_file}")
        else:
            plt.show()
        
        return fig, ax


def visualize_survey_data(json_file: str, output_dir: str = '.'):
    """
    Generate all visualizations from survey data
    
    Args:
        json_file: Path to survey data JSON file
        output_dir: Directory to save output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    viz = MagneticDataVisualizer(json_file)
    
    print("\nGenerating Visualizations...")
    print("-" * 50)
    
    # Contour map
    viz.create_contour_map(
        output_file=str(output_path / 'contour_map.png'),
        title="Total Magnetic Field"
    )
    
    # Anomaly map
    viz.create_anomaly_map(
        output_file=str(output_path / 'anomaly_map.png'),
        title="Magnetic Anomaly"
    )
    
    # Component plots
    viz.create_component_plots(
        output_file=str(output_path / 'components.png'),
        title="Magnetic Field Components"
    )
    
    # Profile plot
    viz.create_profile_plot(
        line_index=0,
        output_file=str(output_path / 'profile.png'),
        title="Magnetic Profile"
    )
    
    # 3D surface
    viz.create_3d_surface(
        output_file=str(output_path / 'surface_3d.png'),
        title="3D Magnetic Field"
    )
    
    print("-" * 50)
    print(f"All visualizations saved to {output_path}")


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("Magnetometer Data Visualization")
    print("تصور بيانات المسح المغناطيسي")
    print("=" * 60)
    
    # Default data file
    data_file = '/workspace/MagnetometerSim/data/survey_data.json'
    output_dir = '/workspace/MagnetometerSim/data/visualizations'
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    
    if not Path(data_file).exists():
        print(f"Error: Data file '{data_file}' not found!")
        print("Please run the physics engine first to generate data.")
        sys.exit(1)
    
    print(f"\nLoading data from: {data_file}")
    visualize_survey_data(data_file, output_dir)
    
    print("\n" + "=" * 60)
    print("Visualization Complete!")
    print("=" * 60)
