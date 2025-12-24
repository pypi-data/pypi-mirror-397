# Soren CLI Processors
# Specialized processors for different evaluation types

from .agent_workflow import (
    process_test_case_directory,
    process_all_test_cases,
    compute_aggregate_metrics,
)

__all__ = [
    "process_test_case_directory",
    "process_all_test_cases",
    "compute_aggregate_metrics",
]
