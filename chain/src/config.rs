use serde::Deserialize;
use crate::consensus::Consensus;
use core::basic::error::anyhow::{anyhow, Result};
use once_cell::sync::OnceCell;
use std::time::Duration;


#[derive(Debug, Clone, Deserialize)]
pub struct ChainConfig {
    // The duration to generate a new block (in the unit of second).
    pub block_interval: usize,
    // Consensus method. Possible values: pow, raft.
    pub consensus: Consensus,
}


// #[derive(Debug, Clone, Deserialize)]
// pub struct MinerConfig {
//     /// Max number of txs in one block.
//     #[serde(default = "default_max_txs")]
//     pub max_txs: usize,
//     /// Min number of txs in one block. It should be greater than 0.
//     #[serde(default)]
//     pub min_txs: usize,
//     /// Max time span used in collecting txs.
//     #[serde(deserialize_with = "slimchain_utils::config::deserialize_duration_from_millis")]
//     pub max_block_interval: Duration,
// }

// fn default_max_txs() -> usize {
//     512
// }


#[derive(Debug, Copy, Clone, Deserialize)]
#[serde(default)]
pub struct PoWConfig {
    /// The initial difficulty used by PoW.
    pub difficulty: u64,
}

static GLOBAL_POW_CONFIG: OnceCell<PoWConfig> = OnceCell::new();

impl Default for PoWConfig {
    fn default() -> Self {
        Self {
            difficulty: 5_000_000,
        }
    }
}

impl PoWConfig {
    pub fn install_as_global(self) -> Result<()> {
        GLOBAL_POW_CONFIG
            .set(self)
            .map_err(|_| anyhow!("Failed to set PoWConfig."))
    }

    pub fn get() -> Self {
        GLOBAL_POW_CONFIG.get().copied().unwrap_or_default()
    }
}
