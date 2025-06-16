import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio
import os

# CPK colors and radii for textbook-style chemistry visualization
CPK_COLORS = {
    'H': '#FFFFFF', 'C': '#909090', 'N': '#3050F8', 'O': '#FF0D0D', 'F': '#90E050', 'P': '#FF8000', 'S': '#FFFF30', 'Cl': '#1FF01F',
    'Br': '#A62929', 'I': '#940094', 'He': '#D9FFFF', 'Ne': '#B3E3F5', 'Ar': '#80D1E3', 'Li': '#CC80FF', 'Be': '#C2FF00',
    'B': '#FFB5B5', 'Na': '#AB5CF2', 'Mg': '#8AFF00', 'Al': '#BFA6A6', 'Si': '#F0C8A0', 'Zn': '#7D80B0', 'Cu': '#C88033',
    'Fe': '#E06633', 'Ca': '#3DFF00', 'Ti': '#BFC2C7', 'Cr': '#8A99C7', 'Mn': '#9C7AC7', 'Ni': '#50D050', 'Co': '#F090A0'
}
CPK_RADII = {
    'H': 0.25, 'C': 0.70, 'N': 0.65, 'O': 0.60, 'F': 0.50, 'P': 1.00, 'S': 1.00, 'Cl': 1.00,
    'Br': 1.15, 'I': 1.25, 'He': 0.28, 'Ne': 0.58, 'Ar': 1.06, 'Li': 1.28, 'Be': 0.96,
    'B': 0.85, 'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11, 'Zn': 1.20, 'Cu': 1.20, 'Fe': 1.20, 'Ca': 1.20,
    'Ti': 1.20, 'Cr': 1.20, 'Mn': 1.20, 'Ni': 1.20, 'Co': 1.20
}

def read_xyz_trajectory(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    trajectory = []
    symbols = []
    i = 0
    while i < len(lines):
        n_atoms = int(lines[i])
        if not symbols:
            for j in range(n_atoms):
                parts = lines[i+2+j].split()
                symbols.append(parts[0])
        coords = []
        for j in range(n_atoms):
            parts = lines[i+2+j].split()
            coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
        trajectory.append(np.array(coords))
        i += n_atoms + 2
    return symbols, trajectory

# Helper to draw spheres for atoms
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def draw_sphere(ax, center, radius, color):
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = center[0] + radius * np.cos(u) * np.sin(v)
    y = center[1] + radius * np.sin(u) * np.sin(v)
    z = center[2] + radius * np.cos(v)
    ax.plot_surface(x, y, z, color=color, shade=True, linewidth=0, antialiased=False, alpha=1.0)


def animate_trajectory(symbols, trajectory, filename='geometry_optimization.gif'):
    images = []
    n_atoms = len(symbols)
    n_steps = len(trajectory)
    temp_files = []
    for step, coords in enumerate(trajectory):
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111, projection='3d')
        # Draw bonds (thin lines)
        for i in range(n_atoms):
            for j in range(i+1, n_atoms):
                r1 = coords[i]
                r2 = coords[j]
                d = np.linalg.norm(r1 - r2)
                rad1 = CPK_RADII.get(symbols[i], 0.7)
                rad2 = CPK_RADII.get(symbols[j], 0.7)
                if d < 1.2 * (rad1 + rad2):
                    ax.plot([r1[0], r2[0]], [r1[1], r2[1]], [r1[2], r2[2]], color='gray', linewidth=1.2, alpha=0.7)
        # Draw atoms as spheres
        for i, (atom, xyz) in enumerate(zip(symbols, coords)):
            color = CPK_COLORS.get(atom, '#FF00FF')
            radius = CPK_RADII.get(atom, 0.7)
            draw_sphere(ax, xyz, radius, color)
        ax.set_xlabel('X (Bohr)')
        ax.set_ylabel('Y (Bohr)')
        ax.set_zlabel('Z (Bohr)')
        ax.set_title(f'Geometry Step {step+1}')
        ax.set_xlim([np.min(trajectory[0][:,0])-2, np.max(trajectory[0][:,0])+2])
        ax.set_ylim([np.min(trajectory[0][:,1])-2, np.max(trajectory[0][:,1])+2])
        ax.set_zlim([np.min(trajectory[0][:,2])-2, np.max(trajectory[0][:,2])+2])
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        plt.tight_layout()
        temp_file = f'_traj_frame_{step}.png'
        plt.savefig(temp_file, dpi=100)
        temp_files.append(temp_file)
        plt.close(fig)
    for temp_file in temp_files:
        images.append(imageio.imread(temp_file))
    imageio.mimsave(filename, images, duration=0.7)
    print(f'Geometry trajectory animation saved as {filename}')
    # Clean up temp files
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception:
            pass

if __name__ == "__main__":
    xyz_traj = sys.argv[1] if len(sys.argv) > 1 else 'geometry_trajectory.xyz'
    out_gif = sys.argv[2] if len(sys.argv) > 2 else 'geometry_optimization.gif'
    symbols, trajectory = read_xyz_trajectory(xyz_traj)
    animate_trajectory(symbols, trajectory, filename=out_gif)
