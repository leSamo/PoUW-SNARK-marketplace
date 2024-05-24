# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import os
import sys
import pytest
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from bind_zokrates import Zokrates, CIRCUIT_PATH
import util

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
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a')) == 3
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'b')) == 55
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'c')) == 761

def test_prepare_circuits():
    for directory in os.listdir(CIRCUIT_PATH):
            subfolder = os.path.join(CIRCUIT_PATH, directory)

            for file in os.listdir(subfolder):
                if not file.endswith(".zok") and file not in ['out', 'proving.key', 'verification.key', 'abi.json'] and os.path.isfile(os.path.join(subfolder, file)):
                    os.remove(os.path.join(subfolder, file))

    circuits = Zokrates.prepare_circuits()

    assert circuits['00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a')
    assert circuits['bc0bcd9b0e9b8f7fe9efe06ecd55bfd942873fef82dd9476365e94398da48075'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'b')
    assert circuits['7a6e42a3c43b426aad2e6062d33be7cc0650e8ea724c12574d44a740cfd63319'] == os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'c')

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

    with open(os.path.join(folder, '3.zok'), 'w') as file:
        file.write(EXAMPLE_INCORRECT_ZOKRATES)

    Zokrates.prepare_circuits()
    captured = capsys.readouterr()

    assert "Circuits: Expected to find circuit file in subfolder klmnop3, ignoring directory" in captured.out

    shutil.rmtree(folder)

def test_generate_proof():
    proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '2 2 4')

def test_verify_proof():
    circuit_folder = os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a')

    proof = Zokrates.generate_proof('1', circuit_folder, '2 2 4')

    assert Zokrates.verify_proof('1', circuit_folder, proof, '2 2 4')

    # check if temp folder and file were deleted
    assert not os.path.exists(os.path.join(circuit_folder, 'temp'))

def test_generate_proof_invalid_params():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '1')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '1 a b')

    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), 123)

def test_generate_false_proof():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a'), '2 2 3')

def test_generate_proof_invalid_folder():
    with pytest.raises(Exception):
        proof = Zokrates.generate_proof('1', os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'xyz'), '2 2 4')

def test_get_circuit_hash():
    hash = util.get_file_hash(os.path.join(os.path.dirname(__file__), CIRCUIT_PATH, 'a', 'a.zok'))

    assert hash == "00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee"

