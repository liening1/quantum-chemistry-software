import numpy as np

def run_scf(S, T, V, ERI, mol, max_iter=50, convergence=1e-6, return_energies=False):
    H_core = T + V
    num_basis = H_core.shape[0]
    num_electrons = mol.n_electrons

    # Build orthogonalization matrix
    eigvals, eigvecs = np.linalg.eigh(S)
    S_half = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T

    D = np.zeros((num_basis, num_basis))  # Initial density matrix
    energy_old = 0.0
    energies = []

    for iteration in range(max_iter):
        # Build Fock matrix
        J = np.einsum('pqrs,rs->pq', ERI, D)  # Coulomb
        K = np.einsum('prqs,rs->pq', ERI, D)  # Exchange
        F = H_core + 2 * J - K

        # Solve Roothaan equations
        F_prime = S_half.T @ F @ S_half
        eps, C_prime = np.linalg.eigh(F_prime)
        C = S_half @ C_prime

        # Build new density matrix
        num_occ = num_electrons // 2
        C_occ = C[:, :num_occ]
        D_new = C_occ @ C_occ.T

        # Compute electronic energy
        E_elec = np.sum((D_new + D) * H_core) + np.sum((D_new + D) * (J - 0.5 * K))
        energies.append(E_elec)
        if abs(E_elec - energy_old) < convergence:
            print(f'SCF converged in {iteration+1} iterations.')
            print(f'Total Electronic Energy: {E_elec:.6f} a.u.')
            break

        D = D_new
        energy_old = E_elec
    else:
        print('SCF did not converge.')

    if return_energies:
        return E_elec, energies
    return E_elec
