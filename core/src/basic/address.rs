use crate::basic::{H160, H256};
use crate::hashes::Hashable;

#[derive(
    Debug,
    Default,
    Copy,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    serde::Serialize,
    serde::Deserialize,
    derive_more::Deref,
    derive_more::DerefMut,
    derive_more::Display,
    derive_more::From,
    derive_more::Into,
)]
pub struct Address(pub H160);

impl Hashable for Address {
    fn to_h256(&self) -> H256 {
        self.0.as_bytes().to_h256()
    }
}
