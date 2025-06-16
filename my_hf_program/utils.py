import numpy as np

def compute_nuclear_repulsion(mol):
    coords = mol.get_nuclear_coords()
    Z = mol.get_atomic_numbers()
    E_nuc = 0.0
    n = len(Z)
    for i in range(n):
        for j in range(i+1, n):
            R = np.linalg.norm(np.array(coords[i]) - np.array(coords[j]))
            E_nuc += Z[i] * Z[j] / R
    return E_nuc
