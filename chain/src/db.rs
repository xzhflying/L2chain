use std::{path::Path, sync::Arc, boxed::Box, println};
use kvdb::{DBKey, DBTransaction, KeyValueDB};
use core::basic::{
    error::anyhow::{Context as _, Error, Result},
    H256
};
use serde::{Deserialize, Serialize};
use crate::role::Role;
use common_utils::serde::{binary_decode, binary_encode};


#[inline]
pub fn str_to_db_key(input: &str) -> DBKey {
    let mut key = DBKey::new();
    key.extend_from_slice(input.as_bytes());
    key
}

#[inline]
pub fn u64_to_db_key(input: u64) -> DBKey {
    let mut key = DBKey::new();
    key.extend_from_slice(&input.to_le_bytes()[..]);
    key
}

// #[inline]
// pub fn block_height_to_db_key(height: BlockHeight) -> DBKey {
//     let mut key = DBKey::new();
//     key.extend_from_slice(&height.to_le_bytes()[..]);
//     key
// }

#[inline]
pub fn h256_to_db_key(input: H256) -> DBKey {
    debug_assert!(!input.is_zero());
    DBKey::from_buf(input.to_fixed_bytes())
}

// A simple DB impl with fixed colums
pub struct DB {
    db: Box<dyn KeyValueDB>
}
pub type DBPtr = Arc<DB>;

pub const TOTAL_COLS: u32 = 5;
// store meta data
pub const META_COL: u32 = 0;
// store block height <-> block
pub const BLOCK_HEIGHT_COL: u32 = 1;
// store tx_hash <-> tx
pub const TX_COL: u32 = 2;
// store state addr <-> node
pub const STATE_DB_COL: u32 = 3;
// store log_idx <-> log
pub const LOG_DB_COL: u32 = 4;

impl DB {
    pub fn open_or_create(path: &Path, enable_statistics: bool) -> Result<Arc<Self>> {
        println!("Open database at {}", path.display());
        let mut cfg = kvdb_rocksdb::DatabaseConfig::with_columns(TOTAL_COLS);
        cfg.enable_statistics = enable_statistics;
        let db = kvdb_rocksdb::Database::open(&cfg, &path)?;
        Ok(Arc::new(Self { db: Box::new(db) }))
    }

    pub fn open_or_create_in_dir(
        dir: &Path,
        role: Role,
        enable_statistics: bool,
    ) -> Result<Arc<Self>> {
        let db_file = match role {
            Role::Client(_) => "client.db",
            Role::Executor(_) => "executor.db",
            Role::Validator => "validator.db",
        };
        Self::open_or_create(&dir.join(db_file), enable_statistics)
    }

    // #[cfg(test)]
    // pub fn load_test() -> Arc<Self> {
    //     let db = kvdb_memorydb::create(TOTAL_COLS);
    //     Arc::new(Self { db: Box::new(db) })
    // }

    pub fn get_object<T: for<'de> Deserialize<'de>>(
        &self,
        col: u32,
        key: &DBKey,
    ) -> Result<T> {
        self.db
            .get(col, key)
            .map_err(Error::msg)?
            .map(|bin| binary_decode::<T>(&bin[..]))
            .transpose()?
            .context("Object not available in the database.")
    }

    pub fn get_meta_object<T: for<'de> Deserialize<'de>>(&self, key: &str) -> Result<Option<T>> {
        self.get_object(META_COL, &str_to_db_key(key))
    }

    pub fn get_log_object<T: for<'de> Deserialize<'de>>(&self, idx: u64) -> Result<Option<T>> {
        self.get_object(LOG_DB_COL, &u64_to_db_key(idx))
    }

    pub fn get_table_size(&self, col: u32) -> usize {
        self.db.iter(col).map(|(k, v)| k.len() + v.len()).sum()
    }

    pub fn write_sync(&self, tx: Transaction) -> Result<()> {
        self.db.write(tx.db_txn).map_err(Error::msg)
    }

    pub async fn write_async(self: &Arc<Self>, tx: Transaction) -> Result<()> {
        let this = self.clone();
        tokio::task::spawn_blocking(move || this.db.write(tx.db_txn))
            .await?
            .map_err(Error::msg)
    }
}


#[derive(Default)]
pub struct Transaction {
    db_txn: DBTransaction,
}

impl Transaction {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_capacity(cap: usize) -> Self {
        Self {
            db_txn: DBTransaction::with_capacity(cap),
        }
    }

    pub fn insert_object<T: Serialize>(&mut self, col: u32, key: &DBKey, value: &T) -> Result<()> {
        let bin = binary_encode(value)?;
        self.db_txn.put_vec(col, key, bin);
        Ok(())
    }

    pub fn insert_meta_object<T: Serialize>(&mut self, key: &str, value: &T) -> Result<()> {
        self.insert_object(META_COL, &str_to_db_key(key), value)
    }

    pub fn insert_log_object<T: Serialize>(&mut self, idx: u64, value: &T) -> Result<()> {
        self.insert_object(LOG_DB_COL, &u64_to_db_key(idx), value)
    }

    // pub fn insert_block<Block: BlockTrait + Serialize>(&mut self, block: &Block) -> Result<()> {
    //     self.insert_object(
    //         BLOCK_HEIGHT_COL,
    //         &block_height_to_db_key(block.block_height()),
    //         block,
    //     )
    // }

    // pub fn insert_tx<Tx: TxTrait + Serialize>(&mut self, tx_hash: H256, tx: &Tx) -> Result<()> {
    //     self.insert_object(TX_COL, &h256_to_db_key(tx_hash), tx)
    // }

    // pub fn update_state(&mut self, update: &TxStateUpdate) -> Result<()> {
    //     for (&addr, node) in update.acc_nodes.iter() {
    //         self.insert_object(STATE_DB_COL, &h256_to_db_key(addr), node)?;
    //     }

    //     for (_, state_update) in update.state_nodes.iter() {
    //         for (&addr, node) in state_update.iter() {
    //             self.insert_object(STATE_DB_COL, &h256_to_db_key(addr), node)?;
    //         }
    //     }

    //     Ok(())
    // }

    pub fn delete_object(&mut self, col: u32, key: &DBKey) {
        self.db_txn.delete(col, key);
    }

    pub fn delete_log_object(&mut self, idx: u64) {
        self.delete_object(LOG_DB_COL, &u64_to_db_key(idx))
    }
}

#[test]
fn test_db(){
    use common_utils::path::binary_directory;
    let db = DB::open_or_create_in_dir(&binary_directory().unwrap(), Role::default(), true);
}
