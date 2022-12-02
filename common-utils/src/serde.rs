use snap::{read::FrameDecoder, write::FrameEncoder};
use serde::{Deserialize, Serialize};
use core::basic::error::anyhow::{Error, Result};

// binary encoder
pub fn binary_encode<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    let mut encoder = FrameEncoder::new(Vec::new());
    bincode::serialize_into(&mut encoder, value).map_err(Error::msg)?;
    Ok(encoder.into_inner()?)
}

// binary decoder
pub fn binary_decode<T: for<'de> Deserialize<'de>>(bytes: &[u8]) -> Result<T> {
    let decoder = FrameDecoder::new(bytes);
    bincode::deserialize_from(decoder).map_err(Error::msg)
}
