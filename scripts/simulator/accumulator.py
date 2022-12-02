import sys
sys.path.append("RSA-accumulator/")
import main as RSA
import helpfunctions as RSAhelper
import hashlib
import random
import time
import math


# we do not have int_to_kv because only digests are recorded on-chain
# actual contents are kept by each Dapp where digests are used for verification
def kv_to_int(addr, val):
    return int.from_bytes(hashlib.sha256('{}:{}'.format(addr, val).encode('utf-8')).digest(), byteorder = 'big')


# Get default digest and initial witness caches will take a long time which will only perform once
def default_RSA_digest(txns, state_num, cache_num):
    # states are in the k:v format but converted into integers
    states = []
    # txn: operation, usertable, address, update value (for update only)
    for i in range(len(txns)):
        addr = txns[i].split(' ')[2]
        val = '{}-{}'.format(addr, i).encode('utf-8')          # suppose currently the state value = its addr-id
        states.append(kv_to_int(addr, val))
    if state_num > len(states):
        for _ in range(state_num - len(states)):
            states.append(kv_to_int(random.getrandbits(256), random.getrandbits(256)))

    n, A0, S = RSA.setup()

    start_time = time.time()
    # # Validate if needed
    # A_post_add, nipoe = RSA.batch_add(A0, S, states, n)
    # nonces_list = list(map(lambda e: RSAhelper.hash_to_prime(e)[1], states))
    # is_valid = RSA.batch_verify_membership_with_NIPoE(nipoe[0], nipoe[1], A0, states, nonces_list, A_post_add, n)
    # assert(is_valid)

    witness_caches = []

    cache_size = math.ceil(state_num/cache_num)
    other_states_in_cache = []

    for i in range(cache_num):
        lower = i*cache_size
        upper = (i+1)*cache_size
        cache_states = [x for  j, x in enumerate(states) if j<lower or j>= upper]
        gap = (i + 1) * cache_size - len(txns)
        if gap > 0 and gap < cache_size:
            other_states_in_cache = [x for  j, x in enumerate(states) if j >= upper - gap and j < upper]
        S.clear()
        cache, nipoe = RSA.batch_add(A0, S, cache_states, n)
        acc_prime = 1
        for state in cache_states:
            acc_prime *= RSAhelper.hash_to_prime(state, RSA.ACCUMULATED_PRIME_SIZE)[0]
        witness_caches.append((cache, acc_prime))
        
    A_post_add, nipoe = RSA.batch_add(witness_caches[-1][0], S, states[-cache_size:], n)
    print('Witness cache initialization time cost: {}'.format(time.time() - start_time))

    other_state_prime = 1
    for state in other_states_in_cache:
        other_state_prime *= RSAhelper.hash_to_prime(state, RSA.ACCUMULATED_PRIME_SIZE)[0]
    return A_post_add, n, S, witness_caches, cache_size, other_state_prime


def accumulate_Dt(addr, val):
    hash_prime, nonce = RSAhelper.hash_to_prime(kv_to_int(addr, val), RSA.ACCUMULATED_PRIME_SIZE)
    return hash_prime


def shamir_trick(wit1, wit2, prime1, prime2, n):
    return RSAhelper.shamir_trick(wit1, wit2, prime1, prime2, n)


if __name__ == '__main__':
    a = int.from_bytes(hashlib.sha256('test:1'.encode('utf-8')).digest(), byteorder = 'big')
    b = int.from_bytes(hashlib.sha256('test'.encode('utf-8')).digest(), byteorder = 'big')
    print(RSAhelper.hash_to_prime(a, 128))
    print(RSAhelper.hash_to_prime(b, 128))
    print(random.getrandbits(256))
