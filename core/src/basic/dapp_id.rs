use crate::basic::Address;
use serde::{Deserialize, Serialize};

#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, Serialize, Deserialize)]
pub struct DAppId {
    pub id: u64,
    pub total: u64,
}

impl Default for DAppId {
    fn default() -> Self {
        Self { id: 0, total: 1 }
    }
}

impl DAppId {
    pub fn new(id: u64, total: u64) -> Self {
        Self { id, total }
    }

    pub fn contains(&self, addr: Address) -> bool {
        // Returns the lowest 8 bytes interpreted as big-endian.
        addr.to_low_u64_be() % self.total == self.id
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::basic::H160;

    #[test]
    fn test_dapp_id() {
        let dapp_id = DAppId::new(1, 2);
        assert!(dapp_id.contains(H160::repeat_byte(0xff).into()));
        assert!(!dapp_id.contains(H160::repeat_byte(0x00).into()));
    }
}
