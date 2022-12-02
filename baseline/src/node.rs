use structopt::StructOpt;
use serde::{Deserialize, Serialize};
use std::{path::PathBuf, time::Duration};
use core::{
    basic::error::anyhow::{bail, Context as _, Result},
    config::Config,
};
use common_utils::path::{project_root_directory, binary_directory};
use chain::{
    config::ChainConfig, 
    role::Role,
    db::DB,
    consensus::Consensus
};


fn default_config_file_path() -> Result<PathBuf> {
    let root_dir = project_root_directory()?;
    let config_file_path = root_dir.join("configs/baseline/nodes/pow_example.toml");
    Ok(config_file_path)
}


#[derive(Debug, StructOpt)]
#[structopt(name = "node", version = "0.1")]
struct Opts {
    /// Path to the config.toml file.
    #[structopt(short, long, parse(from_os_str))]
    config: Option<PathBuf>,

    /// Path to the enclave file.
    #[structopt(short, long, parse(from_os_str))]
    enclave: Option<PathBuf>,

    /// Path to the data directory.
    #[structopt(short, long, parse(from_os_str))]
    data: Option<PathBuf>,

    /// Enable RocksDB statistics.
    #[structopt(long)]
    db_statistics: bool,
}


// TODO: modify the println to info
pub async fn node_main() -> Result<()> {
    let opts = Opts::from_args();

    // load config toml
    let cfg = if let Some(config) = opts.config {
        println!("Load config from {}.", config.display());
        Config::load(&config)?
    } else {
        println!("Load the default config file from {:?}.", default_config_file_path()?);
        Config::load(&default_config_file_path()?)?
    };

    let role: Role = cfg.get("role")?;
    println!("Role: {}", role);
    let chain_cfg: ChainConfig = cfg.get("chain")?;
    println!("Chain Cfg: {:#?}", chain_cfg);

    let bin_dir = binary_directory()?;
    let db = DB::open_or_create_in_dir(&opts.data.unwrap_or(bin_dir), role, opts.db_statistics)?;

    match chain_cfg.consensus {
        Consensus::PoW => {
            use crate::network::pow;
            use chain::config::PoWConfig;
            use network::p2p::config::NetworkConfig;
            
            let net_cfg: NetworkConfig = cfg.get("network")?;

            let pow_cfg: PoWConfig = cfg.get("pow").unwrap_or_default();
            println!("PoW initial difficulty: {}", pow_cfg.difficulty);
            pow_cfg.install_as_global()?;

            match role {
                Role::Client(_) => {
                    // let behavior = ClientBehavior::<Tx>::new(db, &chain_cfg, &net_cfg).await?;
                    // let swarmer =
                    //     Swarmer::new(net_cfg.keypair.to_libp2p_keypair(), behavior).await?;
                    // let mut ctrl = swarmer.spawn_app(&net_cfg.listen).await?;
                    // let _miner_peer_id = ctrl
                    //     .call_with_sender(|swarm, ret| {
                    //         swarm.behaviour_mut().discv_mut().find_random_peer_with_ret(
                    //             Role::Validator,
                    //             Duration::from_secs(60),
                    //             ret,
                    //         )
                    //     })
                    //     .await?
                    //     .context("Failed to find miner.")?;
                    // ctrl.run_until_interrupt().await?;
                }
                Role::Executor(_) => {
                    bail!("Executor is not implemented for baseline PoW network!");
                }
                Role::Validator => {
                    bail!("Not implemented");
                    // let miner_cfg: MinerConfig = cfg.get("miner")?;
                    // info!("Miner Cfg: {:#?}", miner_cfg);
                    // let behavior =
                    //     MinerBehavior::<Tx>::new(db, &chain_cfg, &miner_cfg, &net_cfg).await?;
                    // let swarmer =
                    //     Swarmer::new(net_cfg.keypair.to_libp2p_keypair(), behavior).await?;
                    // let ctrl = swarmer.spawn_app(&net_cfg.listen).await?;
                    // ctrl.run_until_interrupt().await?;
                }
            }
        }
        Consensus::Raft => {
            print!("Not implemented");
            // use crate::network::raft::{client::ClientNode, storage::StorageNode};
            // use slimchain_network::http::config::{NetworkConfig, RaftConfig};

            // let net_cfg: NetworkConfig = cfg.get("network")?;
            // let raft_cfg: RaftConfig = cfg.get("raft")?;

            // match role {
            //     Role::Client(_) => {
            //         let miner_cfg: MinerConfig = cfg.get("miner")?;
            //         println!("Miner Cfg: {:#?}", miner_cfg);
            //         let mut client: ClientNode<Tx> =
            //             ClientNode::new(db, &chain_cfg, &miner_cfg, &net_cfg, &raft_cfg).await?;
            //             println!("Press Ctrl-C to quit.");
            //         tokio::signal::ctrl_c().await?;
            //         println!("Quitting.");
            //         client.shutdown().await?;
            //     }
            //     Role::Storage(_) => {
            //         let engine = create_tx_engine(&cfg, &opts.enclave)?;
            //         let mut storage = StorageNode::new(db, engine, &chain_cfg, &net_cfg).await?;
            //         println!("Press Ctrl-C to quit.");
            //         tokio::signal::ctrl_c().await?;
            //         println!("Quitting.");
            //         storage.shutdown().await?;
            //     }
            //     Role::Miner => {
            //         bail!("Role cannot be miner.");
            //     }
            // }
        }
    }

    Ok(())
}
