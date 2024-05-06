# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import subprocess
import re

import util

ZOKRATES_EXPECTED_VERSION = "0.8.8"

class Zokrates:
    @staticmethod
    def check_version():
        try:
            process = subprocess.Popen(['zokrates', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return_code = process.wait()
            stdout, stderr = process.communicate()

            if return_code == 0:
                pattern = r'\d+\.\d+\.\d+'
                result = re.findall(pattern, stdout.decode())[0]

                major, minor, patch = [int(n) for n in result.split('.')]
                exp_major, exp_minor, exp_patch = [int(n) for n in ZOKRATES_EXPECTED_VERSION.split('.')]

                if major > exp_major or minor < exp_minor:
                    util.eprint(f"Current Zokrates version ({result}) is incompatible -- expected 0.8.8")
            else:
                util.eprint("The 'zokrates' command did not succeed. Do you have it installed?")
        except Exception as e:
            util.eprint("Failed to detect Zokrates version:", e)

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
