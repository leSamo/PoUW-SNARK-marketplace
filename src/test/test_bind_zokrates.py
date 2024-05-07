# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from bind_zokrates import Zokrates, CIRCUIT_PATH

def test_get_constraint_count():
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), "misc/out")) == 2

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
