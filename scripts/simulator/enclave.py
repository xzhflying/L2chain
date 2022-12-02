from structures import Block
import sys
sys.path.append("RSA-accumulator/")
from main import ACCUMULATED_PRIME_SIZE
from helpfunctions import generate_large_prime
from math import ceil
import pickle
import os
import subprocess
from hashlib import sha256
from accumulator import accumulate_Dt

CACHE_SIZE = None

def txn_simulation(txns):
    dumped_txns = str(pickle.dumps(txns))

    os.chdir("enclave/untrusted")

    cmd = ["cargo run -- sim {}".format(dumped_txns)]

    # activate a subprocess to run the rust enclave codes
    return_value = subprocess.call(cmd, shell=True)

    os.chdir("../../")

    if len(return_value) != 2:
        print("SGX simulation fails with the output: {}".format(return_value))
        rw_set, tee_sig = [], 'test'.encode('utf-8')
    else:
        _, rw_set, tee_sig = return_value
    return rw_set, tee_sig


def txn_execution(txns, block: Block, cache_size):
    block_proof = block.get_proof()
    block_content = block.get_block_content_without_proof()
    block_hash = block.get_block_hash()
    offset, splt_mkt_path = block.get_txn_membership_path(0)
    
    if not block.txn_membership_proof(offset, splt_mkt_path):
        print("Miss match of the splt txn in the execution phase!")
        return

    CACHE_SIZE = cache_size
    
    dumped_txns = str(pickle.dumps(txns))

    os.chdir("enclave/untrusted")

    cmd = ["cargo run -- exe {} {} {} {}".format(dumped_txns, block_proof, block_content, block_hash)]

    # activate a subprocess to run the rust enclave codes
    return_value = subprocess.call(cmd, shell=True)

    os.chdir("../../")

    if len(return_value) != 3:
        print("SGX execution fails with the output: {}".format(return_value))
        upd_cache_primes, updated_Dt, tee_sig = [], 'test'.encode('utf-8')
    else:
        _, upd_cache_primes, updated_Dt, tee_sig  = return_value
    return upd_cache_primes, updated_Dt, tee_sig

# Following functions are called by enclaves

def dumps_helper(content):
    return str(pickle.dumps(content))


def loads_helper(content):
    return pickle.loads(content)


def block_proof_verification(proof, content, block_hash):
    return block_hash == sha256(content + pickle.dumps(proof)).hexdigest()


# A simple simulation of obtaining read/write sets
def simulate_txns(dumped_txns):
    txns = pickle.loads(dumped_txns)
    rw_set = []
    for i in range(len(txns)):
        addr = txns[i].split(' ')[2]
        rw_set.append(addr)
    return rw_set

# A simple simulation of state update
def execute_txns(dumped_txns):
    txns = pickle.loads(dumped_txns)

    upd_state_count = len(txns)
    upd_cache_primes = []
    for _ in range(int(ceil(upd_state_count/CACHE_SIZE))):
        upd_cache_primes.append(generate_large_prime(ACCUMULATED_PRIME_SIZE))
    updated_Dt = 1
    for primes in upd_cache_primes:
        updated_Dt *= primes
    return upd_cache_primes, updated_Dt
