import matplotlib.pyplot as plt

def plot_scf_convergence(energies):
    plt.figure(figsize=(6,4))
    plt.plot(range(1, len(energies)+1), energies, marker='o')
    plt.xlabel('Iteration')
    plt.ylabel('Electronic Energy (a.u.)')
    plt.title('SCF Convergence')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('scf_convergence.png')
    print('SCF convergence plot saved as scf_convergence.png')
