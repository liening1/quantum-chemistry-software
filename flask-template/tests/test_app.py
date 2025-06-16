import numpy as np
# import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from app import app as flask_app
from molecule import Molecule
from scf import run_scf


@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_run_scf_returns_energy():
    # Minimal H2 molecule mock
    atoms = [('H', [0.0, 0.0, 0.0]), ('H', [0.74, 0.0, 0.0])]
    mol = Molecule(atoms)
    # Mock integrals (same as in integrals.py)
    S = np.array([[1.0, 0.2], [0.2, 1.0]])
    T = np.array([[1.0, 0.0], [0.0, 1.0]])
    V = np.array([[-1.0, -0.2], [-0.2, -1.0]])
    ERI = np.zeros((2, 2, 2, 2))
    ERI[0, 0, 0, 0] = 0.7
    ERI[0, 0, 1, 1] = 0.6
    ERI[1, 1, 0, 0] = 0.6
    ERI[1, 1, 1, 1] = 0.7

    energy = run_scf(S, T, V, ERI, mol)
    assert isinstance(energy, float)
