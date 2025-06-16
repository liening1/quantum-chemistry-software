# Quantum Chemistry Software

A modular, extensible quantum chemistry framework in Python with visualization capabilities.

## Features

- **Hartree-Fock SCF Implementation**: A modular implementation of the Self-Consistent Field method
- **Geometry Optimization**: Using PySCF for gradients and SciPy for BFGS optimization
- **Visualization**:
  - Molecular structure visualization (matplotlib)
  - SCF convergence plots
  - Geometry optimization trajectory visualization (interactive HTML/3Dmol.js)
  - Multiple visualization options (matplotlib, py3Dmol, offline HTML Canvas)

## Project Structure

- `main.py`: Main entry point for Hartree-Fock calculations
- `molecule.py`: Molecule class and XYZ file handling
- `integrals.py`: Integral calculation utilities 
- `scf.py`: Self-Consistent Field implementation
- `utils.py`: Utility functions for various calculations
- `optimize_geometry.py`: Geometry optimization using PySCF and SciPy
- `plot_scf.py`: Plotting utilities for SCF convergence
- Visualization scripts:
  - `visualize_xyz.py`: Static 3D visualization of molecules
  - `visualize_trajectory.py`: Visualization of geometry optimization trajectories 
  - `visualize_trajectory_py3dmol.py`: Interactive 3D trajectory visualization with py3Dmol/3Dmol.js

## Usage

### Basic Hartree-Fock Calculation

```bash
python main.py h2.xyz
```

### Geometry Optimization

```bash
python optimize_geometry.py h2.xyz
```

### Trajectory Visualization (py3Dmol)

```bash
python visualize_trajectory_py3dmol.py geometry_trajectory.xyz
```

## Visualization Options

1. **Static 3D Visualization**: `visualize_xyz.py` - Creates static 3D plots using matplotlib
2. **Trajectory Animation**: `visualize_trajectory.py` - Creates animated GIFs of geometry optimization
3. **Interactive 3D Visualization**: `visualize_trajectory_py3dmol.py` - Interactive HTML/JS visualization with controls