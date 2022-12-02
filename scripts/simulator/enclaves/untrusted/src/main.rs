extern crate sgx_types;
extern crate sgx_urts;
use sgx_types::*;
use sgx_urts::SgxEnclave;

use std::env;

use pyo3::prelude::*;
use pyo3::types::IntoPyDict;

static ENCLAVE_FILE: &'static str = "enclave.signed.so";

extern {
    fn txn_simulation(eid: sgx_enclave_id_t, retval: *mut sgx_status_t,
                     dumped_txns: *const u8, len: usize) -> sgx_status_t;
    fn txn_execution(eid: sgx_enclave_id_t, retval: *mut sgx_status_t,
                     dumped_txns: *const u8, len: usize) -> sgx_status_t;
    fn splt_verification(eid: sgx_enclave_id_t, retval: *mut sgx_status_t,
                     proof: *const u8, content: *const u8, block_hash: *const u8)
}

fn init_enclave() -> SgxResult<SgxEnclave> {
    let mut launch_token: sgx_launch_token_t = [0; 1024];
    let mut launch_token_updated: i32 = 0;
    // call sgx_create_enclave to initialize an enclave instance
    // Debug Support: set 2nd parameter to 1
    let debug = 1;
    let mut misc_attr = sgx_misc_attribute_t {secs_attr: sgx_attributes_t { flags:0, xfrm:0}, misc_select:0};
    SgxEnclave::create(ENCLAVE_FILE,
                       debug,
                       &mut launch_token,
                       &mut launch_token_updated,
                       &mut misc_attr)
}

fn main() -> PyResult<()> {
    let enclave = match init_enclave() {
        Ok(r) => {
            println!("[+] Init Enclave Successful {}!", r.geteid());
            r
        },
        Err(x) => {
            println!("[-] Init Enclave Failed {}!", x.as_str());
            return;
        },
    };

    let args: Vec<String> = env::args().collect();
    let operation = &args[1];
    let dumped_txns = &args[2];

    if operation.as_slice() == 'exe' {
        let proof = &args[3];
        let content = &args[4];
        let block_hash = &args[5];

        let mut retval = sgx_status_t::SGX_SUCCESS;

        let vrf_result = unsafe {
            splt_verification(enclave.geteid(),
                      &mut retval,
                      proof.as_ptr() as * const u8,
                      content.as_ptr() as * const u8,
                      block_hash.as_ptr() as * const u8)
        };

        match vrf_result {
            sgx_status_t::SGX_SUCCESS => {},
            _ => {
                println!("[-] ECALL Enclave Failed {}!", result.as_str());
            }
        }

        let (exe_result, upd_cache_primes, updated_Dt) = unsafe {
            txn_execution(enclave.geteid(),
                      &mut retval,
                      dumped_txns.as_ptr() as * const u8,
                      dumped_txns.len())
        };

        match exe_result {
            sgx_status_t::SGX_SUCCESS => {},
            _ => {
                println!("[-] ECALL Enclave Failed {}!", result.as_str());
                return (exe_result, upd_cache_primes, updated_Dt);
            }
        }

        println!("[+] Transaction execution success...");
    } else {
        let mut retval = sgx_status_t::SGX_SUCCESS;

        let (sim_result, rw_set) = unsafe {
            txn_simulation(enclave.geteid(),
                      &mut retval,
                      dumped_txns.as_ptr() as * const u8,
                      dumped_txns.len())
        };

        match sim_result {
            sgx_status_t::SGX_SUCCESS => {},
            _ => {
                println!("[-] ECALL Enclave Failed {}!", result.as_str());
                return rw_set;
            }
        }

        println!("[+] Transaction simulation success...");
    }

    enclave.destroy();
}
