"""WorkflowModule for Artificer CLI integration."""

import os
import shlex
from typing import TYPE_CHECKING, Any

import click

from artificer.cli.feature import ArtificerFeature

from .operations import list_workflows, pause_workflow, resume_workflow
from .workflow import Workflow

if TYPE_CHECKING:
    from artificer.cli.config import ArtificerConfig


class WorkflowFeature(ArtificerFeature):
    """Feature providing CLI commands for workflow management."""

    @classmethod
    def register(cls, cli: click.Group, config: "ArtificerConfig") -> None:
        """Register workflow commands with the CLI."""
        workflows_config = cls._import_workflow_entrypoint(config)

        @cli.group()
        def workflows():
            """Manage workflows."""
            pass

        @workflows.command(name="list")
        @click.option("--status", help="Filter by status (e.g., IN_PROGRESS, COMPLETED)")
        def list_cmd(status: str | None = None):
            """List all workflows."""
            status_filter = status.upper() if status else None
            results = list_workflows(status=status_filter)
            if not results:
                click.echo("No workflows found.")
                return
            click.echo(f"{'WORKFLOW ID':<40} {'STATUS':<12} {'START TIME':<20}")
            click.echo("------------------------------------------------------------------------")
            for wf in results:
                click.echo(f"{wf['workflow_id']:<40} {wf['status']:<12} {wf['start_time']:<20}")

        @workflows.command(name="start")
        @click.argument("workflow_name")
        def start_cmd(workflow_name: str):
            """Start a new workflow execution with an agent TUI."""
            agent_command = workflows_config.get("agent_command")
            if not agent_command:
                click.echo("Error: No agent command configured.", err=True)
                click.echo("Add to pyproject.toml:", err=True)
                click.echo("  [tool.artificer.workflows]", err=True)
                click.echo('  agent_command = "claude"', err=True)
                raise SystemExit(1)

            workflow_class = Workflow._workflow_registry.get(workflow_name)
            if workflow_class is None:
                available = list(Workflow._workflow_registry.keys())
                click.echo(f"Unknown workflow: {workflow_name}", err=True)
                if available:
                    click.echo(f"Available workflows: {', '.join(available)}", err=True)
                raise SystemExit(1)

            prompt = f"Starting a `{workflow_name}` workflow. Start the first step."
            cmd_parts = shlex.split(agent_command)
            cmd_parts.append(prompt)
            os.execvp(cmd_parts[0], cmd_parts)

        @workflows.command(name="resume")
        @click.argument("workflow_id")
        def resume_cmd(workflow_id: str):
            """Resume a paused workflow with an agent TUI."""
            agent_command = workflows_config.get("agent_command")
            if not agent_command:
                click.echo("Error: No agent command configured.", err=True)
                click.echo("Add to pyproject.toml:", err=True)
                click.echo("  [tool.artificer.workflows]", err=True)
                click.echo('  agent_command = "claude"', err=True)
                raise SystemExit(1)

            result = resume_workflow(workflow_id)
            if "error" in result:
                click.echo(f"Error: {result['error']}", err=True)
                raise SystemExit(1)

            prompt = f"Resuming workflow `{workflow_id}`. Continue with the current step."
            cmd_parts = shlex.split(agent_command)
            cmd_parts.append(prompt)
            os.execvp(cmd_parts[0], cmd_parts)

        @workflows.command(name="pause")
        @click.argument("workflow_id")
        def pause_cmd(workflow_id: str):
            """Pause a running workflow."""
            result = pause_workflow(workflow_id)
            if "error" in result:
                click.echo(f"Error: {result['error']}", err=True)
                raise SystemExit(1)
            click.echo(result.get("message", f"Paused workflow: {workflow_id}"))

    @classmethod
    def _import_workflow_entrypoint(cls, config: "ArtificerConfig") -> dict[str, Any]:
        """Import the workflow entrypoint module to register workflows.

        Returns:
            Workflow configuration dict from [tool.artificer.workflows]
        """
        import importlib
        import sys
        from pathlib import Path

        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib

        pyproject_path = Path.cwd() / "pyproject.toml"
        if not pyproject_path.exists():
            return {}

        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)

        workflows_config = pyproject.get("tool", {}).get("artificer", {}).get("workflows", {})
        entrypoint = workflows_config.get("entrypoint")

        if entrypoint:
            try:
                importlib.import_module(entrypoint)
            except ImportError as e:
                click.echo(f"Warning: Could not import workflow entrypoint '{entrypoint}': {e}", err=True)

        return workflows_config
