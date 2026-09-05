"""Public reference pipeline for wheelchair IMU angular profiling."""

from .io import SignalTable, read_signal_csv
from .workflow import PipelineConfig, PipelineResult, run_pipeline

__all__ = [
    "PipelineConfig",
    "PipelineResult",
    "SignalTable",
    "read_signal_csv",
    "run_pipeline",
]

__version__ = "1.1.2"
