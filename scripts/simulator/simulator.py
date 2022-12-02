# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: XU Zihuan
import yaml
from pathlib import Path
from structures import L1MerTxn, L1SpltTxn, Block
from enclave import txn_simulation, txn_execution
from dappnode import gen_split_txn, gen_mer_txn, update_RSA_witness
from validator import validate_split, validate_merge
from accumulator import default_RSA_digest
import time
import sys
import pickle
from functools import wraps
from subprocess import Popen, PIPE
import os
DEVNULL = open(os.devnull, 'wb')

VALIDATOR_START_PORT = 4321
DAPPNODE_START_PORT = 5432
MIN_RPS = 10
MAX_RPS = 40000

def memoize(fileName):
    def doMemoize(func):
        if os.path.exists(fileName):
            with open(fileName) as f:
                cache = pickle.load(f)
        else:
            cache = {}
        @wraps(func)
        def wrap(*args):
            if args not in cache:
                cache[args] = func(*args)
                with open(fileName, 'wb') as f:
                    pickle.dump(cache, f)
            return cache[args]
        return wrap
    return doMemoize


def validators_consensus(validator_num, txns):
    dumped_txns = str(pickle.dumps(txns))

    cmd = [sys.executable, 'validator.py']
    validator_processes = []
    validator_addrs = []
    for i in range(validator_num):
        validator_addrs.append('localhost:%d' % (VALIDATOR_START_PORT + i))
    
    # block proposer
    addrs = list(validator_addrs)
    selfAddr = addrs.pop()
    p = Popen(cmd + [dumped_txns] + [selfAddr] + addrs, stdin=PIPE)
    validator_processes.append(p)
    # other validators
    for i in range(validator_num - 1):
        addrs = list(validator_addrs)
        selfAddr = addrs.pop(i)
        p = Popen(cmd + ['validate-only'] + [selfAddr] + addrs, stdin=PIPE)
        # validator_processes.append(p)
    
    delays = []
    for p in validator_processes:
        p.communicate()
        delays.append(float(p.returncode) / 100.0)
    avgDelay = sum(delays) / len(delays)
    print('average validator consensus delay:', avgDelay)


def dapp_nodes_consensus(dapp_num, dapp_node_num, txns_for_each_dapp):
    proposer_processes = []
    
    for i in range(dapp_num):
        dumped_txns = str(pickle.dumps(txns_for_each_dapp[i]))
        cmd = [sys.executable, 'dappnode.py']
        dappnode_addrs = []
        for j in range(dapp_node_num):
            dappnode_addrs.append('localhost:%d' % (DAPPNODE_START_PORT + i * dapp_node_num + j))

        # txn proposer
        addrs = list(dappnode_addrs)
        selfAddr = addrs.pop()
        p = Popen(cmd + [dumped_txns] + [selfAddr] + addrs, stdin=PIPE)
        proposer_processes.append(p)
        # other dapp nodes
        for i in range(dapp_node_num - 1):
            addrs = list(dappnode_addrs)
            selfAddr = addrs.pop(i)
            p = Popen(cmd + ['validate-only'] + [selfAddr] + addrs, stdin=PIPE)
    
    delays = []
    for p in proposer_processes:
        p.communicate()
        delays.append(float(p.returncode) / 100.0)
    avgDelay = sum(delays) / len(delays)
    print('average dapp node consensus delay:', avgDelay)


if __name__ == '__main__':
    cfg_file_path = Path('cfgs/config.yaml')
    root_path = Path('../../')

    if cfg_file_path.exists():
        with open(cfg_file_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    else:
        with open('cfgs/config.yaml', encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

    validator_num = cfg['Validators']
    dapp_num = cfg['DApps']
    dapp_node_num = cfg['DAppNodes']

    # load and distribute workloads
    workload = root_path/'workloads'/'ycsb'/'{}.txt'.format(cfg['workload'])
    txn_num = cfg['txn_count']
    txns = []
    with open(workload, encoding="utf-8") as f:
        counter = 0
        drift = 0
        while(counter<txn_num):
            t = f.readline()
            if t.startswith('READ') or t.startswith('UPDATE'):
                txns.append(t)
                counter += 1
            elif t == '':
                txns.append(txns[drift])
                drift += 1
                counter += 1
    # print(txns)

    # ------------------------------------------------------------
    #  layer-2 processing
    # ------------------------------------------------------------

    # collect transactions (workload)
    txns_for_each_Dapp = []
    count = int(txn_num/dapp_num)
    for i in range(dapp_num):
        txns_for_each_Dapp.append(txns[i*count:(i+1)*count])
    
    # ------------------------------------------------------------
    #  layer-2 TXN batch consensus
    # ------------------------------------------------------------
    dapp_nodes_consensus(dapp_num, dapp_node_num, txns_for_each_Dapp)

    # simulate batch in the enclave (test for one DApp node only)
    batch_size = cfg['L2_batch_size']
    start_time = time.time()
    rw_set, tee_sim_sig = txn_simulation(txns_for_each_Dapp[0][:batch_size])
    print('L2 TXN Simulation Time Cost: {}'.format(time.time()-start_time))

    # split the RSA accumulator and create the split layer-1 transaction (test for one DApp node in one batch only)
    current_RSA_digest, n, S, witness_caches, cache_size, other_state_prime = default_RSA_digest(txns_for_each_Dapp[0][:batch_size], cfg['state_count'], cfg['witness_cache_count'])
    start_time = time.time()
    pre_RSA_digest = current_RSA_digest
    splt, current_RSA_digest = gen_split_txn(txns_for_each_Dapp[0][:batch_size], tee_sim_sig, witness_caches, cache_size, other_state_prime, n)
    print('Gen Splt TXN Time Cost: {}'.format(time.time()-start_time))

    # ------------------------------------------------------------
    #  layer-1 SpltTXN consensus (with additional dummy L1 TXNs)
    # ------------------------------------------------------------
    block_size = cfg['block_size']
    splt_txns = [splt]
    for _ in range(block_size - 1):
        splt_txns.append(L1SpltTxn(1, 'dummy'.encode('utf-8'), 'dummy', 1, 'dummy'))
    
    start_time = time.time()
    validate_split(splt, pre_RSA_digest, n)
    print('Splt TXN Validation Time Cost: {}'.format(time.time()-start_time))
    start_time = time.time()
    block_with_splt =  Block('dummy_proof', splt_txns)
    print('L1 Block Generation Time Cost: {}'.format(time.time()-start_time))

    validators_consensus(validator_num, splt_txns)

    # L2 execution in the enclave (test for one DApp node only)
    start_time = time.time()
    upd_primes, updated_Dt, tee_exe_sig = txn_execution(txns_for_each_Dapp[0][:batch_size], block_with_splt, cache_size)
    print('L2 TXN Execution Time Cost: {}'.format(time.time()-start_time))

    # generate the merge layer-1 transaction (test for one DApp node only)
    start_time = time.time()
    mer = gen_mer_txn(block_with_splt, 0, updated_Dt, tee_exe_sig)
    print('Gen Mer TXN Time Cost: {}'.format(time.time()-start_time))

    # ------------------------------------------------------------
    #  layer-1 MerTXN consensus (with additional dummy L1 TXNs)
    # ------------------------------------------------------------
    mer_txns = [mer]
    for _ in range(block_size - 1):
        mer_txns.append(L1MerTxn(1, 'dummy'.encode('utf-8'), 'dummy', 'dummy'))
    
    start_time = time.time()
    current_RSA_digest = validate_merge(mer, 0, block_with_splt, current_RSA_digest, n)
    print('Mer TXN Validation Time Cost: {}'.format(time.time()-start_time))
    validators_consensus(validator_num, mer_txns)

    # L2 RSA witness update
    start_time = time.time()
    update_RSA_witness(witness_caches, cache_size, batch_size, splt, upd_primes, other_state_prime, n)
    print('Witness Update Time Cost: {}'.format(time.time()-start_time))
