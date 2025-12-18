"""
FlowMason CLI.

Command-line interface for FlowMason pipeline orchestration.

Usage:
    flowmason run pipelines/main.pipeline.json
    flowmason validate pipelines/
    flowmason studio start
"""

from flowmason_core.cli.main import app

__all__ = ["app"]
