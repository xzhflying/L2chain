#![crate_name = "simenclave"]
#![crate_type = "staticlib"]

#![cfg_attr(not(target_env = "sgx"), no_std)]
#![cfg_attr(target_env = "sgx", feature(rustc_private))]

extern crate sgx_types;
#[cfg(not(target_env = "sgx"))]
#[macro_use]
extern crate sgx_tstd as std;

extern crate kvdb;
extern crate kvdb_memorydb;

use sgx_types::*;
use std::string::String;
use std::vec::Vec;
use std::io::{self, Write};
use std::slice;

use kvdb::{DBTransaction, KeyValueDB};

use pyo3::prelude::*;
use pyo3::types::IntoPyDict;

#[no_mangle]
pub extern "C" fn txn_simulation(some_string: *const u8, some_len: usize) -> sgx_status_t {
    let enclave_helper = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../enclave.py"));
    
    let key1 ="dumped_txns";
    Python::with_gil(|py| {
    let activators = PyModule:: from_code (py, enclave_helper,"", "")?;
    let kwargs = [(key1,dumped_txns)].into_py_dict(py);
    let rw_set:Vec<&str> = activators.getattr("simulate_txns")?.call((), Some(kwargs))?.extract()?;
    Ok(())
    })

    (sgx_status_t::SGX_SUCCESS, rw_set)
}


#[no_mangle]
pub extern "C" fn txn_execution(dumped_txns: *const u8, some_len: usize) -> (sgx_status_t, Vec<i32>, i32) {

    let enclave_helper = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../enclave.py"));
    
    let key1 ="dumped_txns";
    Python::with_gil(|py| {
    let activators = PyModule:: from_code (py, enclave_helper,"", "")?;
    let kwargs = [(key1,dumped_txns)].into_py_dict(py);
    let (upd_cache_primes:Vec<i32>, updated_Dt: i32) = activators.getattr("execute_txns")?.call((), Some(kwargs))?.extract()?;
    Ok(())
    })

    // test kvdb_memorydb
    let db = kvdb_memorydb::create(0);
    println!("get the db instance");

    let mut batch = DBTransaction::new();
    batch.put(None, b"test", dumped_txns);
    db.write_buffered(batch);
    

    (sgx_status_t::SGX_SUCCESS, upd_cache_primes, updated_Dt)
}


#[no_mangle]
pub extern "C" fn splt_verification(proof: *const u8, content: *const u8, block_hash: *const u8) -> sgx_status_t {
    let enclave_helper = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../enclave.py"));
    
    let key1 = "proof"
    let key2 = "content"
    let key3 = "block_hash"

    Python::with_gil(|py| {
        let activators = PyModule:: from_code (py, enclave_helper,"", "")?;
        let kwargs = [(key1, proof), (key2, content), (key3, block_hash)].into_py_dict(py);
        let res:bool = activators.getattr("block_proof_verification")?.call((), Some(kwargs))?.extract()?;
        Ok(())
    })

    if !res {
        println!("Something wrong with the splt verification");
    }

    sgx_status_t::SGX_SUCCESS
}
