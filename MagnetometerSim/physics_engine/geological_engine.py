"""
Geological Engine - Advanced Geological Modeling
=================================================
محرك النمذجة الجيولوجية المتقدم

يدعم:
- طبقات أفقية (Horizontal Layers)
- فوالق (Faults)
- أجسام معدنية (Ore Bodies)
- أنابيب مدفونة (Buried Pipes)
- أهداف بترولية (Oil & Gas Targets)

Author: AI Assistant
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
import json
from enum import Enum

# Import from physics engine
import sys
sys.path.append('/workspace/MagnetometerSim/physics_engine')
from magnetometer_physics import GeologicalBody, MagneticFieldCalculator


class LithologyType(Enum):
    """أنواع الصخور"""
    SEDIMENTARY = "sedimentary"
    IGNEOUS = "igneous"
    METAMORPHIC = "metamorphic"
    UNCONSOLIDATED = "unconsolidated"
    ORE = "ore"
    HYDROCARBON = "hydrocarbon"


class FaultType(Enum):
    """أنواع الفوالق"""
    NORMAL = "normal"
    REVERSE = "reverse"
    STRIKE_SLIP = "strike_slip"
    OBLIQUE = "oblique"


@dataclass
class Layer:
    """تمثيل طبقة جيولوجية أفقية"""
    id: str
    top_depth: float  # Depth to top of layer (m)
    thickness: float  # Layer thickness (m)
    lithology: LithologyType
    susceptibility: float
    density: float = 2.5  # g/cm³
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'top_depth': self.top_depth,
            'thickness': self.thickness,
            'lithology': self.lithology.value,
            'susceptibility': self.susceptibility,
            'density': self.density,
            'description': self.description
        }
    
    def to_geological_body(self, x_size: float = 1000, y_size: float = 1000) -> GeologicalBody:
        """Convert layer to geological body for magnetic calculation"""
        return GeologicalBody(
            id=f"layer_{self.id}",
            body_type='layer',
            position=(0, 0, -(self.top_depth + self.thickness/2)),
            dimensions=(x_size, y_size, self.thickness),
            susceptibility=self.susceptibility
        )


@dataclass
class Fault:
    """تمثيل فالق جيولوجي"""
    id: str
    fault_type: FaultType
    strike: float  # Strike angle (degrees from North)
    dip: float  # Dip angle (degrees from horizontal)
    displacement: float  # Vertical displacement (m)
    position: Tuple[float, float, float]  # Surface intersection point
    length: float  # Fault length along strike (m)
    width: float  # Fault zone width (m)
    susceptibility_contrast: float = 0.001
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'fault_type': self.fault_type.value,
            'strike': self.strike,
            'dip': self.dip,
            'displacement': self.displacement,
            'position': self.position,
            'length': self.length,
            'width': self.width,
            'susceptibility_contrast': self.susceptibility_contrast
        }
    
    def to_geological_body(self) -> GeologicalBody:
        """Convert fault to geological body"""
        # Approximate fault as inclined prism
        return GeologicalBody(
            id=f"fault_{self.id}",
            body_type='prism',
            position=self.position,
            dimensions=(self.width, self.length, abs(self.displacement)),
            susceptibility=self.susceptibility_contrast
        )


@dataclass
class OreBody:
    """تمثيل جسم خام معدني"""
    id: str
    ore_type: str  # 'massive_sulfide', 'banded_iron', 'chromite', etc.
    position: Tuple[float, float, float]  # Center position
    shape: str  # 'ellipsoid', 'pipe', 'irregular'
    dimensions: Tuple[float, float, float]  # Semi-axes or dimensions
    susceptibility: float
    remanent_magnetization: Optional[Tuple[float, float, float]] = None
    grade: float = 0.0  # Ore grade percentage
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'ore_type': self.ore_type,
            'position': self.position,
            'shape': self.shape,
            'dimensions': self.dimensions,
            'susceptibility': self.susceptibility,
            'remanent_magnetization': self.remanent_magnetization,
            'grade': self.grade
        }
    
    def to_geological_body(self) -> GeologicalBody:
        """Convert ore body to geological body"""
        body = GeologicalBody(
            id=f"ore_{self.id}",
            body_type='prism',
            position=self.position,
            dimensions=self.dimensions,
            susceptibility=self.susceptibility
        )
        if self.remanent_magnetization:
            body.magnetization = np.array(self.remanent_magnetization)
        return body


@dataclass
class BuriedPipe:
    """تمثيل أنبوب مدفون"""
    id: str
    pipe_type: str  # 'steel', 'cast_iron', 'concrete', 'plastic'
    start_position: Tuple[float, float, float]
    end_position: Tuple[float, float, float]
    diameter: float  # meters
    depth: float  # burial depth (m)
    wall_thickness: float = 0.01  # meters
    susceptibility: float = 0.1  # High for steel pipes
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'pipe_type': self.pipe_type,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'diameter': self.diameter,
            'depth': self.depth,
            'wall_thickness': self.wall_thickness,
            'susceptibility': self.susceptibility
        }
    
    def to_geological_bodies(self, n_segments: int = 10) -> List[GeologicalBody]:
        """Convert pipe to series of prism segments"""
        bodies = []
        start = np.array(self.start_position)
        end = np.array(self.end_position)
        
        segment_length = np.linalg.norm(end - start) / n_segments
        direction = (end - start) / np.linalg.norm(end - start)
        
        for i in range(n_segments):
            t1 = i / n_segments
            t2 = (i + 1) / n_segments
            center = start + (t1 + t2) / 2 * (end - start)
            center[2] = -self.depth
            
            bodies.append(GeologicalBody(
                id=f"pipe_{self.id}_seg{i}",
                body_type='prism',
                position=tuple(center),
                dimensions=(self.diameter, segment_length, self.diameter),
                susceptibility=self.susceptibility
            ))
        
        return bodies


@dataclass
class OilGasTarget:
    """تمثيل هدف بترولي"""
    id: str
    target_type: str  # 'anticline', 'salt_dome', 'stratigraphic_trap'
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]
    depth: float
    porosity: float = 0.2
    fluid_saturation: str = 'oil'  # 'oil', 'gas', 'water'
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'target_type': self.target_type,
            'position': self.position,
            'dimensions': self.dimensions,
            'depth': self.depth,
            'porosity': self.porosity,
            'fluid_saturation': self.fluid_saturation
        }
    
    def to_geological_body(self) -> GeologicalBody:
        """Convert to geological body (usually low susceptibility contrast)"""
        # Hydrocarbon reservoirs typically have lower susceptibility than surroundings
        return GeologicalBody(
            id=f"target_{self.id}",
            body_type='prism',
            position=self.position,
            dimensions=self.dimensions,
            susceptibility=-0.0001  # Negative contrast
        )


class GeologicalModel:
    """
    نموذج جيولوجي متكامل
    
    يجمع بين مختلف العناصر الجيولوجية
    """
    
    # Typical susceptibility values (SI units)
    SUSCEPTIBILITY_TABLE = {
        LithologyType.SEDIMENTARY: 0.0001,
        LithologyType.IGNEOUS: 0.01,
        LithologyType.METAMORPHIC: 0.005,
        LithologyType.UNCONSOLIDATED: 0.00005,
        LithologyType.ORE: 0.05,
        LithologyType.HYDROCARBON: -0.0001
    }
    
    def __init__(self, name: str = "Geological Model"):
        """
        Initialize geological model
        
        Args:
            name: Model name
        """
        self.name = name
        self.layers: List[Layer] = []
        self.faults: List[Fault] = []
        self.ore_bodies: List[OreBody] = []
        self.pipes: List[BuriedPipe] = []
        self.targets: List[OilGasTarget] = []
        
        # Calculator for magnetic field
        self.calculator = MagneticFieldCalculator()
    
    def add_layer(self, layer: Layer):
        """إضافة طبقة"""
        self.layers.append(layer)
        self._update_calculator()
    
    def add_fault(self, fault: Fault):
        """إضافة فالق"""
        self.faults.append(fault)
        self._update_calculator()
    
    def add_ore_body(self, ore: OreBody):
        """إضافة جسم خام"""
        self.ore_bodies.append(ore)
        self._update_calculator()
    
    def add_pipe(self, pipe: BuriedPipe):
        """إضافة أنبوب"""
        self.pipes.append(pipe)
        self._update_calculator()
    
    def add_target(self, target: OilGasTarget):
        """إضافة هدف بترولي"""
        self.targets.append(target)
        self._update_calculator()
    
    def remove_element(self, element_id: str):
        """إزالة عنصر بالنموذج"""
        # Remove from all lists
        self.layers = [l for l in self.layers if l.id != element_id]
        self.faults = [f for f in self.faults if f.id != element_id]
        self.ore_bodies = [o for o in self.ore_bodies if o.id != element_id]
        self.pipes = [p for p in self.pipes if p.id != element_id]
        self.targets = [t for t in self.targets if t.id != element_id]
        
        self._update_calculator()
    
    def _update_calculator(self):
        """Update magnetic field calculator with current model"""
        self.calculator.clear_bodies()
        
        # Add layers
        for layer in self.layers:
            body = layer.to_geological_body()
            self.calculator.add_body(body)
        
        # Add faults
        for fault in self.faults:
            body = fault.to_geological_body()
            self.calculator.add_body(body)
        
        # Add ore bodies
        for ore in self.ore_bodies:
            body = ore.to_geological_body()
            self.calculator.add_body(body)
        
        # Add pipes (as multiple segments)
        for pipe in self.pipes:
            bodies = pipe.to_geological_bodies()
            for body in bodies:
                self.calculator.add_body(body)
        
        # Add targets
        for target in self.targets:
            body = target.to_geological_body()
            self.calculator.add_body(body)
    
    def get_all_geological_bodies(self) -> List[GeologicalBody]:
        """Get all geological bodies as list"""
        bodies = []
        
        for layer in self.layers:
            bodies.append(layer.to_geological_body())
        
        for fault in self.faults:
            bodies.append(fault.to_geological_body())
        
        for ore in self.ore_bodies:
            bodies.append(ore.to_geological_body())
        
        for pipe in self.pipes:
            bodies.extend(pipe.to_geological_bodies())
        
        for target in self.targets:
            bodies.append(target.to_geological_body())
        
        return bodies
    
    def calculate_field_at_point(self, x: float, y: float, z: float) -> Tuple[np.ndarray, float]:
        """
        Calculate magnetic field at a point
        
        Args:
            x, y, z: Position coordinates
            
        Returns:
            Tuple of (vector_field, total_intensity)
        """
        position = np.array([x, y, z])
        return self.calculator.calculate_total_field(position)
    
    def to_dict(self) -> Dict:
        """Export model to dictionary"""
        return {
            'name': self.name,
            'layers': [l.to_dict() for l in self.layers],
            'faults': [f.to_dict() for f in self.faults],
            'ore_bodies': [o.to_dict() for o in self.ore_bodies],
            'pipes': [p.to_dict() for p in self.pipes],
            'targets': [t.to_dict() for t in self.targets]
        }
    
    def export_to_json(self, filename: str):
        """Export model to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Model exported to {filename}")
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GeologicalModel':
        """Create model from dictionary"""
        model = cls(name=data.get('name', 'Imported Model'))
        
        # Reconstruct layers
        for layer_data in data.get('layers', []):
            layer = Layer(
                id=layer_data['id'],
                top_depth=layer_data['top_depth'],
                thickness=layer_data['thickness'],
                lithology=LithologyType(layer_data['lithology']),
                susceptibility=layer_data['susceptibility'],
                density=layer_data.get('density', 2.5),
                description=layer_data.get('description', '')
            )
            model.add_layer(layer)
        
        # Reconstruct faults
        for fault_data in data.get('faults', []):
            fault = Fault(
                id=fault_data['id'],
                fault_type=FaultType(fault_data['fault_type']),
                strike=fault_data['strike'],
                dip=fault_data['dip'],
                displacement=fault_data['displacement'],
                position=tuple(fault_data['position']),
                length=fault_data['length'],
                width=fault_data['width'],
                susceptibility_contrast=fault_data.get('susceptibility_contrast', 0.001)
            )
            model.add_fault(fault)
        
        # Reconstruct ore bodies
        for ore_data in data.get('ore_bodies', []):
            ore = OreBody(
                id=ore_data['id'],
                ore_type=ore_data['ore_type'],
                position=tuple(ore_data['position']),
                shape=ore_data['shape'],
                dimensions=tuple(ore_data['dimensions']),
                susceptibility=ore_data['susceptibility'],
                remanent_magnetization=ore_data.get('remanent_magnetization'),
                grade=ore_data.get('grade', 0.0)
            )
            model.add_ore_body(ore)
        
        # Reconstruct pipes
        for pipe_data in data.get('pipes', []):
            pipe = BuriedPipe(
                id=pipe_data['id'],
                pipe_type=pipe_data['pipe_type'],
                start_position=tuple(pipe_data['start_position']),
                end_position=tuple(pipe_data['end_position']),
                diameter=pipe_data['diameter'],
                depth=pipe_data['depth'],
                wall_thickness=pipe_data.get('wall_thickness', 0.01),
                susceptibility=pipe_data.get('susceptibility', 0.1)
            )
            model.add_pipe(pipe)
        
        # Reconstruct targets
        for target_data in data.get('targets', []):
            target = OilGasTarget(
                id=target_data['id'],
                target_type=target_data['target_type'],
                position=tuple(target_data['position']),
                dimensions=tuple(target_data['dimensions']),
                depth=target_data['depth'],
                porosity=target_data.get('porosity', 0.2),
                fluid_saturation=target_data.get('fluid_saturation', 'oil')
            )
            model.add_target(target)
        
        return model


def create_mining_scenario() -> GeologicalModel:
    """إنشاء سيناريو تعدين نموذجي"""
    model = GeologicalModel(name="Mining Exploration Scenario")
    
    # Add stratigraphy
    overburden = Layer(
        id="layer_overburden",
        top_depth=0,
        thickness=5,
        lithology=LithologyType.UNCONSOLIDATED,
        susceptibility=0.00005,
        description="Surface overburden"
    )
    model.add_layer(overburden)
    
    host_rock = Layer(
        id="layer_host",
        top_depth=5,
        thickness=50,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.0001,
        description="Host sedimentary rock"
    )
    model.add_layer(host_rock)
    
    basement = Layer(
        id="layer_basement",
        top_depth=55,
        thickness=500,
        lithology=LithologyType.IGNEOUS,
        susceptibility=0.01,
        description="Crystalline basement"
    )
    model.add_layer(basement)
    
    # Add ore body (massive sulfide)
    ore = OreBody(
        id="ore_massive_sulfide",
        ore_type="massive_sulfide",
        position=(0, 0, -30),
        shape="ellipsoid",
        dimensions=(20, 15, 10),
        susceptibility=0.08,
        grade=15.0,
        remanent_magnetization=(0.5, 0, 2.0)
    )
    model.add_ore_body(ore)
    
    # Add fault
    fault = Fault(
        id="fault_main",
        fault_type=FaultType.NORMAL,
        strike=45,
        dip=60,
        displacement=10,
        position=(50, 0, 0),
        length=200,
        width=5,
        susceptibility_contrast=0.002
    )
    model.add_fault(fault)
    
    # Add buried pipe (infrastructure)
    pipe = BuriedPipe(
        id="pipe_water",
        pipe_type="steel",
        start_position=(-30, -30, 0),
        end_position=(30, 30, 0),
        diameter=0.5,
        depth=2,
        susceptibility=0.5
    )
    model.add_pipe(pipe)
    
    return model


def create_oil_gas_scenario() -> GeologicalModel:
    """إنشاء سيناريو استكشاف نفطي"""
    model = GeologicalModel(name="Oil & Gas Exploration Scenario")
    
    # Deep stratigraphy
    shallow = Layer(
        id="layer_shallow",
        top_depth=0,
        thickness=100,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.0001,
        description="Shallow sediments"
    )
    model.add_layer(shallow)
    
    reservoir = Layer(
        id="layer_reservoir",
        top_depth=100,
        thickness=50,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.00008,
        description="Reservoir sandstone"
    )
    model.add_layer(reservoir)
    
    source = Layer(
        id="layer_source",
        top_depth=150,
        thickness=100,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.00015,
        description="Source rock (shale)"
    )
    model.add_layer(source)
    
    basement = Layer(
        id="layer_basement",
        top_depth=250,
        thickness=1000,
        lithology=LithologyType.IGNEOUS,
        susceptibility=0.005,
        description="Basement complex"
    )
    model.add_layer(basement)
    
    # Anticlinal trap
    anticline = OilGasTarget(
        id="target_anticline",
        target_type="anticline",
        position=(0, 0, -125),
        dimensions=(200, 100, 30),
        depth=125,
        porosity=0.25,
        fluid_saturation='oil'
    )
    model.add_target(anticline)
    
    # Salt dome
    salt_dome = OilGasTarget(
        id="target_salt",
        target_type="salt_dome",
        position=(300, 0, -300),
        dimensions=(150, 150, 400),
        depth=300,
        porosity=0.05,
        fluid_saturation='gas'
    )
    model.add_target(salt_dome)
    
    # Growth fault
    growth_fault = Fault(
        id="fault_growth",
        fault_type=FaultType.NORMAL,
        strike=90,
        dip=45,
        displacement=50,
        position=(150, 0, 0),
        length=500,
        width=10,
        susceptibility_contrast=0.0005
    )
    model.add_fault(growth_fault)
    
    return model


def create_archaeology_scenario() -> GeologicalModel:
    """إنشاء سيناريو آثار"""
    model = GeologicalModel(name="Archaeological Survey Scenario")
    
    # Shallow stratigraphy
    topsoil = Layer(
        id="layer_topsoil",
        top_depth=0,
        thickness=0.5,
        lithology=LithologyType.UNCONSOLIDATED,
        susceptibility=0.0001,
        description="Topsoil"
    )
    model.add_layer(topsoil)
    
    subsoil = Layer(
        id="layer_subsoil",
        top_depth=0.5,
        thickness=2,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.00005,
        description="Subsoil"
    )
    model.add_layer(subsoil)
    
    bedrock = Layer(
        id="layer_bedrock",
        top_depth=2.5,
        thickness=100,
        lithology=LithologyType.SEDIMENTARY,
        susceptibility=0.0002,
        description="Bedrock"
    )
    model.add_layer(bedrock)
    
    # Buried walls
    wall1 = OreBody(
        id="wall_north",
        ore_type="brick",
        position=(-5, 0, -1.25),
        shape="pipe",
        dimensions=(0.5, 15, 1.5),
        susceptibility=0.01
    )
    model.add_ore_body(wall1)
    
    wall2 = OreBody(
        id="wall_south",
        ore_type="brick",
        position=(5, 0, -1.25),
        shape="pipe",
        dimensions=(0.5, 15, 1.5),
        susceptibility=0.01
    )
    model.add_ore_body(wall2)
    
    wall3 = OreBody(
        id="wall_east",
        ore_type="brick",
        position=(0, 7.5, -1.25),
        shape="pipe",
        dimensions=(11, 0.5, 1.5),
        susceptibility=0.01
    )
    model.add_ore_body(wall3)
    
    # Metal artifacts
    artifact1 = OreBody(
        id="artifact_iron",
        ore_type="iron",
        position=(0, 3, -1),
        shape="ellipsoid",
        dimensions=(0.2, 0.1, 0.05),
        susceptibility=0.5,
        remanent_magnetization=(0, 0, 1.0)
    )
    model.add_ore_body(artifact1)
    
    # Modern pipe
    modern_pipe = BuriedPipe(
        id="pipe_modern",
        pipe_type="steel",
        start_position=(-20, -20, 0),
        end_position=(20, -20, 0),
        diameter=0.3,
        depth=1,
        susceptibility=0.3
    )
    model.add_pipe(modern_pipe)
    
    return model


if __name__ == '__main__':
    print("=" * 60)
    print("Geological Engine - Test Run")
    print("محرك النمذجة الجيولوجية")
    print("=" * 60)
    
    # Test mining scenario
    print("\n[1] Creating Mining Scenario...")
    mining_model = create_mining_scenario()
    print(f"Layers: {len(mining_model.layers)}")
    print(f"Faults: {len(mining_model.faults)}")
    print(f"Ore Bodies: {len(mining_model.ore_bodies)}")
    print(f"Pipes: {len(mining_model.pipes)}")
    
    # Export model
    print("\n[2] Exporting Mining Model...")
    mining_model.export_to_json('/workspace/MagnetometerSim/data/mining_model.json')
    
    # Test oil & gas scenario
    print("\n[3] Creating Oil & Gas Scenario...")
    oil_model = create_oil_gas_scenario()
    print(f"Layers: {len(oil_model.layers)}")
    print(f"Targets: {len(oil_model.targets)}")
    print(f"Faults: {len(oil_model.faults)}")
    
    # Export model
    print("\n[4] Exporting Oil & Gas Model...")
    oil_model.export_to_json('/workspace/MagnetometerSim/data/oil_gas_model.json')
    
    # Test archaeology scenario
    print("\n[5] Creating Archaeology Scenario...")
    arch_model = create_archaeology_scenario()
    print(f"Layers: {len(arch_model.layers)}")
    print(f"Walls: {len(arch_model.ore_bodies)}")
    print(f"Pipes: {len(arch_model.pipes)}")
    
    # Export model
    print("\n[6] Exporting Archaeology Model...")
    arch_model.export_to_json('/workspace/MagnetometerSim/data/archaeology_model.json')
    
    # Test field calculation
    print("\n[7] Testing Field Calculation...")
    field, intensity = mining_model.calculate_field_at_point(0, 0, 1)
    print(f"Field at (0, 0, 1): Vector={field} nT, Total={intensity:.2f} nT")
    
    print("\n" + "=" * 60)
    print("Geological Engine Test Complete!")
    print("=" * 60)
