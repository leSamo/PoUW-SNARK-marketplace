# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import subprocess
import re
import os

import util

ZOKRATES_EXPECTED_VERSION = "0.8.8"
CIRCUIT_PATH = "circuit/"
ZOKRATES_EXTENSION = ".zok"

class Zokrates:
    @staticmethod
    def prepare_circuits() -> dict:
        util.vprint("Circuits: Detecting circuits...")

        result = {}

        for root, dirs, _ in os.walk(CIRCUIT_PATH):
            for directory in dirs:
                subfolder = os.path.join(root, directory)

                zokrates_files = util.find_files_with_extension(subfolder, ZOKRATES_EXTENSION)

                if len(zokrates_files) == 0:
                    util.wprint(f"Circuits: Expected to find a single Zokrates (.zok) file in subfolder {directory}, but found zero, ignoring directory")
                    continue
                elif len(zokrates_files) > 1:
                    util.wprint(f"Circuits: Expected to find a single Zokrates (.zok) file in subfolder {directory}, but found multiple, ignoring directory")
                    continue

                process = subprocess.Popen(['zokrates', 'compile', '-i', zokrates_files[0]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                return_code = process.wait()

                # TODO: skip if exists
                if return_code != 0:
                    util.wprint(f"Circuits: Failed to compile circuit in subfolder {directory}, ignoring directory")
                    continue

                file_hash : str = util.get_file_hash(zokrates_files[0])
                #constraint_count = Zokrates.get_constraint_count(os.path.join(subfolder, 'out'))

                # TODO: skip if exists
                process = subprocess.Popen(['zokrates', 'setup', '-e', file_hash], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                return_code = process.wait()

                if return_code != 0:
                    util.wprint(f"Circuits: Failed to perform key setup in subfolder {directory}, ignoring directory")
                    continue

                result[file_hash] = os.path.join(subfolder, 'out')

        return result

    @staticmethod
    def check_version() -> None:
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
    def get_constraint_count(filename : str) -> int:
        """
        Run command "zokrates inspect -i <filename>" and return the number of constraints
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
            raise Exception("Failed to extract constraint count from", filename)

    @staticmethod
    def verify_proof() -> bool:
        # TODO
        pass

    @staticmethod
    def generate_proof(circuit_path : str, parameters : str) -> bytes:
        process = subprocess.Popen(['zokrates', 'compute-witness', '-i', circuit_path, '-a', parameters], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()

        if return_code != 0:
            util.wprint(f"Circuits: Failed to compute-witness for circuit {circuit_path}")
            raise Exception("Failed to generate proof")

        process = subprocess.Popen(['zokrates', 'generate-proof', '-i', circuit_path, '-p', '???', '-w', '???'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()

        if return_code != 0:
            util.wprint(f"Circuits: Failed to generate-proof for circuit {circuit_path}")
            raise Exception("Failed to generate proof")

        # return proof
