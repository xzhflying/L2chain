use crate::basic::{H160, H256};

pub use blake2b_simd::{Hash as Blake2bHash, Params as Blake2bParams};

pub const DEFAULT_DIGEST_LEN: usize = 32;

pub fn blake2(size: usize) -> Blake2bParams {
    let mut params = Blake2bParams::new();
    params.hash_length(size);
    params
}

pub fn default_blake2() -> Blake2bParams {
    blake2(DEFAULT_DIGEST_LEN)
}

pub fn blake2b_hash_to_h256(input: Blake2bHash) -> H256 {
    H256::from_slice(input.as_bytes())
}

pub trait Hashable {
    fn to_h256(&self) -> H256;
}

impl Hashable for [u8] {
    fn to_h256(&self) -> H256 {
        let hash = default_blake2().hash(self);
        blake2b_hash_to_h256(hash)
    }
}

impl Hashable for alloc::vec::Vec<u8> {
    fn to_h256(&self) -> H256 {
        self.as_slice().to_h256()
    }
}
