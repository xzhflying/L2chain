#![no_std]

extern crate alloc;
#[cfg(feature = "std")]
extern crate std;

pub mod basic;
pub mod hashes;
pub mod utils;
pub mod config;

pub use core;
