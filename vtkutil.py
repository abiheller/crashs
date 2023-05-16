import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import pymeshlab


# Read VTK mesh
def load_vtk(filename):
    rd = vtk.vtkPolyDataReader()
    rd.SetFileName(filename)
    rd.Update()
    return rd.GetOutput()

# Read points from the polydata
def vtk_get_points(pd):
    return vtk_to_numpy(pd.GetPoints().GetData())

# Set points in the polydata
def vtk_set_points(pd, x):
    return pd.GetPoints().SetData(numpy_to_vtk(x))

# Read the faces from the polydata
def vtk_get_triangles(pd):
    return vtk_to_numpy(pd.GetPolys().GetData()).reshape(-1,4)[:,1:]

# Map all point arrays to cell arrays
def vtk_all_point_arrays_to_cell_arrays(pd):
    flt = vtk.vtkPointDataToCellData()
    flt.SetInputData(pd)
    flt.Update()
    return flt.GetOutput()

# Read a point array
def vtk_get_point_array(pd, name):
    a = pd.GetPointData().GetArray(name)
    return vtk_to_numpy(a) if a is not None else None

# Add a cell array to a mesh
def vtk_set_point_array(pd, name, array, array_type=vtk.VTK_FLOAT):
    a = numpy_to_vtk(array, array_type=array_type)
    a.SetName(name)
    pd.GetPointData().AddArray(a)

# Read a cell array
def vtk_get_cell_array(pd, name):
    a = pd.GetCellData().GetArray(name)
    return vtk_to_numpy(a) if a is not None else None

# Add a cell array to a mesh
def vtk_set_cell_array(pd, name, array):
    a = numpy_to_vtk(array)
    a.SetName(name)
    pd.GetCellData().AddArray(a)

# Set generic field data
def vtk_set_field_data(pd, name, array):
    a = numpy_to_vtk(array)
    a.SetName(name)
    pd.GetFieldData().AddArray(a)

# Make a VTK polydata from vertices and triangles
def vtk_make_pd(v, f):
    pd = vtk.vtkPolyData()
    pts = vtk.vtkPoints()
    pts.SetData(numpy_to_vtk(v))
    pd.SetPoints(pts)
    ca = vtk.vtkCellArray()
    ca.SetCells(f.shape[0], numpy_to_vtk(np.insert(f, 0, 3, axis=1).ravel(), array_type=vtk.VTK_ID_TYPE))
    pd.SetPolys(ca)
    return pd

# Clone an existing PD
def vtk_clone_pd(pd):
    pd_clone = vtk.vtkPolyData()
    pd_clone.DeepCopy(pd)
    return pd_clone

# Save VTK polydata
def save_vtk(pd, filename, binary = False):
    wr=vtk.vtkPolyDataWriter()
    wr.SetFileName(filename)
    wr.SetInputData(pd)
    if binary:
        wr.SetFileTypeToBinary()
    wr.Update()

# Reduction using pymeshlab
def decimate(v, f, target_faces):
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(vertex_matrix=v, face_matrix=f))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target_faces,
                                                preserveboundary=True,
                                                preservenormal=True,
                                                preservetopology=True,
                                                planarquadric=True)
    m0 = ms.mesh(0)
    return m0.vertex_matrix(), m0.face_matrix()