import numpy as np

try:
    from pyscf import gto, scf as pyscf_scf
    HAS_PYSCF = True
except ImportError:
    HAS_PYSCF = False

def get_integrals(mol, basis='sto-3g'):
    if not HAS_PYSCF:
        # Fallback: H2 minimal basis mock
        S = np.array([[1.0, 0.2], [0.2, 1.0]])
        T = np.array([[1.0, 0.0], [0.0, 1.0]])
        V = np.array([[-1.0, -0.2], [-0.2, -1.0]])
        ERI = np.zeros((2, 2, 2, 2))
        ERI[0, 0, 0, 0] = 0.7
        ERI[0, 0, 1, 1] = 0.6
        ERI[1, 1, 0, 0] = 0.6
        ERI[1, 1, 1, 1] = 0.7
        print('PySCF not installed: using mock integrals for H2.')
        return S, T, V, ERI

    # Build PySCF molecule from mol object
    atom_str = ''
    for symbol, coords in mol.atoms:
        atom_str += f"{symbol} {' '.join(str(x) for x in coords)}; "
    atom_str = atom_str.strip()
    pyscf_mol = gto.Mole()
    pyscf_mol.atom = atom_str
    pyscf_mol.charge = mol.charge
    pyscf_mol.spin = (mol.n_electrons % 2)  # 0 for closed shell, 1 for open shell
    pyscf_mol.basis = basis
    pyscf_mol.build()

    S = pyscf_mol.intor('int1e_ovlp')
    T = pyscf_mol.intor('int1e_kin')
    V = pyscf_mol.intor('int1e_nuc')
    ERI = pyscf_mol.intor('int2e')
    # ERI is (nbf, nbf, nbf, nbf)
    return S, T, V, ERI
