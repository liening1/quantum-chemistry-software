class Molecule:
    def __init__(self, atoms, charge=0):
        self.atoms = atoms
        self.charge = charge
        self.symbol_to_Z = {
            'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
            'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18,
            'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30
        }
        self.n_electrons = sum(self.symbol_to_Z[symbol] for symbol, _ in atoms) - charge

    def get_nuclear_coords(self):
        return [coords for _, coords in self.atoms]

    def get_atomic_numbers(self):
        return [self.symbol_to_Z[symbol] for symbol, _ in self.atoms]

def load_molecule(filename, charge=0):
    atoms = []
    with open(filename, 'r') as f:
        lines = f.readlines()[2:]  # Skip first two lines in XYZ
        for line in lines:
            parts = line.split()
            atoms.append((parts[0], [float(parts[1]), float(parts[2]), float(parts[3])]))
    return Molecule(atoms, charge=charge)
