import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Simple covalent radii (in Angstroms) for common elements
COVALENT_RADII = {
    'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57, 'P': 1.07, 'S': 1.05, 'Cl': 1.02,
    'Br': 1.20, 'I': 1.39, 'He': 0.28, 'Ne': 0.58, 'Ar': 1.06, 'Li': 1.28, 'Be': 0.96,
    'B': 0.85, 'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11
}
# Simple color map for elements
ATOM_COLORS = {
    'H': 'white', 'C': 'black', 'N': 'blue', 'O': 'red', 'F': 'green', 'P': 'orange', 'S': 'yellow', 'Cl': 'green',
    'Br': 'brown', 'I': 'purple', 'He': 'cyan', 'Ne': 'cyan', 'Ar': 'cyan', 'Li': 'violet', 'Be': 'darkgreen',
    'B': 'salmon', 'Na': 'violet', 'Mg': 'darkgreen', 'Al': 'gray', 'Si': 'gray'
}

def read_xyz(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    n_atoms = int(lines[0])
    atoms = []
    coords = []
    for line in lines[2:2+n_atoms]:
        parts = line.split()
        atoms.append(parts[0])
        coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return atoms, np.array(coords)

def plot_xyz(filename, title=None, savefig=True):
    atoms, coords = read_xyz(filename)
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    # Draw bonds
    for i in range(len(atoms)):
        for j in range(i+1, len(atoms)):
            r1 = coords[i]
            r2 = coords[j]
            d = np.linalg.norm(r1 - r2)
            rad1 = COVALENT_RADII.get(atoms[i], 0.7)
            rad2 = COVALENT_RADII.get(atoms[j], 0.7)
            if d < 1.2 * (rad1 + rad2):  # Simple bond threshold
                ax.plot([r1[0], r2[0]], [r1[1], r2[1]], [r1[2], r2[2]], color='gray', linewidth=2, alpha=0.7)
    # Draw atoms
    for i, (atom, xyz) in enumerate(zip(atoms, coords)):
        color = ATOM_COLORS.get(atom, 'magenta')
        ax.scatter(*xyz, s=200, c=color, edgecolors='k', label=atom if i == atoms.index(atom) else "")
        ax.text(*xyz, f'{atom}', fontsize=12, ha='center', va='center')
    ax.set_xlabel('X (Angstrom)')
    ax.set_ylabel('Y (Angstrom)')
    ax.set_zlabel('Z (Angstrom)')
    if title:
        ax.set_title(title)
    # Only show unique legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    plt.tight_layout()
    if savefig:
        plt.savefig('geometry_3d.png')
        print('3D geometry plot saved as geometry_3d.png')
    # plt.show()  # Uncomment if running locally with GUI

if __name__ == "__main__":
    # Only use the first argument after the script name as the xyz file
    if len(sys.argv) > 1:
        xyz_file = sys.argv[1]
    else:
        xyz_file = 'optimized.xyz'
    plot_xyz(xyz_file, title=f'3D Structure: {xyz_file}')
