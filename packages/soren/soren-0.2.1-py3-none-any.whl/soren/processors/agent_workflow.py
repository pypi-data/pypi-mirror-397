"""
Agent Workflow Test Case Processor

Processes the test case directory structure for agent workflow evaluations.
This processor handles the complex, variable file structures of agent workflow tests.

Key Design Decisions:
- Only metrics (TP/TN/FP/FN) are stored in Postgres for filtering
- All other files are uploaded as-is to S3 for raw display in the UI
- Context folder is used to extract a display name for the test case
- Documents are stored with references for the UI to render

Directory Structure Expected:
    test_case_{n}/
    ├── context/
    │   └── engagement.json         # Context metadata (used for display name)
    ├── row_content/
    │   ├── control.txt             # Control statement
    │   └── test_plan.txt           # Test plan
    ├── documents/
    │   ├── original/               # Raw files (PDF, XLSX, etc.)
    │   ├── json_representation/    # Structured JSON extracts
    │   ├── summary/                # AI summaries
    │   └── pdf_conversion_path/    # Text extractions
    ├── expected_outputs/
    │   └── determine_effectiveness.txt
    ├── outputs/
    │   └── iteration_{n}/
    │       └── determine_effectiveness.txt
    └── evaluation_results/
        └── iteration_{n}/
            └── determine_effectiveness_eval_result.csv
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TestCaseSummary:
    """
    Summary of a test case for storage in Postgres.

    This is a lightweight representation for fast filtering/pagination.
    Full data is stored in S3.
    """
    test_case_id: str
    result: Optional[str]  # TP, TN, FP, FN, or None if no metrics
    control_summary: Optional[str]  # First 500 chars of control text
    expected_verdict: Optional[str]
    actual_verdict: Optional[str]
    document_count: int
    display_name: Optional[str]  # From context/engagement.json
    s3_data_key: Optional[str] = None


@dataclass
class TestCaseFullData:
    """
    Full test case data to be stored in S3.

    Contains all files and metadata for rendering in the UI.
    """
    test_case_id: str
    display_name: Optional[str]
    context: Dict[str, Any]

    # File listings (relative paths within the test case)
    files: Dict[str, List[str]]  # Category -> list of file paths

    # Metrics if available
    metrics: Optional[Dict[str, int]]
    result: Optional[str]


def process_test_case_directory(test_case_path: Path) -> Tuple[TestCaseSummary, TestCaseFullData]:
    """
    Process a single test case directory.

    Args:
        test_case_path: Path to the test case directory (e.g., test_case_0/)

    Returns:
        Tuple of (TestCaseSummary for Postgres, TestCaseFullData for S3)
    """
    test_case_id = test_case_path.name

    # 1. Read context for display name
    context = {}
    display_name = None
    engagement_file = test_case_path / "context" / "engagement.json"
    if engagement_file.exists():
        try:
            with open(engagement_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            display_name = context.get("name", test_case_id)
        except Exception as e:
            print(f"  Warning: Could not read engagement.json: {e}")

    # 2. Read control for summary
    control_summary = None
    control_file = test_case_path / "row_content" / "control.txt"
    if control_file.exists():
        try:
            control_text = control_file.read_text(encoding='utf-8').strip()
            control_summary = control_text[:500] if control_text else None
        except Exception as e:
            print(f"  Warning: Could not read control.txt: {e}")

    # 3. Read expected verdict
    expected_verdict = None
    expected_verdict_file = test_case_path / "expected_outputs" / "determine_effectiveness.txt"
    if expected_verdict_file.exists():
        try:
            expected_verdict = expected_verdict_file.read_text(encoding='utf-8').strip()
            # Extract just the first line for display
            expected_verdict = expected_verdict.split('\n')[0][:100]
        except Exception as e:
            print(f"  Warning: Could not read expected verdict: {e}")

    # 4. Read actual verdict (from latest iteration)
    actual_verdict = None
    outputs_dir = test_case_path / "outputs"
    if outputs_dir.exists():
        iterations = sorted([d for d in outputs_dir.iterdir() if d.is_dir()])
        if iterations:
            latest_iteration = iterations[-1]
            actual_verdict_file = latest_iteration / "determine_effectiveness.txt"
            if actual_verdict_file.exists():
                try:
                    actual_verdict = actual_verdict_file.read_text(encoding='utf-8').strip()
                    # Extract just the first line for display
                    actual_verdict = actual_verdict.split('\n')[0][:100]
                except Exception as e:
                    print(f"  Warning: Could not read actual verdict: {e}")

    # 5. Read evaluation metrics (TP/TN/FP/FN)
    metrics = None
    result = None
    eval_dir = test_case_path / "evaluation_results"
    if eval_dir.exists():
        iterations = sorted([d for d in eval_dir.iterdir() if d.is_dir()])
        if iterations:
            latest_iteration = iterations[-1]
            metrics_file = latest_iteration / "determine_effectiveness_eval_result.csv"
            if metrics_file.exists():
                metrics = read_eval_metrics_csv(metrics_file)
                result = compute_result_from_metrics(metrics)

    # 6. Count documents
    document_count = 0
    original_docs_dir = test_case_path / "documents" / "original"
    if original_docs_dir.exists():
        document_count = len([f for f in original_docs_dir.iterdir() if f.is_file() and not f.name.startswith('.')])

    # 7. Collect all files for S3 storage
    files = collect_all_files(test_case_path)

    # Create summary for Postgres
    summary = TestCaseSummary(
        test_case_id=test_case_id,
        result=result,
        control_summary=control_summary,
        expected_verdict=expected_verdict,
        actual_verdict=actual_verdict,
        document_count=document_count,
        display_name=display_name,
    )

    # Create full data for S3
    full_data = TestCaseFullData(
        test_case_id=test_case_id,
        display_name=display_name,
        context=context,
        files=files,
        metrics=metrics,
        result=result,
    )

    return summary, full_data


def read_eval_metrics_csv(file_path: Path) -> Dict[str, int]:
    """
    Read evaluation metrics from CSV format:

    Metric,Value
    true_positives,1
    true_negatives,0
    false_positives,0
    false_negatives,0

    Returns:
        Dict with metric names and values
    """
    metrics = {}
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metric = row.get("Metric", "").lower().strip()
                value_str = row.get("Value", "0").strip()
                try:
                    metrics[metric] = int(value_str)
                except ValueError:
                    # Skip non-integer values
                    pass
    except Exception as e:
        print(f"  Warning: Could not read metrics CSV: {e}")
    return metrics


def compute_result_from_metrics(metrics: Dict[str, int]) -> Optional[str]:
    """
    Compute the result classification (TP/TN/FP/FN) for a single test case.

    For a single test case, only one of these should be 1.
    """
    tp = metrics.get("true_positives", 0)
    tn = metrics.get("true_negatives", 0)
    fp = metrics.get("false_positives", 0)
    fn = metrics.get("false_negatives", 0)

    # For a single test case, exactly one should be 1
    if tp > 0:
        return "TP"
    elif tn > 0:
        return "TN"
    elif fp > 0:
        return "FP"
    elif fn > 0:
        return "FN"
    return None  # No metrics or all zeros


def collect_all_files(test_case_path: Path) -> Dict[str, List[str]]:
    """
    Collect all files in the test case directory, organized by category.

    Returns a dict mapping category names to lists of relative file paths.
    """
    files = {
        "context": [],
        "row_content": [],
        "documents_original": [],
        "documents_json": [],
        "documents_summary": [],
        "documents_pdf_text": [],
        "expected_outputs": [],
        "outputs": [],
        "evaluation_results": [],
    }

    def add_files_from_dir(dir_path: Path, category: str):
        if dir_path.exists():
            for f in dir_path.iterdir():
                if f.is_file() and not f.name.startswith('.'):
                    rel_path = str(f.relative_to(test_case_path))
                    files[category].append(rel_path)

    # Context files
    add_files_from_dir(test_case_path / "context", "context")

    # Row content
    add_files_from_dir(test_case_path / "row_content", "row_content")

    # Documents
    add_files_from_dir(test_case_path / "documents" / "original", "documents_original")
    add_files_from_dir(test_case_path / "documents" / "json_representation", "documents_json")
    add_files_from_dir(test_case_path / "documents" / "summary", "documents_summary")
    add_files_from_dir(test_case_path / "documents" / "pdf_conversion_path", "documents_pdf_text")

    # Expected outputs
    add_files_from_dir(test_case_path / "expected_outputs", "expected_outputs")

    # Outputs (iterate through iterations)
    outputs_dir = test_case_path / "outputs"
    if outputs_dir.exists():
        for iteration_dir in outputs_dir.iterdir():
            if iteration_dir.is_dir():
                for f in iteration_dir.iterdir():
                    if f.is_file() and not f.name.startswith('.'):
                        rel_path = str(f.relative_to(test_case_path))
                        files["outputs"].append(rel_path)

    # Evaluation results (iterate through iterations)
    eval_dir = test_case_path / "evaluation_results"
    if eval_dir.exists():
        for iteration_dir in eval_dir.iterdir():
            if iteration_dir.is_dir():
                for f in iteration_dir.iterdir():
                    if f.is_file() and not f.name.startswith('.'):
                        rel_path = str(f.relative_to(test_case_path))
                        files["evaluation_results"].append(rel_path)

    return files


def process_all_test_cases(base_dir: Path) -> Tuple[List[TestCaseSummary], List[TestCaseFullData]]:
    """
    Process all test case directories in a base directory.

    Args:
        base_dir: Path to directory containing test_case_* folders

    Returns:
        Tuple of (list of summaries, list of full data)
    """
    summaries = []
    full_data_list = []

    # Find all test case directories
    test_case_dirs = sorted([
        d for d in base_dir.iterdir()
        if d.is_dir() and d.name.startswith("test_case_")
    ])

    if not test_case_dirs:
        print(f"No test case directories found in {base_dir}")
        return summaries, full_data_list

    print(f"Found {len(test_case_dirs)} test case directories")

    for tc_dir in test_case_dirs:
        try:
            print(f"  Processing {tc_dir.name}...")
            summary, full_data = process_test_case_directory(tc_dir)
            summaries.append(summary)
            full_data_list.append(full_data)
            print(f"    Result: {summary.result or 'No metrics'}")
        except Exception as e:
            print(f"  Error processing {tc_dir.name}: {e}")

    return summaries, full_data_list


def compute_aggregate_metrics(summaries: List[TestCaseSummary]) -> Dict[str, Any]:
    """
    Compute aggregate metrics from all test case summaries.

    Returns:
        Dict with aggregate metrics suitable for storage in Postgres
    """
    total_test_cases = len(summaries)
    true_positives = sum(1 for s in summaries if s.result == "TP")
    true_negatives = sum(1 for s in summaries if s.result == "TN")
    false_positives = sum(1 for s in summaries if s.result == "FP")
    false_negatives = sum(1 for s in summaries if s.result == "FN")

    # Compute derived metrics
    total_positive = true_positives + false_negatives
    total_predicted_positive = true_positives + false_positives
    total_correct = true_positives + true_negatives

    accuracy = total_correct / total_test_cases if total_test_cases > 0 else None
    precision = true_positives / total_predicted_positive if total_predicted_positive > 0 else None
    recall = true_positives / total_positive if total_positive > 0 else None

    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None

    return {
        "total_test_cases": total_test_cases,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def test_case_summary_to_dict(summary: TestCaseSummary) -> Dict[str, Any]:
    """Convert TestCaseSummary to dict for API calls."""
    return asdict(summary)


def test_case_full_data_to_dict(full_data: TestCaseFullData) -> Dict[str, Any]:
    """Convert TestCaseFullData to dict for JSON serialization."""
    return asdict(full_data)
