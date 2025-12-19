#!/usr/bin/env python3
"""
CLI Application for Text Vectorization
Command-line interface for embedding text using embed-client.

This CLI is fully based on the embed-client library and uses:
- ClientFactory for client creation
- ClientConfig for configuration management
- response_parsers for data extraction
- All authentication methods (API Key, JWT, Basic, Certificate)
- Queue management commands

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from embed_client.async_client import EmbeddingServiceAsyncClient
from embed_client.client_factory import ClientFactory
from embed_client.config import ClientConfig
from embed_client.response_parsers import extract_embeddings, extract_embedding_data


class VectorizationCLI:
    """CLI application for text vectorization using embed-client library."""

    def __init__(self):
        self.client: Optional[EmbeddingServiceAsyncClient] = None

    async def connect(
        self,
        config: Optional[ClientConfig] = None,
        config_dict: Optional[Dict[str, Any]] = None,
    ):
        """Connect to embedding service using ClientFactory."""
        try:
            if config:
                self.client = EmbeddingServiceAsyncClient.from_config(config)
            elif config_dict:
                self.client = EmbeddingServiceAsyncClient(config_dict=config_dict)
            else:
                # Use ClientFactory.from_environment() as fallback
                self.client = ClientFactory.from_environment()

            await self.client.__aenter__()
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}", file=sys.stderr)
            return False

    async def disconnect(self):
        """Disconnect from embedding service."""
        if self.client:
            await self.client.close()

    async def health_check(self) -> bool:
        """Check service health."""
        try:
            result = await self.client.health()
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}", file=sys.stderr)
            return False

    async def vectorize_texts(
        self,
        texts: List[str],
        output_format: str = "json",
        show_full_data: bool = False,
    ) -> Optional[List[List[float]]]:
        """Vectorize texts using client.cmd() and response_parsers.

        Notes:
            - Uses error_policy="continue" to align with Embedding Service contract:
              per-item validation errors are returned in result.data.results[*].error.
        """
        try:
            # Always use error_policy="continue" for batch safety and per-item errors
            params = {"texts": texts, "error_policy": "continue"}
            result = await self.client.cmd("embed", params=params)

            # Use response_parsers from library
            if show_full_data:
                # Extract full embedding data
                data = extract_embedding_data(result)
                if output_format == "json":
                    print(json.dumps(data, indent=2))
                else:
                    # For other formats, extract just embeddings
                    embeddings = extract_embeddings(result)
                    if output_format == "csv":
                        self._print_csv(embeddings)
                    elif output_format == "vectors":
                        self._print_vectors(embeddings)
                return None
            else:
                # Extract just embeddings
                embeddings = extract_embeddings(result)
                if output_format == "json":
                    print(json.dumps(embeddings, indent=2))
                elif output_format == "csv":
                    self._print_csv(embeddings)
                elif output_format == "vectors":
                    self._print_vectors(embeddings)
                return embeddings

        except Exception as e:
            print(f"❌ Vectorization failed: {e}", file=sys.stderr)
            return None

    def _print_csv(self, embeddings: List[List[float]]):
        """Print embeddings in CSV format."""
        for i, embedding in enumerate(embeddings):
            print(f"text_{i}," + ",".join(map(str, embedding)))

    def _print_vectors(self, embeddings: List[List[float]]):
        """Print embeddings as vectors."""
        for i, embedding in enumerate(embeddings):
            print(f"Text {i}: [{', '.join(map(str, embedding))}]")

    async def get_help(self, command: Optional[str] = None):
        """Get help information."""
        try:
            if command:
                result = await self.client.cmd("help", params={"command": command})
            else:
                result = await self.client.cmd("help")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Help request failed: {e}", file=sys.stderr)

    async def get_commands(self):
        """Get available commands."""
        try:
            result = await self.client.get_commands()
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Commands request failed: {e}", file=sys.stderr)

    async def queue_list(self, status: Optional[str] = None, limit: Optional[int] = None):
        """List queued commands."""
        try:
            result = await self.client.list_queued_commands(status=status, limit=limit)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to list queue: {e}", file=sys.stderr)

    async def queue_status(self, job_id: str):
        """Get job status."""
        try:
            result = await self.client.job_status(job_id)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to get job status: {e}", file=sys.stderr)

    async def queue_cancel(self, job_id: str):
        """Cancel a job."""
        try:
            result = await self.client.cancel_command(job_id)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to cancel job: {e}", file=sys.stderr)

    async def queue_wait(self, job_id: str, timeout: float = 60.0, poll_interval: float = 1.0):
        """Wait for job completion."""
        try:
            result = await self.client.wait_for_job(job_id, timeout=timeout, poll_interval=poll_interval)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to wait for job: {e}", file=sys.stderr)

    async def queue_logs(self, job_id: str):
        """Get job logs."""
        try:
            result = await self.client.get_job_logs(job_id)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to get job logs: {e}", file=sys.stderr)


def create_config_from_args(args) -> Dict[str, Any]:
    """Create configuration from command line arguments using ClientFactory pattern."""
    config = {
        "server": {"host": args.host, "port": args.port},
        "auth": {"method": "none"},
        "ssl": {"enabled": False},
        "client": {"timeout": getattr(args, "timeout", 30.0)},
    }

    # Add authentication if specified
    if args.api_key:
        config["auth"]["method"] = "api_key"
        config["auth"]["api_keys"] = {"user": args.api_key}
        if hasattr(args, "api_key_header") and args.api_key_header:
            config["auth"]["api_key_header"] = args.api_key_header
    elif hasattr(args, "jwt_secret") and args.jwt_secret:
        config["auth"]["method"] = "jwt"
        config["auth"]["jwt"] = {
            "secret": args.jwt_secret,
            "username": getattr(args, "jwt_username", ""),
            "password": getattr(args, "jwt_password", ""),
        }
    elif hasattr(args, "basic_username") and args.basic_username:
        config["auth"]["method"] = "basic"
        config["auth"]["basic"] = {
            "username": args.basic_username,
            "password": getattr(args, "basic_password", ""),
        }

    # Add SSL if specified
    if args.ssl or args.cert_file or args.key_file:
        config["ssl"]["enabled"] = True
        if args.cert_file:
            config["ssl"]["cert_file"] = args.cert_file
        if args.key_file:
            config["ssl"]["key_file"] = args.key_file
        if args.ca_cert_file:
            config["ssl"]["ca_cert_file"] = args.ca_cert_file

    return config


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="CLI Application for Text Vectorization (fully based on embed-client library)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vectorize text from command line
  python -m embed_client vectorize "hello world" "test text"
  
  # Vectorize text from file
  python -m embed_client vectorize --file texts.txt
  
  # Use HTTPS with API key authentication
  python -m embed_client vectorize "hello world" --host https://localhost --port 8443 --api-key your-key
  
  # Use mTLS with client certificates
  python -m embed_client vectorize "hello world" --ssl --cert-file client.crt --key-file client.key
  
  # Use JWT authentication
  python -m embed_client vectorize "hello" --jwt-secret secret --jwt-username user --jwt-password pass
  
  # Use config file
  python -m embed_client --config config.json vectorize "hello"
  
  # Queue management
  python -m embed_client queue-list
  python -m embed_client queue-status JOB_ID
  python -m embed_client queue-cancel JOB_ID
  python -m embed_client queue-wait JOB_ID
  
  # Get help from service
  python -m embed_client help
  
  # Check service health
  python -m embed_client health
        """,
    )

    # Global options
    parser.add_argument("--config", "-c", help="Path to configuration file (JSON or YAML)")
    parser.add_argument(
        "--host",
        default="http://localhost",
        help="Server host (default: http://localhost)",
    )
    parser.add_argument("--port", type=int, default=8001, help="Server port (default: 8001)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")

    # Authentication options
    auth_group = parser.add_argument_group("authentication")
    auth_group.add_argument("--api-key", help="API key for authentication")
    auth_group.add_argument("--api-key-header", help="API key header name (default: X-API-Key)")
    auth_group.add_argument("--jwt-secret", help="JWT secret for authentication")
    auth_group.add_argument("--jwt-username", help="JWT username")
    auth_group.add_argument("--jwt-password", help="JWT password")
    auth_group.add_argument("--basic-username", help="Basic auth username")
    auth_group.add_argument("--basic-password", help="Basic auth password")

    # SSL/TLS options
    ssl_group = parser.add_argument_group("ssl/tls")
    ssl_group.add_argument("--ssl", action="store_true", help="Enable SSL/TLS")
    ssl_group.add_argument("--cert-file", help="Client certificate file")
    ssl_group.add_argument("--key-file", help="Client private key file")
    ssl_group.add_argument("--ca-cert-file", help="CA certificate file")

    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Vectorize command
    vectorize_parser = subparsers.add_parser("vectorize", help="Vectorize text")
    vectorize_parser.add_argument("texts", nargs="*", help="Texts to vectorize")
    vectorize_parser.add_argument("--file", "-f", help="File containing texts (one per line)")
    vectorize_parser.add_argument(
        "--format",
        choices=["json", "csv", "vectors"],
        default="json",
        help="Output format (default: json)",
    )
    vectorize_parser.add_argument(
        "--full-data",
        action="store_true",
        help="Show full embedding data (body, embedding, tokens, bm25_tokens)",
    )

    # Health command
    subparsers.add_parser("health", help="Check service health")

    # Help command
    help_parser = subparsers.add_parser("help", help="Get help from service")
    help_parser.add_argument("--command", help="Specific command to get help for")

    # Commands command
    subparsers.add_parser("commands", help="Get available commands")

    # Queue commands
    queue_list_parser = subparsers.add_parser("queue-list", help="List queued commands")
    queue_list_parser.add_argument("--status", help="Filter by status")
    queue_list_parser.add_argument("--limit", type=int, help="Limit number of results")

    queue_status_parser = subparsers.add_parser("queue-status", help="Get job status")
    queue_status_parser.add_argument("job_id", help="Job identifier")

    queue_cancel_parser = subparsers.add_parser("queue-cancel", help="Cancel a job")
    queue_cancel_parser.add_argument("job_id", help="Job identifier")

    queue_wait_parser = subparsers.add_parser("queue-wait", help="Wait for job completion")
    queue_wait_parser.add_argument("job_id", help="Job identifier")
    queue_wait_parser.add_argument("--timeout", type=float, default=60.0, help="Timeout in seconds")
    queue_wait_parser.add_argument("--poll-interval", type=float, default=1.0, help="Poll interval in seconds")

    queue_logs_parser = subparsers.add_parser("queue-logs", help="Get job logs")
    queue_logs_parser.add_argument("job_id", help="Job identifier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load configuration
    config = None
    config_dict = None

    if args.config:
        # Load from config file using ClientConfig
        config = ClientConfig(args.config)
        config.load_config()
    else:
        # Create config from command line arguments
        config_dict = create_config_from_args(args)

    # Create CLI instance
    cli = VectorizationCLI()

    try:
        # Connect to service
        if not await cli.connect(config=config, config_dict=config_dict):
            return 1

        # Execute command
        if args.command == "vectorize":
            texts = args.texts
            if args.file:
                with open(args.file, "r") as f:
                    texts.extend(line.strip() for line in f if line.strip())

            if not texts:
                print("❌ No texts provided", file=sys.stderr)
                return 1

            await cli.vectorize_texts(texts, args.format, args.full_data)

        elif args.command == "health":
            await cli.health_check()

        elif args.command == "help":
            await cli.get_help(getattr(args, "command", None))

        elif args.command == "commands":
            await cli.get_commands()

        elif args.command == "queue-list":
            await cli.queue_list(getattr(args, "status", None), getattr(args, "limit", None))

        elif args.command == "queue-status":
            await cli.queue_status(args.job_id)

        elif args.command == "queue-cancel":
            await cli.queue_cancel(args.job_id)

        elif args.command == "queue-wait":
            await cli.queue_wait(
                args.job_id,
                timeout=getattr(args, "timeout", 60.0),
                poll_interval=getattr(args, "poll_interval", 1.0),
            )

        elif args.command == "queue-logs":
            await cli.queue_logs(args.job_id)

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
    finally:
        await cli.disconnect()


def cli_main():
    """Synchronous entry point for CLI command."""
    return asyncio.run(main())


if __name__ == "__main__":
    sys.exit(cli_main())
