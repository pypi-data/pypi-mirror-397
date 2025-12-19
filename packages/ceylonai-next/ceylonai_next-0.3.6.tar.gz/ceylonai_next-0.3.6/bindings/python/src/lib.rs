// Python bindings for the Ceylon AI framework
// This module coordinates all the Python bindings across different components
// Uses inline module syntax for PyO3 introspection support

use pyo3::prelude::*;

// Module declarations
mod action;
mod agent;
mod llm;
mod logging;
mod memory;
mod mesh;
mod metrics;
mod react;
mod registry;
mod runtime;

// Re-exports for easy access within submodules
pub use action::{PyAction, PyToolInvoker};
pub use agent::{PyAgent, PyAgentContext, PyAgentMessageProcessor};
pub use llm::{PyLlmAgent, PyLlmConfig};
pub use logging::{init_logging_py, PyLoggingConfig, PyLoggingHandle};
pub use memory::{PyInMemoryBackend, PyMemoryEntry, PyMemoryQuery, PyRedisBackend};
pub use mesh::{PyDistributedMesh, PyLocalMesh, PyMeshRequest, PyMeshResult};
pub use metrics::get_metrics;
pub use react::{PyReActConfig, PyReActResult, PyReActStep};
pub use registry::{PyAgentMetadata, PyInMemoryRegistry};

/// Ceylon AI Python module - using inline module syntax for introspection support
#[pymodule]
pub mod ceylonai_next {
    use super::*;

    // Mesh components
    #[pymodule_export]
    use super::mesh::PyDistributedMesh;
    #[pymodule_export]
    use super::mesh::PyLocalMesh;
    #[pymodule_export]
    use super::mesh::PyMeshRequest;
    #[pymodule_export]
    use super::mesh::PyMeshResult;

    // Agent components
    #[pymodule_export]
    use super::agent::PyAgent;
    #[pymodule_export]
    use super::agent::PyAgentContext;
    #[pymodule_export]
    use super::agent::PyAgentMessageProcessor;

    // Action/Tool components
    #[pymodule_export]
    use super::action::PyAction;
    #[pymodule_export]
    use super::action::PyToolInvoker;

    // LLM components
    #[pymodule_export]
    use super::llm::PyLlmAgent;
    #[pymodule_export]
    use super::llm::PyLlmConfig;

    // Memory components
    #[pymodule_export]
    use super::memory::PyInMemoryBackend;
    #[pymodule_export]
    use super::memory::PyMemoryEntry;
    #[pymodule_export]
    use super::memory::PyMemoryQuery;
    #[pymodule_export]
    use super::memory::PyRedisBackend;

    // ReAct framework components
    #[pymodule_export]
    use super::react::PyReActConfig;
    #[pymodule_export]
    use super::react::PyReActResult;
    #[pymodule_export]
    use super::react::PyReActStep;

    // Registry components
    #[pymodule_export]
    use super::registry::PyAgentMetadata;
    #[pymodule_export]
    use super::registry::PyInMemoryRegistry;

    // Logging components
    #[pymodule_export]
    use super::logging::init_logging_py;
    #[pymodule_export]
    use super::logging::PyLoggingConfig;
    #[pymodule_export]
    use super::logging::PyLoggingHandle;

    // Metrics
    #[pymodule_export]
    use super::metrics::get_metrics;
}
