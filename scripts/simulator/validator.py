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
sys.path.append("../")
from pysyncobj import SyncObj, replicated, SyncObjConf, FAIL_REASON
from structures import Block, L1MerTxn, L1SpltTxn


class Validator(SyncObj):
    cfg = SyncObjConf(
            appendEntriesUseBatch=False,
        )

    def __init__(self, self_node, other_nodes, **kwargs):
        SyncObj.__init__(self, self_node, other_nodes, **kwargs)
        self.__txn_pool = []
        self.__latest_block = ''  # To be consented

    def add_txn_to_pool(self, txns):
        assert type(txns) == list
        for txn in txns:
            assert type(txn) == L1MerTxn or type(txn) == L1SpltTxn
        self.__txn_pool += txns
    
    def get_txn_pool(self):
        return self.__txn_pool

    def get_txn_pool_size(self):
        return len(self.__txn_pool)

    def pack_up_block(self, volum):
        txns = self.__txn_pool[:volum]
        del self.__txn_pool[:volum]
        block = Block('dummy_proof', txns)
        return pickle.dumps(block)

    @replicated
    def set_latest_block(self, pickled_block, callTime, sync = True):
        self.__latest_block = pickled_block
        return (callTime, time.time())

    def get_latest_block(self):
        if self.__latest_block == '':
            return None
        else:
            block = pickle.loads(self.__latest_block)
            return block


def validate_merge(mer: L1MerTxn, splt_offset, splt_block: Block, current_rsa_digest, n):
    offset, path = splt_block.get_txn_membership_path(splt_offset)
    assert path[0][1] == mer.splt_hash
    assert splt_block.txn_membership_proof(offset, path)
    rsa_digest = pow(current_rsa_digest, mer.rsa_digest, n)
    return rsa_digest


def validate_split(splt, pre_RSA_digest, n):
    assert pow(splt.witness, splt.rsa_digest, n) == pre_RSA_digest
    return


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

    block_interval = cfg['block_interval']
    block_size = cfg['block_size']

    validator = Validator(selfAddr, partners)

    if pickled_txn_pool == 'validate-only':
        while validator._getLeader() is None:
            time.sleep(0.5)

        txn_num = cfg['txn_count']
        block_num = int(txn_num/block_size)
        startTime = time.time()

        while time.time() - startTime < block_num * block_interval:
            st = time.time()
            if validator.get_latest_block() is not None:
                _g_success += 1
            delta = time.time() - st
            assert delta <= block_interval
            time.sleep(block_interval - delta)

        time.sleep(4.0)

        sys.exit()
    else:
        validator.add_txn_to_pool(pickle.loads(ast.literal_eval(pickled_txn_pool)))

        while validator._getLeader() is None:
            time.sleep(0.5)

        pickled_block_list = []
        for _ in range(int(validator.get_txn_pool_size()/block_size)):
            pickled_block_list.append(validator.pack_up_block(block_size))
        block_num = len(pickled_block_list)
        time.sleep(3.0)

        startTime = time.time()

        while time.time() - startTime < block_num * block_interval:
            st = time.time()
            validator.set_latest_block(pickled_block_list.pop(), time.time(), callback=clbck)
            _g_sent += 1
            delta = time.time() - st
            assert delta <= block_interval
            time.sleep(block_interval - delta)

        time.sleep(4.0)

        successRate = float(_g_success) / float(_g_sent)
        print('LAYER-1 BLOCK SUCCESS RATE:', successRate)

        delays = sorted(_g_delays)
        avgDelay = _g_delays[int(len(_g_delays) / 2)]
        print('LAYER-1 BLOCK AVG DELAY:', avgDelay)

        if successRate < 0.9:
            print('LAYER-1 BLOCK LOST RATE:', 1.0 - float(_g_success + _g_error) / float(_g_sent))
            print('ERRORS STATS: %d' % len(_g_errors))
            for err in _g_errors:
                print(err, float(_g_errors[err]) / float(_g_error))

        sys.exit(int(avgDelay * 100))
