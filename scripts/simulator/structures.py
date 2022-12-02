import pickle
from hashlib import sha256
from dataclasses import dataclass
from pymerkle import MerkleTree
import random


@dataclass
class L1Txn:
    rsa_digest: int
    tee_sig: bytes


@dataclass
class L1SpltTxn(L1Txn):
    addrs: str
    witness: int
    txn_root: str

    def get_hash(self):
        concact_string = '{},{},{},{},{}'.format(self.rsa_digest, self.tee_sig, self.addrs, self.witness, self.txn_root)
        return sha256(concact_string.encode('utf-8')).hexdigest()


@dataclass
class L1MerTxn(L1Txn):
    block_hash: str
    splt_hash: str

    def get_hash(self):
        concact_string = '{},{},{},{}'.format(self.rsa_digest, self.tee_sig, self.block_hash, self.splt_hash)
        return sha256(concact_string.encode('utf-8')).hexdigest()


class Block:
    def __init__(self, proof, txns):
        self.__pre_hash = sha256('only_for_test'.encode('utf-8')).hexdigest()
        self.__consensus_proof = proof
        self.__txns = txns
        self.__txns_mkt = None
        self.__txns_mkt_root = None
        self.set_txns_mkt()
        self.__block_hash = sha256(pickle.dumps(self.__pre_hash) + pickle.dumps(self.__txns_mkt_root) + pickle.dumps(self.__consensus_proof)).hexdigest()

    def set_txns_mkt(self):
        self.__txns_mkt = MerkleTree()
        for txn in self.__txns:
            self.__txns_mkt.encrypt(txn.get_hash())
        self.__txns_mkt_root = str(self.__txns_mkt.get_root_hash())

    def get_txn_membership_path(self, offset):
        return self.__txns_mkt.generate_audit_path(offset)

    def txn_membership_proof(self, offset, path):
        proof = self.__txns_mkt.create_proof(offset, path)
        return proof.verify()

    def get_txn_leaf_digest(self, offset):
        return self.__txns_mkt.get_leaf(offset).digest

    def get_proof(self):
        return self.__consensus_proof

    def get_txns(self):
        return self.__txns

    def get_block_hash(self):
        return self.__block_hash

    def get_block_content_without_proof(self):
        return pickle.dumps(self.__pre_hash) + pickle.dumps(self.__txns_mkt_root)


if __name__ == '__main__':
    txns = [L1SpltTxn(1, 'dummy'.encode('utf-8'), 'dummy', 1, 'dummy'), L1SpltTxn(2, 'dummy'.encode('utf-8'), 'dummy', 2, 'dummy')]
    test_b = Block('dummy-proof', txns)
    print(test_b.get_block_hash())
    print(test_b.get_txn_leaf_digest(0))
    offset, path = test_b.get_txn_membership_path(0)
    print(test_b.txn_membership_proof(offset, path))

# print(sha256('dummy_block'.encode('utf-8')).hexdigest())
