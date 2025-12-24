use base64::Engine as _;
use base64::engine::general_purpose::STANDARD;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::HashMap;
use std::sync::Mutex;

// Global asset store: optional HashMap from name -> bytes
static ASSET_STORE: Mutex<Option<HashMap<String, Vec<u8>>>> = Mutex::new(None);

fn init_store() {
    let mut s = ASSET_STORE.lock().unwrap();
    if s.is_none() {
        *s = Some(HashMap::new());
    }
}

fn store_put(name: String, bytes: Vec<u8>) {
    init_store();
    let mut s = ASSET_STORE.lock().unwrap();
    if let Some(ref mut map) = *s {
        map.insert(name, bytes);
    }
}

fn store_get(name: &str) -> Option<Vec<u8>> {
    let s = ASSET_STORE.lock().unwrap();
    if let Some(ref map) = *s {
        map.get(name).cloned()
    } else {
        None
    }
}

fn store_get_by_basename(basename: &str) -> Option<Vec<u8>> {
    let s = ASSET_STORE.lock().unwrap();
    if let Some(ref map) = *s {
        for (k, v) in map.iter() {
            if k.ends_with(basename) || k == basename {
                return Some(v.clone());
            }
        }
    }
    None
}

fn guess_mime_from_name(name: &str) -> &str {
    let name = name.to_lowercase();
    if name.ends_with(".png") {
        "image/png"
    } else if name.ends_with(".jpg") || name.ends_with(".jpeg") {
        "image/jpeg"
    } else if name.ends_with(".gif") {
        "image/gif"
    } else if name.ends_with(".svg") {
        "image/svg+xml"
    } else if name.ends_with(".webp") {
        "image/webp"
    } else if name.ends_with(".bmp") {
        "image/bmp"
    } else {
        "application/octet-stream"
    }
}

fn bytes_to_data_uri(name: &str, bytes: &[u8]) -> String {
    let mime = guess_mime_from_name(name);
    let b64 = STANDARD.encode(bytes);
    format!("data:{};base64,{}", mime, b64)
}

/// Python-facing AssetCatalog for registering raw assets from Python.
#[pyclass]
pub struct AssetCatalog;

#[pymethods]
impl AssetCatalog {
    #[new]
    fn new() -> Self {
        init_store();
        AssetCatalog {}
    }

    /// Add an asset by name and raw bytes.
    #[pyo3(text_signature = "($self, name, data)")]
    fn add<'py>(&self, _py: Python<'py>, name: String, data: &Bound<'py, PyAny>) -> PyResult<()> {
        let bytes: Vec<u8> = data
            .extract()
            .map_err(|_| PyValueError::new_err("data must be bytes"))?;

        store_put(name, bytes);
        Ok(())
    }

    /// Return an asset data URI if present, else None.
    #[pyo3(text_signature = "($self, name)")]
    fn get_data_uri(&self, name: String) -> Option<String> {
        if let Some(b) = store_get(&name) {
            Some(bytes_to_data_uri(&name, &b))
        } else if let Some(b) = store_get_by_basename(&name) {
            Some(bytes_to_data_uri(&name, &b))
        } else {
            None
        }
    }
}

// Helpers for other Rust code to consult the store
pub fn get_asset_data_uri(name: &str) -> Option<String> {
    if let Some(b) = store_get(name) {
        Some(bytes_to_data_uri(name, &b))
    } else if let Some(b) = store_get_by_basename(name) {
        Some(bytes_to_data_uri(name, &b))
    } else {
        None
    }
}
