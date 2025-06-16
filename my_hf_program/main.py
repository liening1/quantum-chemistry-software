from molecule import load_molecule
from integrals import get_integrals
from scf import run_scf
from utils import compute_nuclear_repulsion

try:
    from plot_scf import plot_scf_convergence
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

import sys

def main():
    # Usage: python main.py [xyz_file] [charge] [basis]
    xyz_file = 'h2.xyz'
    charge = 0
    basis = 'sto-3g'
    if len(sys.argv) > 1:
        xyz_file = sys.argv[1]
    if len(sys.argv) > 2:
        charge = int(sys.argv[2])
    if len(sys.argv) > 3:
        basis = sys.argv[3]
    mol = load_molecule(xyz_file, charge=charge)
    S, T, V, ERI = get_integrals(mol, basis=basis)
    E_elec, energies = run_scf(S, T, V, ERI, mol, return_energies=True)
    E_nuc = compute_nuclear_repulsion(mol)
    print(f"Nuclear Repulsion Energy: {E_nuc:.6f} a.u.")
    print(f"Total Hartree-Fock Energy: {E_elec + E_nuc:.6f} a.u.")
    if HAS_PLOT:
        plot_scf_convergence(energies)
    else:
        print("matplotlib not installed: skipping SCF convergence plot.")

if __name__ == "__main__":
    main()
