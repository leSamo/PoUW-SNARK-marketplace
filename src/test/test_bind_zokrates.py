# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from bind_zokrates import Zokrates

def test_get_constraint_count():
    assert Zokrates.get_constraint_count(os.path.join(os.path.dirname(__file__), "misc/out")) == 2
