# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: XU Zihuan
import time
import sys
import pickle
import ast
from pathlib import Path
import yaml
from collections import defaultdict
from pymerkle import MerkleTree
sys.path.append("../")
from pysyncobj import SyncObj, replicated, SyncObjConf, FAIL_REASON
from structures import Block, L1MerTxn, L1SpltTxn
from accumulator import accumulate_Dt, shamir_trick
from hashlib import sha256
import math

class DAppNode(SyncObj):
    cfg = SyncObjConf(
            appendEntriesUseBatch=False,
        )
    
    def __init__(self, self_node, other_nodes, **kwargs):
        SyncObj.__init__(self, self_node, other_nodes, **kwargs)
        self.__txn_pool = []
        self.__txn = '' # To be consented
        self.__txn_batch = []  # To be consented

    def add_txn_to_pool(self, txns):
        assert type(txns) == list
        self.__txn_pool += txns

    def get_txn_pool(self):
        return self.__txn_pool

    def get_txn_pool_size(self):
        return len(self.__txn_pool)

    def partition_batches(self, batch_size):
        partitioned_batches = []
        batch = []
        for txn in self.__txn_pool:
            if txn.startswith('UPDATE') and len(batch) < batch_size:
                batch.append(txn)
            elif len(batch) == batch_size:
                partitioned_batches.append(list(batch))
                batch = []
        partitioned_batches.append(list(batch))
        return partitioned_batches

    @replicated
    def set_txn(self, txn, callTime, sync = True):
        self.__txn = txn
        return (callTime, time.time())

    def get_txn(self):
        return self.__txn

    @replicated
    def set_txn_batch(self, txns, callTime, sync = True):
        self.__txn_batch = txns
        return (callTime, time.time())

    def get_txn_batch(self):
        return self.__txn_batch

_g_sent = 0
_g_success = 0
_g_error = 0
_g_errors = defaultdict(int)
_g_delays = []


def clbck(res, err):
    global _g_error, _g_success, _g_delays
    if err == FAIL_REASON.SUCCESS:
        _g_success += 1
        callTime, recvTime = res
        delay = time.time() - callTime
        _g_delays.append(delay)
    else:
        _g_error += 1
        _g_errors[err] += 1


def gen_split_txn(txns, tee_sig, witness_caches, cache_size, other_state_prime, n):
    rw_set = []
    Dt = 1
    for i in range(len(txns)):
        addr = txns[i].split(' ')[2]
        val = '{}-{}'.format(addr, i).encode('utf-8')
        rw_set.append(addr)
        Dt *= accumulate_Dt(addr, val)
    
    St = pickle.dumps(','.join(rw_set))

    Wt = witness_caches[0][0]
    acc_Dt = witness_caches[0][1]
    j = 0
    for j in range(math.ceil(len(txns)/cache_size) - 2):
        acc_Dt *= witness_caches[j][1]
        Wt = shamir_trick(Wt, witness_caches[j+1][0], acc_Dt, witness_caches[j+1][1], n)
    if len(txns) % cache_size != 0:
        if len(txns) / cache_size < 1:
            Wt = pow(Wt, other_state_prime, n)
        else:
            acc_Dt *= witness_caches[j][1]
            Wt = shamir_trick(Wt, witness_caches[j+1], acc_Dt, witness_caches[j+1][1], n)
            Wt = pow(Wt, other_state_prime, n)

    mkt = MerkleTree()
    for txn in txns:
        mkt.encrypt(bytes(txn, 'utf-8'))

    return (L1SpltTxn(Dt, tee_sig, St, Wt, str(mkt.get_root_hash())), Wt)


def gen_mer_txn(block_with_splt: Block, splt_offset, updated_Dt, tee_exe_sig):
    splt_digest = block_with_splt.get_txn_leaf_digest(splt_offset)
    return L1MerTxn(updated_Dt, tee_exe_sig, block_with_splt.get_block_hash(), splt_digest)


def update_RSA_witness(caches, cache_size, batch_size, splt_txn: L1SpltTxn, upd_primes, other_state_prime, n):
    updated_Dt = 1
    for p in upd_primes:
        updated_Dt *= p

    for i in range(len(caches)):
        wit, prime = caches[i]
        if i * cache_size >= batch_size:
            # deal with splt txn
            upd_wit = shamir_trick(wit, splt_txn.witness, prime, splt_txn.rsa_digest, n)
            # deal with mer txn
            upd_wit = pow(upd_wit, updated_Dt, n)
            caches[i] = (upd_wit, prime)
        elif (i+1) * cache_size >= batch_size:
            Wt = pow(wit, prime, n)
            upd_wit = shamir_trick(Wt, splt_txn.witness, upd_primes[i] * other_state_prime, splt_txn.rsa_digest, n)
            p = 1
            for j in range(len(upd_primes)-1):
                p *= upd_primes[j]
            upd_wit = pow(upd_wit, p, n)
            caches[i] = (upd_wit, upd_primes[i] * other_state_prime)
        else:
            Wt = pow(wit, prime, n)
            upd_wit = shamir_trick(Wt, splt_txn.witness, upd_primes[i], splt_txn.rsa_digest, n)
            p = 1
            for j in range(len(upd_primes)):
                if j != i:
                    p *= upd_primes[j]
            upd_wit = pow(upd_wit, p, n)
            caches[i] = (upd_wit, upd_primes[i])
    return


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: pickled_txn_pool selfHost:port partner1Host:port partner2Host:port ...' % sys.argv[0])
        sys.exit(-1)
    
    pickled_txn_pool = str(sys.argv[1])

    selfAddr = sys.argv[2]
    partners = sys.argv[3:]

    maxCommandsQueueSize = int(0.9 * SyncObjConf().commandsQueueSize / len(partners))

    cfg_file_path = Path('cfgs/config.yaml')
    root_path = Path('../../')

    if cfg_file_path.exists():
        with open(cfg_file_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    else:
        with open('cfgs/config.yaml', encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

    L2_batch_size = cfg['L2_batch_size']

    dapp_node = DAppNode(selfAddr, partners)

    if pickled_txn_pool == 'validate-only':
        while dapp_node._getLeader() is None:
            time.sleep(0.5)

        time.sleep(4.0)

        txn_num = cfg['txn_count']
        batch_num = int(txn_num/L2_batch_size)
        startTime = time.time()

        while time.time() - startTime < batch_num:
            st = time.time()
            if dapp_node.get_txn_batch() is not None:
                _g_success += 1
            delta = time.time() - st
            assert delta <= 1
            time.sleep(1 - delta)

        time.sleep(4.0)

        sys.exit()
    else:
        dapp_node.add_txn_to_pool(pickle.loads(ast.literal_eval(pickled_txn_pool)))

        while dapp_node._getLeader() is None:
            time.sleep(0.5)

        pickled_batch_list = dapp_node.partition_batches(L2_batch_size)
        batch_num = len(pickled_batch_list)

        startTime = time.time()

        while time.time() - startTime < batch_num:
            st = time.time()
            dapp_node.set_txn_batch(pickled_batch_list.pop(), time.time(), callback=clbck)
            _g_sent += 1
            delta = time.time() - st
            assert delta <= 1
            time.sleep(1 - delta)

        time.sleep(4.0)

        successRate = float(_g_success) / float(_g_sent)
        print('LAYER-2 TXN SUCCESS RATE:', successRate)

        delays = sorted(_g_delays)
        avgDelay = _g_delays[int(len(_g_delays) / 2)]
        print('LAYER-2 TXN AVG DELAY:', avgDelay)

        if successRate < 0.9:
            print('LAYER-2 TXN LOST RATE:', 1.0 - float(_g_success + _g_error) / float(_g_sent))
            print('ERRORS STATS: %d' % len(_g_errors))
            for err in _g_errors:
                print(err, float(_g_errors[err]) / float(_g_error))

        sys.exit(int(avgDelay * 100))
