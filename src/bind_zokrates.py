# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import subprocess
import re
import os
import json

import util

ZOKRATES_EXPECTED_VERSION = "0.8.8"
CIRCUIT_PATH = os.path.join(os.path.dirname(__file__), "circuit/")

class Zokrates:
    @staticmethod
    def prepare_circuits() -> dict:
        util.vprint("Circuits: Detecting circuits...")

        result = {}

        for directory in os.listdir(CIRCUIT_PATH):
            subfolder = os.path.join(CIRCUIT_PATH, directory)

            zokrates_files = util.find_files_with_extension(subfolder, ".zok")

            if len(zokrates_files) == 0:
                util.wprint(f"Circuits: Expected to find a single Zokrates (.zok) file in subfolder {directory}, but found zero, ignoring directory")
                continue
            elif len(zokrates_files) > 1:
                util.wprint(f"Circuits: Expected to find a single Zokrates (.zok) file in subfolder {directory}, but found multiple, ignoring directory")
                continue

            zokrates_filepath = os.path.join(subfolder, zokrates_files[0])
            circuit_filepath = os.path.join(subfolder, "out")
            proving_key_filepath = os.path.join(subfolder, "proving.key")
            verification_key_filepath = os.path.join(subfolder, "verification.key")
            abi_filepath = os.path.join(subfolder, "abi.json")

            try:
                assert os.path.exists(circuit_filepath), "circuit"
                assert os.path.exists(proving_key_filepath), "proving key"
                assert os.path.exists(verification_key_filepath), "verification key"
                assert os.path.exists(abi_filepath), "ABI"
            except AssertionError as e:
                util.wprint(f"Circuits: Expected to find {e} file in subfolder {directory}, ignoring directory")

            file_hash : str = util.get_file_hash(zokrates_filepath)

            result[file_hash] = subfolder

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
    def get_constraint_count(circuit_folder : str) -> int:
        """
        Run command "zokrates inspect -i <filename>" and return the number of constraints
        if successful or raises an Exception on command failure
        """
        circuit_filepath = os.path.join(circuit_folder, "out")

        process = subprocess.Popen(['zokrates', 'inspect', '-i', circuit_filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()
        stdout, stderr = process.communicate()

        if return_code == 0:
            match = re.search(r'constraint_count:\s*(\d+)', stdout.decode())
            constraint_count = int(match.group(1))

            return constraint_count
        else:
            raise Exception("Failed to extract constraint count from", circuit_folder)

    @staticmethod
    def verify_proof(block_metadata : str, circuit_folder : str, proof : str, parameters : str) -> bool:
        #   1. Write proof to a temp file
        temp_file = os.path.join(circuit_folder, 'temp')

        proof_json = json.loads(proof)

        # check the block metadata integrity
        assert int(proof_json['inputs'][-2], 0) == int(block_metadata)

        # TODO: Verify proof parameters
        for i in range(len(proof_json['inputs']) - 2):
            pass

        with open(temp_file, 'w') as file:
            file.write(proof)

        #   2. Verify proof
        process = subprocess.Popen(['zokrates', 'verify', '-j', temp_file, '-v', os.path.join(circuit_folder, 'verification.key')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()
        stdout, stderr = process.communicate()

        #   3. Delete temp proof file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        print("return code", stdout)

        #   4. Return result
        return return_code == 0

    @staticmethod
    def generate_proof(block_metadata : str, circuit_folder : str, parameters : str) -> str:
        circuit_filepath = os.path.join(circuit_folder, "out")
        abi_filepath = os.path.join(circuit_folder, "abi.json")
        proving_key_filepath = os.path.join(circuit_folder, "proving.key")
        witness_filepath = os.path.join(circuit_folder, "witness")
        circom_witness_filepath = os.path.join(circuit_folder, "out.wtns")
        proof_filepath = os.path.join(circuit_folder, "proof.json")

        process = subprocess.Popen(['zokrates', 'compute-witness', '-i', circuit_filepath, '-s', abi_filepath, '-o', witness_filepath, '--circom-witness', circom_witness_filepath, '-a', *parameters.split(" "), block_metadata], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()

        if return_code != 0:
            raise Exception(f"Failed to compute witness for circuit {circuit_folder}")

        process = subprocess.Popen(['zokrates', 'generate-proof', '-i', circuit_filepath, '-p', proving_key_filepath, '-w', witness_filepath, '-j', proof_filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()

        if return_code != 0:
            raise Exception(f"Failed to generate proof for circuit {circuit_folder}")

        proof = None

        with open(proof_filepath, "r") as proof_file:
            proof = proof_file.read()

        if os.path.exists(witness_filepath):
            os.remove(witness_filepath)

        if os.path.exists(circom_witness_filepath):
            os.remove(circom_witness_filepath)

        if os.path.exists(proof_filepath):
            os.remove(proof_filepath)

        return proof
