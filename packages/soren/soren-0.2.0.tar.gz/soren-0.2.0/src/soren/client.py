"""
API client for communicating with the Soren backend service
"""
import os
import requests
from typing import Optional, Dict, Any


class SorenClient:
    """Client for interacting with the Soren backend API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Soren API client

        Args:
            api_key: API key for authentication (defaults to env var SOREN_API_KEY)
            base_url: Base URL for the Soren API (defaults to env var SOREN_API_URL or production URL)
        """
        self.api_key = api_key or os.getenv("SOREN_API_KEY")
        self.base_url = base_url or os.getenv("SOREN_API_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._auth_disabled: Optional[bool] = None

        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def check_auth_status(self) -> Dict[str, Any]:
        """
        Check if the backend has auth disabled.

        Returns:
            Dict with auth_disabled bool and optional default_user info
        """
        try:
            response = self.session.get(f"{self.base_url}/auth/status")
            response.raise_for_status()
            status = response.json()
            self._auth_disabled = status.get("auth_disabled", False)
            return status
        except Exception as e:
            print(f"Warning: Could not check auth status: {e}")
            return {"auth_disabled": False}

    def is_auth_disabled(self) -> bool:
        """Check if auth is disabled (cached after first call)."""
        if self._auth_disabled is None:
            self.check_auth_status()
        return self._auth_disabled or False
    
    def login(self, api_key: str) -> Dict[str, Any]:
        """
        Authenticate with the Soren backend and validate API key.

        Validates if the API key is valid by checking if the user exists.
        If the user exists, return the API key and user info.
        If the user does not exist, return an error.

        Args:
            api_key: User API key

        Returns:
            Response containing API key (as access_token) and user info
        """
        response = self.session.post(
            f"{self.base_url}/auth/validate-api-key",
            json={"api_key": api_key}
        )
        response.raise_for_status()
        return response.json()
    
    def create_run(self, yaml_config: dict, **kwargs) -> Dict[str, Any]:
        """
        Create a new evaluation run

        Args:
            yaml_config: Parsed YAML configuration dictionary from user's machine
            **kwargs: Additional run parameters

        Returns:
            Response containing run ID and details
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")

        yaml_config_dict = dict(yaml_config.items())

        # Create the run --> store in backend and create in frontend
        response = self.session.post(
            f"{self.base_url}/runs",
            json={
                "yaml_config": yaml_config_dict,
            }
        )
        response.raise_for_status()
        return response.json()

    def update_run(self, run_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of a run

        Args:
            run_id: Run ID
            status: New status
        """
        response = self.session.patch(
            f"{self.base_url}/runs/{run_id}",
            json={
                "status": status,
                }
            )
        response.raise_for_status()
        return response.json()

    def upload_output(self, run_id: str, output_content: str) -> Dict[str, Any]:
        """
        Upload the output content to the backend.

        Args:
            run_id: Run ID
            output_content: The output file content as a string

        Returns:
            Response from server
        """
        response = self.session.patch(
            f"{self.base_url}/runs/{run_id}/output",
            json={"output": output_content}
        )
        response.raise_for_status()
        return response.json()

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get details for a specific run

        Args:
            run_id: Run ID

        Returns:
            Run details
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")

        response = self.session.get(f"{self.base_url}/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    def request_upload_urls(self, run_id: str, files: list) -> Dict[str, Any]:
        """
        Request presigned S3 upload URLs from the backend.

        This allows the CLI to upload files directly to S3 without exposing AWS credentials.
        The backend generates temporary presigned URLs that grant upload permission.

        Args:
            run_id: Run ID
            files: List of file metadata dictionaries
                [
                    {
                        "path": "metrics.json",
                        "size_bytes": 1234,
                        "media_type": "application/json"
                    },
                    ...
                ]

        Returns:
            Response containing presigned URLs:
            {
                "upload_urls": [
                    {
                        "path": "metrics.json",
                        "upload_url": "https://s3.amazonaws.com/...",
                        "s3_key": "runs/123/20250101T120000Z/metrics.json"
                    },
                    ...
                ],
                "manifest_upload_url": "https://s3.amazonaws.com/...",
                "manifest_s3_key": "runs/123/20250101T120000Z/manifest.json",
                "timestamp": "20250101T120000Z"
            }
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")

        response = self.session.post(
            f"{self.base_url}/runs/{run_id}/upload-urls",
            json={"files": files}
        )
        response.raise_for_status()
        return response.json()

    def store_metrics(self, run_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store backtest metrics in the backend database.

        This sends the parsed metrics.json data to be stored in the backtest_metrics
        table for efficient querying.

        Args:
            run_id: Run ID
            metrics: Metrics dictionary containing:
                {
                    "total": int,
                    "true_positives": int,
                    "false_positives": int,
                    "true_negatives": int,
                    "false_negatives": int,
                    "precision": float,
                    "recall": float,
                    "f1": float,
                    "accuracy": float
                }

        Returns:
            Response confirming storage:
            {
                "status": "ok",
                "run_id": 123,
                "experiment_id": "exp_abc123",
                "metrics_id": 456,
                "message": "Backtest metrics stored successfully"
            }
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")

        response = self.session.post(
            f"{self.base_url}/runs/{run_id}/metrics",
            json=metrics
        )
        response.raise_for_status()
        return response.json()

    def store_results(self, run_id: str, results: list) -> Dict[str, Any]:
        """
        Store backtest results in the backend database.

        This sends the parsed results.json data to be stored in the backtest_results
        table for efficient querying.

        Args:
            run_id: Run ID
            results: List of result dictionaries:
                [
                    {
                        "row_id": "row_000",
                        "label": true,
                        "prediction": false,
                        "reasoning": "...",
                        "correct": false
                    },
                    ...
                ]

        Returns:
            Response confirming storage:
            {
                "status": "ok",
                "run_id": 123,
                "experiment_id": "exp_abc123",
                "results_count": 132,
                "message": "Backtest results stored successfully (132 rows)"
            }
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")

        response = self.session.post(
            f"{self.base_url}/runs/{run_id}/results",
            json={"results": results}
        )
        response.raise_for_status()
        return response.json()
