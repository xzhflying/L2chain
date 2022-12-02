use toml::Value as TomlValue;
use std::{fs, path::Path};
use crate::basic::error::anyhow::{anyhow, Result, Error};
use serde::Deserialize;


#[derive(Debug, Clone)]
pub struct Config(TomlValue);

impl Config {
    // load configs from the file
    pub fn load(file: &Path) -> Result<Self> {
        let cfg = toml::from_str(
            &fs::read_to_string(file)
                .map_err(|e| anyhow!("Failed to open {}. Err: {}.", file.display(), e))?,
        )
        .map_err(|e| anyhow!("Failed to load {}. Err: {}.", file.display(), e))?;
        Ok(Self(cfg))
    }

    // get the value of the given key in the config
    pub fn get<'de, T: Deserialize<'de>>(&self, key: &str) -> Result<T> {
        self.0
            .get(key)
            .ok_or_else(|| anyhow!("Failed to read `{}` in the config.", key))?
            .clone()
            .try_into()
            .map_err(Error::msg)
    }
}
