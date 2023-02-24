import h5py
import pyvista as pv
import numpy as np
import os


def mapDataToFullGrid(grid,data,indexMap):

    full_data = np.empty(grid.n_cells,)
    full_data[indexMap] = data
    return full_data

absolute_path = os.path.dirname(__file__)
relative_path = "../../data/runBattery3D_resultsVTK.h5"
fname = os.path.join(absolute_path, relative_path)


f = h5py.File(fname, 'r')

## Make unstructured grid

# Create points
points = np.transpose(f['Grid']['points'])

# Create cells
cells = np.transpose(f['Grid']['cells']).astype(int)
cells[:,1:] = cells[:,1:]-1

# Define celltypes
celltypes = np.empty(len(cells), dtype=np.uint8)

# TODO: Make this more general so grid can contain different celltypes
nn = cells[0,0]

if nn == 2:
    ct = 3 # LINE
elif nn == 4:
    ct = 9 # POLYGON - MRST export currently not working for 2D grids
elif nn == 8:
    ct = 12 # HEXAHEDRON
else:
    print("Cell type not implemented")


celltypes[:] = pv.CellType(ct)

# Create grid
grid = pv.UnstructuredGrid(cells, celltypes, points) 

data = f['Electrolyte']['100']['c'][:].ravel()
indexMap = f['Electrolyte']['IndexMap_elyte'][:].ravel().astype(int)
full_data = mapDataToFullGrid(grid,data,indexMap)

#grid.plot(show_edges=True, jupyter_backend='ipyvtklink')
grid.cell_data['c'] = full_data
grid.plot(show_edges=False)


f.close()