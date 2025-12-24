import os
import platform
import glob
import sys
import shutil

# Setup function to create necessary symlinks and copy dependencies
def _setup_library_symlinks():
    """Create symbolic links for versioned libraries on Linux/macOS.
    Copy gmsh DLL on Windows.
    
    Note: On Linux, libraries use RPATH=$ORIGIN set during build (via patchelf),
    so they automatically find dependencies in the same directory and gmsh in env/lib.
    """
    package_dir = os.path.dirname(os.path.abspath(__file__))
    system = platform.system()
    
    # Windows: Copy gmsh DLL to package directory
    if system == 'Windows':
        # Find gmsh DLL in site-packages/lib or Lib
        site_packages = os.path.dirname(package_dir)
        gmsh_dll_search_paths = [
            os.path.join(site_packages, 'lib'),
            os.path.join(os.path.dirname(site_packages), 'Lib'),
            os.path.join(sys.prefix, 'Lib'),
            os.path.join(sys.prefix, 'Library', 'bin')
        ]
        
        gmsh_dll_found = False
        for search_path in gmsh_dll_search_paths:
            if os.path.exists(search_path):
                gmsh_dlls = glob.glob(os.path.join(search_path, 'gmsh-*.dll'))
                for gmsh_dll in gmsh_dlls:
                    dest = os.path.join(package_dir, os.path.basename(gmsh_dll))
                    if not os.path.exists(dest):
                        try:
                            shutil.copy2(gmsh_dll, dest)
                            gmsh_dll_found = True
                        except (OSError, IOError):
                            pass
        
        # Add package directory to DLL search path
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(package_dir)
            except (OSError, FileNotFoundError):
                pass
    
    # Linux/macOS: Create symbolic links for versioned libraries
    elif system == 'Linux' or system == 'Darwin':
        # Find all .so.X.Y.Z files and create .so.X symlinks
        versioned_pattern = os.path.join(package_dir, '*.so.*.*.*')
        versioned_libs = glob.glob(versioned_pattern)
        
        links_created = 0
        for target_path in versioned_libs:
            target_basename = os.path.basename(target_path)
            parts = target_basename.split('.')
            if len(parts) >= 4 and parts[-3].isdigit():
                link_name = '.'.join(parts[:-2])  # lib*.so.7.4.0 -> lib*.so.7
                link_path = os.path.join(package_dir, link_name)
                
                # Remove existing symlink if it exists
                if os.path.exists(link_path) or os.path.islink(link_path):
                    try:
                        os.remove(link_path)
                    except OSError:
                        pass
                
                # Create new symlink
                try:
                    os.symlink(target_basename, link_path)
                    links_created += 1
                except OSError:
                    pass

# Run setup before importing modules
_setup_library_symlinks()

# Salome legacy
from .fcscore import (
    GEOM_Object,
    GEOM_Field,
    GEOMAlgo_State
)

# OCC legacy
from .fcscore import (
    TColStd_HSequenceOfTransient,
    TopAbs_ShapeEnum,
    ExplodeType,
    ComparisonConditionGeometry,
    ShapeKind,
    SICheckLevel
)

# Core
from .fcscore import (
    ComparisonCondition,
    Color,
    ColorSelection,
    Palette,
    XYZ,
    Line,
    Ray,
    Segment
)

# Geometry
from .fcscore import (
    GeometricShape,
    Geometry3DPrimitives,
    ExtGeometry3DPrimitives,
    GeometryBasicOperations,
    GeometryBlockOperations,
    GeometryBooleanOperations,
    ExtGeometryBooleanOperations,
    GeometryCurveOperations,
    GeometryFieldOperations,
    GeometryGroupOperations,
    GeometryHealingOperations,
    ExtGeometryHealingOperations,
    GeometryInsertOperations,
    GeometryLocalOperations,
    GeometryMeasureOperations,
    ExtGeometryMeasureOperations,
    GeometryShapeOperations,
    ExtGeometryShapeOperations,
    GeometryTransformOperations,
    ImportOperations,
    ExportOperations
)

# Mesh
from .fcscore import (
    EdgeSeedingParameters,
    ElementDimension,
    ElementReferences,
    ElementShape,
    ElementCoupling,
    SolverElementType,
    MeshElementOrder,
    Mesh2DAlgorithmChoice,
    Mesh3DAlgorithmChoice,
    Target3DMeshType,
    RecombineAll,
    RecombinationAlgorithm,
    RecombineNodePositioning,
    Mesh1DSettings,
    Mesh2DSettings,
    MeshNETGEN2DSettings,
    Mesh3DSettings,
    Mesh,
    Element,
    Node,
    ElementSet,
    NodeSet,
    MasterMesh,
    ComponentMesh,
    MeshFactory,
    Mesher3D,
    Quality2DResult,
    QualityMeasure,
    MeshReferenceType,
    MeshFileFormat,
    MeshTransaction,
    SolverProfile,
    ElementShapeToModel,
    ElementAttributes,
    GenericElementType
)

# Model
from .fcscore import (
    Model,
    ItemType,
    StoredEntityType,
    ModelConfiguration,
    ModelItemInstance,
    GeometryInstance,
    MeshComponentInstance,
    MeshSetInstance
)

# Backend Service template
from .fcsservice import ( 
    BackendService,
    fcs_command
)  

# Logger
from .fcslogger import ( 
    FCSLogger,
    DiagnosticLog,
    create_generic_logger
)

# Enum options 
from .fcsoptions import ( 
    StatusMessageType,
    ContainerTypes,
    DataTypes
)

# Geometry builder
from .geometrybuilder import GeometryBuilder

# Cloud model session communicator base class
from .fcsmodelsession import CloudModelCommunicatorBase
