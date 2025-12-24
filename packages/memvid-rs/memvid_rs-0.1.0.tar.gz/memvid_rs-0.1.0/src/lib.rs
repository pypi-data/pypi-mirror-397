use pyo3::prelude::*;

mod encoder;
use encoder::MemvidEncoder;

#[pymodule]
fn memvid_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<MemvidEncoder>()?;
    Ok(())
}
