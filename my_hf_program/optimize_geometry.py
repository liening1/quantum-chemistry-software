import sys
try:
    from pyscf import gto, scf, grad
except ImportError:
    print('PySCF is required for geometry optimization. Please install with: pip install pyscf')
    sys.exit(1)
import numpy as np
from .molecule import load_molecule
from scipy.optimize import minimize


def xyz_to_atomstr(xyz_file):
    atoms = []
    with open(xyz_file, 'r') as f:
        lines = f.readlines()[2:]
        for line in lines:
            parts = line.split()
            atoms.append(f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}")
    return "; ".join(atoms)

def save_xyz(filename, symbols, coords, comment="Optimized geometry"):
    with open(filename, 'w') as f:
        f.write(f"{len(symbols)}\n{comment}\n")
        for sym, xyz in zip(symbols, coords):
            f.write(f"{sym} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}\n")

def export_xyz_trajectory(filename, symbols, trajectory):
    with open(filename, 'w') as f:
        for i, coords in enumerate(trajectory):
            f.write(f"{len(symbols)}\nStep {i+1}\n")
            for sym, xyz in zip(symbols, coords):
                f.write(f"{sym} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}\n")
    print(f'XYZ trajectory saved as {filename}')

def optimize_geometry(xyz_file, charge=0, basis='sto-3g', conv_tol=1e-4, max_steps=100):
    atomstr = xyz_to_atomstr(xyz_file)
    mol = gto.Mole()
    mol.atom = atomstr
    mol.charge = charge
    mol.basis = basis
    mol.build()
    n_atoms = mol.natm
    coords0 = mol.atom_coords().flatten()
    energies = []
    trajectory = []
    symbols = [mol.atom_symbol(i) for i in range(n_atoms)]

    def energy_and_grad(flat_coords):
        mol.set_geom_(flat_coords.reshape((n_atoms, 3)), unit='Bohr')
        mf = scf.RHF(mol)
        mf.kernel()
        e = mf.e_tot
        g = grad.RHF(mf).kernel().flatten()
        energies.append(e)
        trajectory.append(mol.atom_coords().copy())
        return e, g

    def fun(flat_coords):
        e, _ = energy_and_grad(flat_coords)
        return e

    def jac(flat_coords):
        _, g = energy_and_grad(flat_coords)
        return g

    result = minimize(fun, coords0, jac=jac, method='BFGS', tol=conv_tol, options={'maxiter': max_steps, 'disp': True})
    mol.set_geom_(result.x.reshape((n_atoms, 3)), unit='Bohr')
    coords = mol.atom_coords()
    save_xyz('optimized.xyz', symbols, coords, comment="Optimized geometry from PySCF")
    print("\nOptimized geometry saved to optimized.xyz")
    print("Optimized geometry (Bohr):")
    for i, xyz in enumerate(coords):
        print(f"{symbols[i]} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}")
    print(f"Final energy: {result.fun:.6f} a.u.")
    if result.success:
        print("Geometry optimization converged.")
    else:
        print("Geometry optimization did not converge.")
    # Export XYZ trajectory for visualization
    export_xyz_trajectory('geometry_trajectory.xyz', symbols, trajectory)

if __name__ == "__main__":
    xyz_file = sys.argv[1] if len(sys.argv) > 1 else 'h2.xyz'
    charge = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    basis = sys.argv[3] if len(sys.argv) > 3 else 'sto-3g'
    optimize_geometry(xyz_file, charge, basis)
