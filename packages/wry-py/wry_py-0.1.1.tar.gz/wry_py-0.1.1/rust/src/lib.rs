mod elements;
mod renderer;
mod window;

use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn wry_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Classes
    m.add_class::<window::UiWindow>()?;
    m.add_class::<elements::Element>()?;
    m.add_class::<elements::ElementBuilder>()?;

    // Convenience functions
    m.add_function(wrap_pyfunction!(elements::div, m)?)?;
    m.add_function(wrap_pyfunction!(elements::text, m)?)?;
    m.add_function(wrap_pyfunction!(elements::button, m)?)?;
    m.add_function(wrap_pyfunction!(elements::input, m)?)?;

    Ok(())
}
