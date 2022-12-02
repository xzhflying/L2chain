use core::basic::{error::anyhow::Result};

fn main() -> Result<()> {
    use tokio::runtime::Builder;
    Builder::new_multi_thread()
        .enable_all()
        .thread_stack_size(16 * 1024 * 1024) // increase thread stack size
        .build()
        .unwrap()
        .block_on(async { baseline::node::node_main().await })
}
