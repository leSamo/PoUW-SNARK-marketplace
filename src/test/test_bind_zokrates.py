# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️❌
# ####################################################################################################

import os
import sys
import pytest
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from bind_zokrates import Zokrates, CIRCUIT_PATH

EXAMPLE_CORRECT_ZOKRATES = """
def main() -> bool {
    return true;
}
"""

EXAMPLE_INCORRECT_ZOKRATES = """
def main() -> bool {
    return undefined_variable;
}
"""

@pytest.fixture
def cleanup():
    # Setup code before the test
    yield

    for folder in ['klmnop1', 'klmnop2', 'klmnop3']:
        if os.path.exists(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, folder)):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, folder))

def test_get_constraint_count():
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a')) == 2
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'b')) == 54
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'c')) == 760

def test_prepare_circuits():
    for directory in os.listdir(CIRCUIT_PATH):
            subfolder = os.path.join(CIRCUIT_PATH, directory)

            for file in os.listdir(subfolder):
                if not file.endswith(".zok") and os.path.isfile(os.path.join(subfolder, file)):
                    os.remove(os.path.join(subfolder, file))

    circuits = Zokrates.prepare_circuits()

    assert circuits['f6d00f1b20054ec6660af23c8b5953ae8799ddbb8c9bd9e1808376fef65d970e'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a')
    assert circuits['94752db6f90ebd65a52a9a148d84264526d5abae2cefbd57bcee330ca6f37dc5'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'b')
    assert circuits['8bbae86aed9b439ce9dc6b553889c8e8924f3f08bb6ea26ca4c30486e959c747'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'c')

    for directory in os.listdir(CIRCUIT_PATH):
            subfolder = os.path.join(CIRCUIT_PATH, directory)

            assert os.path.exists(os.path.join(subfolder, "out"))
            assert os.path.exists(os.path.join(subfolder, "proving.key"))
            assert os.path.exists(os.path.join(subfolder, "verification.key"))

@pytest.mark.usefixtures('cleanup')
def test_prepare_circuits_empty_folder(capsys):
    folder = os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'klmnop1')
    os.makedirs(folder, exist_ok=True)

    Zokrates.prepare_circuits()
    captured = capsys.readouterr()

    assert "Circuits: Expected to find a single Zokrates (.zok) file in subfolder klmnop1, but found zero, ignoring directory" in captured.out

    os.rmdir(folder)

@pytest.mark.usefixtures('cleanup')
def test_prepare_circuits_multiple_zokrates(capsys):
    folder = os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'klmnop2')
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, '1.zok'), 'w') as file:
        file.write(EXAMPLE_CORRECT_ZOKRATES)

    with open(os.path.join(folder, '2.zok'), 'w') as file:
        file.write(EXAMPLE_CORRECT_ZOKRATES)

    Zokrates.prepare_circuits()
    captured = capsys.readouterr()

    assert "Circuits: Expected to find a single Zokrates (.zok) file in subfolder klmnop2, but found multiple, ignoring directory" in captured.out

    shutil.rmtree(folder)

@pytest.mark.usefixtures('cleanup')
def test_prepare_circuits_invalid_zokrates(capsys):
    folder = os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'klmnop3')
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, '1.zok'), 'w') as file:
        file.write(EXAMPLE_INCORRECT_ZOKRATES)

    Zokrates.prepare_circuits()
    captured = capsys.readouterr()

    assert "Circuits: Failed to compile circuit in subfolder klmnop3, ignoring directory" in captured.out

    shutil.rmtree(folder)

def test_generate_proof():
    proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '2 2 4')

def test_verify_proof():
    proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '2 2 4')

    assert Zokrates.verify_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), proof)

    # TODO: assert temp folder and file was deleted

def test_generate_proof_invalid_params():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '1')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '1 a b')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), 123)

def test_generate_false_proof():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '2 2 3')

def test_generate_proof_invalid_folder():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'xyz'), '2 2 4')
