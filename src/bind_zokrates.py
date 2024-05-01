# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import subprocess
import re

class Zokrates:
    @staticmethod
    def get_constraint_count(filename):
        """
        Run command "zokrates inspect -i <filename>", returns the number of constraints 
        if successful or raises an Exception on command failure
        """
        process = subprocess.Popen(['zokrates', 'inspect', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return_code = process.wait()
        stdout, stderr = process.communicate()

        if return_code == 0:
            match = re.search(r'constraint_count:\s*(\d+)', stdout.decode())
            constraint_count = int(match.group(1))

            return constraint_count
        else:
            raise Exception("Failed to extract constraint count from ", filename)

    @staticmethod
    def verify_proof(filename):
        # TODO
        pass

    @staticmethod
    def generate_proof(filename):
        # TODO
        pass
    