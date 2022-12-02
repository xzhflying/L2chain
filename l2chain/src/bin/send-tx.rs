use serde::{Deserialize, Serialize};
use std::{
    fs::File,
    io::{self, prelude::*},
    path::PathBuf,
    sync::Mutex,
};
use structopt::StructOpt;
use core::basic::{error::anyhow::{anyhow, Result, Context, bail}};
use once_cell::sync::{Lazy, OnceCell};
use regex::Regex;

static YCSB: OnceCell<Mutex<io::BufReader<File>>> = OnceCell::new();
static YCSB_READ_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^READ usertable (\w+) \[.+\]$").unwrap());
static YCSB_WRITE_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^UPDATE usertable (\w+) \[ field\d+=(.+) \]$").unwrap());

#[derive(Debug, StructOpt, Serialize, Deserialize)]
#[structopt(name = "send-tx", version = "0.1")]
struct Opts {
    /// Endpoint to http tx server.
    #[structopt(long, default_value = "127.0.0.1:8000")]
    endpoint: String,

    /// Total number of DApps.
    #[structopt(long, default_value = "1")]
    dapps: u64,

    /// Total number of TX.
    #[structopt(short, long)]
    txns: usize,

    /// Number of TX per seconds.
    #[structopt(short, long)]
    rate: usize,

    /// Wait period in seconds to check block committing after sending TX.
    #[structopt(short, long, default_value = "60")]
    wait: u64,

    /// Seed used for RNG.
    #[structopt(long)]
    seed: Option<u64>,

    /// Maximum number of accounts.
    #[structopt(short, long)]
    accounts: Option<usize>,

    // List of contracts. Accepted values: kvstore.
    // #[structopt(parse(try_from_str = parse_contract_arg), required = true)]
    // contract: Vec<ContractArg>,

    // Consensus protocol. Accepted values: pow, raft
    // #[structopt(long)]
    // consensus: ConsensusProtocol,

    // TODO: modify to support all workload.txt like files
    #[structopt(
        short,
        long,
        parse(from_os_str),
        help = "Path to ycsb.txt. Used for kvstore smart contract."
    )]
    ycsb: Option<PathBuf>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let opts = Opts::from_args();
    dbg!("Input opts:", &opts);

    // set ycsb file buffer. TODO: modify to support all workload.txt files
    if let Some(ycsb) = opts.ycsb.as_ref() {
        YCSB.set(Mutex::new(io::BufReader::new(File::open(ycsb)?)))
            .map_err(|_e| anyhow!("Failed to set YCSB file buffer."))?;
    }

    // TODO: send information to http rpc services


    Ok(())
}
