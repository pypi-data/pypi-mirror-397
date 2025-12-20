use crate::read_stream::ReadStream;
use crate::tos_error::map_tos_error;
use crate::tos_model::ListObjectsResult;
use pyo3::{pyclass, pymethods, PyRef, PyRefMut, PyResult};
use std::sync::{Arc, Mutex, RwLock};

#[pyclass(name = "ListStream", module = "tosnativeclient")]
pub struct ListStream {
    pub(crate) list_stream: Arc<RwLock<tosnativeclient_core::list_stream::ListStream>>,
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) prefix: String,
    #[pyo3(get)]
    pub(crate) delimiter: String,
    #[pyo3(get)]
    pub(crate) max_keys: isize,
    #[pyo3(get)]
    pub(crate) continuation_token: String,
    #[pyo3(get)]
    pub(crate) start_after: String,
    #[pyo3(get)]
    pub(crate) list_background_buffer_count: isize,
    #[pyo3(get)]
    pub(crate) prefetch: bool,
}

#[pymethods]
impl ListStream {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(
        slf: PyRefMut<'_, Self>,
    ) -> PyResult<Option<(ListObjectsResult, Option<Vec<ReadStream>>)>> {
        let list_stream = slf.list_stream.clone();
        slf.py()
            .allow_threads(|| match list_stream.write().unwrap().next() {
                Ok(data) => match data {
                    None => Ok(None),
                    Some(output) => Ok(Some(trans_list_objects_result(output))),
                },
                Err(ex) => Err(map_tos_error(ex)),
            })
    }

    pub fn close(slf: PyRef<'_, Self>) {
        let list_stream = slf.list_stream.clone();
        slf.py().allow_threads(|| {
            list_stream.read().unwrap().close();
        });
    }

    pub fn current_prefix(slf: PyRef<'_, Self>) -> PyResult<Option<String>> {
        let list_stream = slf.list_stream.clone();
        slf.py()
            .allow_threads(|| match list_stream.read().unwrap().current_prefix() {
                Ok(prefix) => Ok(prefix),
                Err(ex) => Err(map_tos_error(ex)),
            })
    }

    pub fn current_continuation_token(slf: PyRef<'_, Self>) -> PyResult<Option<String>> {
        let list_stream = slf.list_stream.clone();
        slf.py().allow_threads(
            || match list_stream.read().unwrap().current_continuation_token() {
                Ok(prefix) => Ok(prefix),
                Err(ex) => Err(map_tos_error(ex)),
            },
        )
    }
}

fn trans_list_objects_result(
    output: (
        ve_tos_rust_sdk::object::ListObjectsType2Output,
        Option<Vec<tosnativeclient_core::read_stream::ReadStream>>,
    ),
) -> (ListObjectsResult, Option<Vec<ReadStream>>) {
    match output.1 {
        None => (ListObjectsResult::new(output.0), None),
        Some(streams) => {
            let mut read_streams = Vec::with_capacity(streams.len());
            for stream in streams {
                let bucket = stream.bucket().to_string();
                let key = stream.key().to_string();
                let etag = stream.etag().to_string();
                let size = stream.size();
                read_streams.push(ReadStream {
                    read_stream: Arc::new(stream),
                    bucket,
                    key,
                    etag,
                    size,
                });
            }
            (ListObjectsResult::new(output.0), Some(read_streams))
        }
    }
}
