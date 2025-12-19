"""
Soren CLI - Command-line interface for Soren AI evaluation framework
"""
from math import e
import yaml
import argparse
import sys
import os
import subprocess
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import __version__
from .client import SorenClient
from .config import SorenConfig
from .validation import build_manifest_entry

def validate_yaml_config(yaml_data: dict) -> tuple:
    """
    Validate YAML configuration has required fields and proper values.

    This performs client-side validation before sending to the backend,
    providing faster feedback to users about configuration errors.

    Required fields:
        - cmd: The command to execute (must be non-empty)
        - run_name: Display name for the evaluation run (must be non-empty)

    Args:
        yaml_data: Parsed YAML configuration dictionary

    Returns:
        tuple: (is_valid: bool, error_message: str)
            - If valid: (True, "")
            - If invalid: (False, "descriptive error message")
    """
    # # REQUIRED FIELDS
    if "cmd" not in yaml_data:
        return False, "YAML configuration must contain 'cmd' field"
    if "run_name" not in yaml_data:
        return False, "YAML configuration must contain 'run_name' field (or legacy 'name')"
    if "project_name" not in yaml_data:
        return False, "YAML configuration must contain 'project_name' field"
    if "eval_type" not in yaml_data:
        return False, "YAML configuration must contain 'eval_type' field"

    # VALIDATE FIELDS ARE NOT EMPTY
    cmd_value = yaml_data["cmd"]
    if not cmd_value or (isinstance(cmd_value, str) and not cmd_value.strip()):
        return False, "Field 'cmd' cannot be empty"
    run_name_value = yaml_data["run_name"]
    if not run_name_value or (isinstance(run_name_value, str) and not run_name_value.strip()):
        return False, "Field 'run_name' cannot be empty"
    project_name_value = yaml_data["project_name"]
    if not project_name_value or (isinstance(project_name_value, str) and not project_name_value.strip()):
        return False, "Field 'project_name' cannot be empty"
    eval_type_value = yaml_data["eval_type"]
    if not eval_type_value or (isinstance(eval_type_value, str) and not eval_type_value.strip()):
        return False, "Field 'eval_type' cannot be empty"

    # All validations passed
    return True, ""


def handle_login(args):
    """Handle the login command with support for self-hosted instances"""
    config = SorenConfig()

    # Determine the API URL
    api_url = _get_api_url(args, config)

    # Save the API URL to config
    config.set_api_url(api_url)

    # Verify connection and check auth status
    print(f"\nConnecting to {api_url}...")
    client = SorenClient(base_url=api_url)

    try:
        auth_status = client.check_auth_status()
        print(f"✓ Connected to {api_url}")

        # Show server info if available
        if auth_status.get("version"):
            print(f"  Server version: {auth_status.get('version')}")

    except Exception as e:
        print(f"✗ Failed to connect to {api_url}")
        print(f"  Error: {e}")
        print("\nPlease check:")
        print("  - The server URL is correct")
        print("  - The server is running and accessible")
        print("  - Any firewalls allow connections on this port")
        sys.exit(1)

    # Check if backend has auth disabled
    if client.is_auth_disabled():
        print("\nℹ Backend running in no-auth mode - API key not required")
        print(f"✓ Configuration saved to {config.config_file}")
        print("\nYou can now run 'soren run <config.yaml>' directly")
        return

    # Auth is enabled - prompt for API key
    print(f"  Auth mode: enabled\n")

    api_key = args.SOREN_API_KEY or input("Enter your API key: ")

    if not api_key or not api_key.strip():
        print("✗ API key cannot be empty")
        sys.exit(1)

    api_key = api_key.strip()

    try:
        # Authenticate with backend
        print("Validating API key...")
        response = client.login(api_key)

        # Store API key locally
        validated_key = response.get('access_token')
        if validated_key:
            config.set_api_key(validated_key)

            # Show user info if available
            user_info = response.get('user', {})
            if user_info.get('email'):
                print(f"✓ Successfully logged in as {user_info.get('email')}")
            else:
                print("✓ Successfully logged in!")

            print(f"  Config saved to {config.config_file}")
        else:
            print("✗ Login failed: No API key received from server")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)


def _get_api_url(args, config: SorenConfig) -> str:
    """
    Determine the API URL from args, environment, config, or user prompt.

    Priority:
    1. --url command line argument
    2. SOREN_API_URL environment variable
    3. Existing config file value (if user confirms)
    4. Interactive prompt

    Returns:
        The API URL to use
    """
    # 1. Check command line argument
    if args.url:
        return args.url.rstrip('/')

    # 2. Check environment variable
    env_url = os.getenv("SOREN_API_URL")
    if env_url:
        print(f"Using API URL from environment: {env_url}")
        return env_url.rstrip('/')

    # 3. Check existing config
    existing_url = config.get_api_url()
    if existing_url:
        use_existing = input(f"Use existing server URL '{existing_url}'? [Y/n]: ").strip().lower()
        if use_existing != 'n':
            return existing_url.rstrip('/')

    # 4. Interactive prompt
    print("\nWhere is your Soren instance running?")
    print("  [1] Soren Cloud (hosted)")
    print("  [2] Self-hosted (your own infrastructure)")
    print()

    choice = input("Enter choice [1]: ").strip()

    if choice == "2":
        # Self-hosted - prompt for URL
        print("\nEnter your Soren server URL")
        print("  Example: http://54.123.45.67:8000")
        print("  Example: https://soren.yourcompany.com")
        print()

        while True:
            url = input("Server URL: ").strip()
            if not url:
                print("✗ URL cannot be empty")
                continue

            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                print("✗ URL must start with http:// or https://")
                continue

            return url.rstrip('/')
    else:
        # Soren Cloud (default) - use localhost for now, or a production URL
        # TODO: Update this to the actual Soren Cloud URL when available
        default_url = "http://localhost:8000"
        print(f"\nUsing default: {default_url}")
        return default_url


def handle_run(args):
    """Handle the run command"""

    """
    config-path: The path to the config file
    - This config file is a YAML file that contains the necessary configs for run

    Pseudocode:
    1. API is parsed to validate each run.
    2. Reads the YAML configuration file for each of the necessary toggles + other for UI.
    3. Spawns their CLI and commands with these toggles.
    4. This creates a new run in my frontend (running)
    5. After it is done, it pulls from the output directory and outputs to backend and my UI.
    6. View on UI
    """
    config = SorenConfig()
    api_key = config.get_api_key()

    # Check if backend has auth disabled
    client_for_check = SorenClient(base_url=config.get_api_url())
    auth_disabled = client_for_check.is_auth_disabled()

    if not api_key and not auth_disabled:
        print("✗ Not logged in. Run 'soren login' first.")
        sys.exit(1)

    if auth_disabled:
        print("ℹ Backend running in no-auth mode - login not required")
        api_key = "no-auth-token"  # Use placeholder token

    print(f"Config path: {args.config_path}")

    # Read the YAML configuration file (user device)
    try:
        with open(args.config_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        # Print configuration summary
        print("\n=== YAML Configuration ===")
        print(yaml.dump(yaml_data, default_flow_style=False))
        print("=" * 26 + "\n")

    except FileNotFoundError:
        print(f"✗ Error: Config file not found at: {args.config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"✗ Error: Invalid YAML format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading config file: {e}")
        sys.exit(1)

    # Validate YAML configuration
    print("=== Validating Configuration ===")
    is_valid, error_msg = validate_yaml_config(yaml_data)
    if not is_valid:
        print(f"✗ Invalid YAML configuration: {error_msg}")
        print("\nRequired fields:")
        print("  - cmd: The command to execute")
        print("  - name: Display name for the run")
        sys.exit(1)
    print("✓ Configuration validated successfully\n")

    # Build command from config
    print("\n=== Building Command ===")
    try:
        command = yaml_data.get("cmd")
        print(f"Command: {command}\n")
    except Exception as e:
        print(f"✗ Error building command: {e}")
        sys.exit(1)
    
    # Create run in backend
    try:
        client = SorenClient(api_key=api_key, base_url=config.get_api_url())
        
        print("Creating a new evaluation run...")
        run = client.create_run(yaml_config=yaml_data)
        run_id = run.get('run_id')
        experiment_id = run.get('experiment_id') or yaml_data.get("experiment_id") or yaml_data.get("experiment-id")
        
        print(f"✓ Run created: {run_id}")
        if experiment_id:
            print(f"Experiment ID: {experiment_id}")
        else:
            print("⚠ No experiment_id returned; experiment manifest updates will be skipped.")
        
    except Exception as e:
        print(f"✗ Failed to create run: {e}")
        sys.exit(1)
    
    # Determine working directory
    working_dir = yaml_data.get("working-directory")
    if not working_dir:
        # Default to directory containing the YAML config file
        working_dir = os.path.dirname(os.path.abspath(args.config_path))
    
    print(f"Working directory: {working_dir}")
    
    # Validate working directory exists
    if not os.path.isdir(working_dir):
        print(f"✗ Error: Working directory does not exist: {working_dir}")
        sys.exit(1)
    
    # Execute command locally
    print("\n=== Executing Command ===")
    print(f"Starting execution at {datetime.now()}")
    print("-" * 50)
    print()
    
    # Execute the command locally (run scripts on user device)
    result = execute_command(command=command, working_dir=working_dir)
    
    print()
    print("-" * 50)
    
    if result["success"]:
        print(f"✓ Command completed successfully!")
        print(f"Exit code: {result['exit_code']}")

        # UPDATE FRONTEND WITH THE RESULT (from In Progress to --> Done)
        client.update_run(
            run_id=run_id,
            status="completed"
            )

        # Support both "output-dir" (hyphenated) and "output_dir" (underscored)
        output_directory = yaml_data.get("output-dir") or yaml_data.get("output_dir")
        if output_directory:
            print(f"\n=== Retrieving Output ===")

            # Resolve to absolute path using working_dir as base when needed
            if not os.path.isabs(output_directory):
                output_directory = os.path.abspath(os.path.join(working_dir, output_directory))
            else:
                output_directory = os.path.abspath(output_directory)

            if not os.path.isdir(output_directory):
                print(f"✗ Error: Output directory does not exist: {output_directory}")
                sys.exit(1)

            print(f"Output directory (resolved): {output_directory}")

            # Collect all files and build manifest entries
            manifest_entries: List[Dict[str, Any]] = []
            file_list_for_backend = []

            for root, _, files in os.walk(output_directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, output_directory)
                    normalized_relative_path = "/".join(relative_path.split(os.sep))

                    # Build manifest entry (includes validation info)
                    manifest_entry = build_manifest_entry(file_path, normalized_relative_path)
                    manifest_entries.append(manifest_entry)

                    # Prepare file info for backend
                    file_list_for_backend.append({
                        "path": normalized_relative_path,
                        "size_bytes": manifest_entry.get("size_bytes", 0),
                        "media_type": manifest_entry.get("media_type", "application/octet-stream")
                    })

            if not manifest_entries:
                print("✗ No files found in output directory")
                sys.exit(1)

            # =====================================================
            # Store metrics and results in Postgres BEFORE S3 upload
            # =====================================================
            print(f"\n=== Storing Metrics & Results in Database ===")

            # Find and store backtest metrics (backtest_metrics.v1)
            metrics_entry = None
            results_entry = None

            for entry in manifest_entries:
                schema_id = entry.get("validation", {}).get("schema_id")
                if schema_id == "backtest_metrics.v1":
                    metrics_entry = entry
                elif schema_id == "backtest_results.v1":
                    results_entry = entry

            # Store backtest metrics if found
            if metrics_entry:
                metrics_path = os.path.join(output_directory, metrics_entry["path"])
                try:
                    with open(metrics_path, 'r') as f:
                        metrics_data = json.load(f)

                    print(f"Storing backtest metrics from {metrics_entry['path']}...")
                    response = client.store_metrics(run_id, metrics_data)
                    print(f"✓ Backtest metrics stored successfully")
                except FileNotFoundError:
                    print(f"⚠ Metrics file not found: {metrics_path}")
                except json.JSONDecodeError as e:
                    print(f"⚠ Failed to parse metrics JSON: {e}")
                except Exception as e:
                    print(f"⚠ Failed to store metrics: {e}")
            else:
                print("ℹ No backtest_metrics.v1 file found, skipping metrics storage")

            # Store backtest results if found
            if results_entry:
                results_path = os.path.join(output_directory, results_entry["path"])
                try:
                    with open(results_path, 'r') as f:
                        results_data = json.load(f)

                    print(f"Storing backtest results from {results_entry['path']}...")
                    response = client.store_results(run_id, results_data)
                    results_count = response.get("results_count", len(results_data))
                    print(f"✓ Backtest results stored successfully ({results_count} rows)")
                except FileNotFoundError:
                    print(f"⚠ Results file not found: {results_path}")
                except json.JSONDecodeError as e:
                    print(f"⚠ Failed to parse results JSON: {e}")
                except Exception as e:
                    print(f"⚠ Failed to store results: {e}")
            else:
                print("ℹ No backtest_results.v1 file found, skipping results storage")

            # =====================================================
            # Upload files to S3 for audit purposes
            # =====================================================
            print(f"\n=== Uploading Files to S3 (Audit) ===")

            # Request presigned URLs from backend
            print(f"Requesting upload URLs for {len(file_list_for_backend)} file(s)...")
            try:
                upload_response = client.request_upload_urls(run_id, file_list_for_backend)
                upload_urls = upload_response.get("upload_urls", [])
                manifest_upload_url = upload_response.get("manifest_upload_url")
                timestamp_prefix = upload_response.get("timestamp")

                if not upload_urls or not manifest_upload_url:
                    print("✗ Failed to get upload URLs from backend")
                    sys.exit(1)

                print(f"✓ Received upload URLs")
            except Exception as e:
                print(f"✗ Failed to request upload URLs: {e}")
                sys.exit(1)

            # Upload files using presigned URLs
            uploaded_count = 0
            failed_uploads = []

            for i, manifest_entry in enumerate(manifest_entries):
                file_path = os.path.join(output_directory, manifest_entry["path"])
                upload_info = upload_urls[i]

                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()

                    import requests
                    response = requests.put(
                        upload_info["upload_url"],
                        data=file_data,
                        headers={'Content-Type': manifest_entry.get("media_type", "application/octet-stream")}
                    )

                    if response.status_code == 200:
                        uploaded_count += 1
                        valid_flag = "valid" if manifest_entry["validation"]["valid"] else "invalid"
                        schema_id = manifest_entry["validation"]["schema_id"]
                        schema_info = f"schema={schema_id}" if schema_id else "schema=none"
                        print(f"✓ Uploaded ({valid_flag}, {schema_info}) {manifest_entry['path']}")

                        # Add S3 key to manifest entry
                        manifest_entry["s3_key"] = upload_info["s3_key"]
                    else:
                        failed_uploads.append((file_path, f"HTTP {response.status_code}"))
                        print(f"⚠ Failed to upload {file_path}: HTTP {response.status_code}")
                except Exception as e:
                    failed_uploads.append((file_path, str(e)))
                    print(f"⚠ Failed to upload {file_path}: {e}")

            # Upload manifest using presigned URL
            manifest_body = json.dumps(
                {
                    "run_id": run_id,
                    "timestamp": timestamp_prefix,
                    "output_dir": output_directory,
                    "files": manifest_entries,
                },
                indent=2,
            )
            try:
                import requests
                response = requests.put(
                    manifest_upload_url,
                    data=manifest_body.encode("utf-8"),
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    print(f"✓ Uploaded manifest")
                else:
                    print(f"⚠ Failed to upload manifest: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠ Failed to upload manifest: {e}")

            if uploaded_count == 0:
                print("✗ No files uploaded; no files found in output directory or all uploads failed.")
                sys.exit(1)

            print(f"✓ Uploaded {uploaded_count} file(s)")
            if failed_uploads:
                print("⚠ Some files failed to upload:")
                for path, error in failed_uploads:
                    print(f"  - {path}: {error}")

        else:
            print("⚠ No output-dir specified in config, skipping output retrieval")
    else:
        print(f"✗ Command failed with exit code: {result['exit_code']}")
        if result["stderr"]:
            print(f"Error: {result['stderr']}")
        sys.exit(1)
    
    return


def get_output(output_dir: str, working_dir: str) -> str:
    """
    Legacy helper for single-file output retrieval (not used by handle_run).
    Prefer the directory-based S3 uploads implemented in handle_run.

    Args:
        output_dir: Directory containing run outputs (relative or absolute)
        working_dir: Working directory to resolve relative paths

    Returns:
        File contents as string, or None if file doesn't exist
    """
    # Handle None or empty output_dir
    if not output_dir:
        print("[CLI] No output directory specified, skipping output retrieval")
        return None

    # Resolve to absolute path on user's machine
    if not os.path.isabs(output_dir):
        full_path = os.path.join(working_dir, output_dir)
    else:
        full_path = output_dir

    # Check if file exists on user's machine
    if not os.path.exists(full_path):
        print(f"[CLI] Warning: Output file not found at {full_path}")
        return None

    # Read entire file from user's machine
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[CLI] Successfully read {len(content)} bytes from {full_path}")
        return content
    except Exception as e:
        print(f"[CLI] Error reading output file: {e}")
        return None

def execute_command(command: str, working_dir: str = None) -> dict:
    """
    Execute a shell command on the local machine with real-time output.
    
    Args:
        command: The full command string to execute
        working_dir: Optional working directory (defaults to current dir)
        
    Returns:
        Dict with execution results: {
            "success": bool,
            "exit_code": int,
            "stdout": str,
            "stderr": str
        }
    """
    print(f"Executing: {command}")
    print(f"Working directory: {working_dir or os.getcwd()}")
    print()
    print(command)
    
    try:
        # Start the process
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            cwd=working_dir
        )
        
        # Collect output while streaming to console
        stdout_lines = []
        stderr_lines = []
        
        # Read stdout in real-time
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(stdout_line, end='')
                stdout_lines.append(stdout_line)
            
            # Check if process has finished
            if process.poll() is not None:
                # Read any remaining output
                remaining = process.stdout.read()
                if remaining:
                    print(remaining, end='')
                    stdout_lines.append(remaining)
                break
        
        # Read stderr after process completes
        stderr_output = process.stderr.read()
        if stderr_output:
            print(stderr_output, file=sys.stderr)
            stderr_lines.append(stderr_output)
        
        # Get exit code
        exit_code = process.returncode
        
        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines)
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command not found: {command.split()[0]}"
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}"
        }


def build_command_from_config(yaml_config: dict) -> str:
    """
    Build a shell command from YAML configuration.

    Args:
        yaml_config: Parsed YAML configuration

    Returns:
        Complete command string
    """
    # Reserved keys that are not CLI flags
    # These are metadata fields stored in the database but not passed to the command
    #
    # Categories:
    # - System fields: cmd, name, description
    # - Path fields: config-path, output-dir/output_dir, working-directory
    # - Metadata fields: Custom fields that may be used for tracking/filtering in UI
    #
    # Note: Any field not in this list will be passed as a CLI flag (--field-name value)
    RESERVED_KEYS = {
        # Core system fields (required)
        "cmd",                    # The command to execute
        "name",                   # Display name in UI (legacy)
        "run_name",               # Display name in UI (canonical)
        "project_name",           # Project name (metadata that is required)

        # Optional metadata fields (stored in DB, not passed to CLI)
        "description",            # Run description
        "project_description",    # Project description
        "config-path",            # Path to the YAML config file
        "output-dir",             # Directory where evaluation output is written
        "output_dir",             # Directory where evaluation output is written
        "working-directory",      # Working directory for command execution

        # Common metadata fields (customize based on your needs)
        # These are stored in yaml_metadata JSONB column for filtering/analysis
        "model",                  # Model name (e.g., "gpt-4")
        "prompt-variant",         # Prompt variant identifier
        "prompt_variant",         # Alternative underscore format
        "experiment-name",        # Experiment name
        "experiment_name",        # Alternative underscore format
        "tags",                   # Custom tags for categorization
        "version",                # Version identifier
    }
    
    # The command is the base command
    base_cmd = yaml_config.get("cmd")
    if not base_cmd:
        raise ValueError("YAML config must contain 'cmd' field")
    return base_cmd

def handle_logout(args):
    """Handle the logout command"""
    config = SorenConfig()
    config.clear()
    print("✓ Logged out successfully")


def handle_status(args):
    """Handle the status command - show current configuration"""
    config = SorenConfig()

    print("\n=== Soren CLI Status ===\n")

    # Show config file location
    print(f"Config file: {config.config_file}")
    print()

    # Show API URL
    api_url = config.get_api_url()
    if api_url:
        print(f"Server URL: {api_url}")
    else:
        print("Server URL: (not configured)")

    # Show API key status (masked)
    api_key = config.get_api_key()
    if api_key:
        # Show masked key (first 10 chars + ...)
        masked = api_key[:10] + "..." if len(api_key) > 10 else api_key
        print(f"API key:    {masked}")
    else:
        print("API key:    (not set)")

    print()

    # Try to connect to server if URL is configured
    if api_url:
        print("Checking server connection...")
        client = SorenClient(base_url=api_url)
        try:
            auth_status = client.check_auth_status()
            print(f"✓ Server is reachable")

            if auth_status.get("auth_disabled"):
                print("  Auth mode: disabled (no-auth)")
            else:
                print("  Auth mode: enabled")

            if auth_status.get("version"):
                print(f"  Version: {auth_status.get('version')}")

        except Exception as e:
            print(f"✗ Cannot reach server: {e}")
    else:
        print("Run 'soren login' to configure your connection")

    print()


def main():
    """Main entry point for the Soren CLI"""

    # Main parser
    parser = argparse.ArgumentParser(
        prog="soren",
        description="Soren AI - Evaluation framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Global version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"soren {__version__}",
    )
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # API login command
    login_parser = subparsers.add_parser(
        "login",
        help="Authenticate with Soren",
        description="Connect to a Soren instance and authenticate. Supports both Soren Cloud and self-hosted deployments."
    )
    login_parser.add_argument(
        "--url",
        help="Soren server URL (e.g., http://your-server:8000). For self-hosted instances."
    )
    login_parser.add_argument(
        "--SOREN_API_KEY",
        help="Your Soren API key (can also be entered interactively)"
    )
    
    # Run command (will be edited later to support their CLI)

    # THEIR EVALS CLI
    # 3. **Local**: Run `poetry run evaluate-agents-performance`
    # - **Base mode**: `poetry run evaluate-agents-performance`
    # - **With feature flags**: `poetry run evaluate-agents-performance --feature-flag is_opted_in_to_gold_examples`
    # - **With baseline agents**: `poetry run evaluate-agents-performance --include-baseline`
    # - **On backtesting data**: `poetry run evaluate-agents-performance --end-to-end`
    run_parser = subparsers.add_parser("run", help="Create and run an evaluation")
    run_parser.add_argument("config_path", help="The path to the config file")
    
    # Logout command
    logout_parser = subparsers.add_parser("logout", help="Clear stored credentials")

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show current configuration and connection status"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Route to command handlers
    if args.command == "login":
        handle_login(args)
    elif args.command == "run":
        handle_run(args)
    elif args.command == "logout":
        handle_logout(args)
    elif args.command == "status":
        handle_status(args)
    else:
        print(f"Command '{args.command}' not yet implemented")


if __name__ == "__main__":
    main()
