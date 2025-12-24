"""Main CLI entry point for Langflow CLI."""

import click
from langflow_cli.commands import env as env_commands
from langflow_cli.commands import settings as settings_commands
from langflow_cli.commands import flows as flows_commands
from langflow_cli.commands import projects as projects_commands
from langflow_cli.commands import git as git_commands
from langflow_cli.commands import status as status_command


@click.group()
def cli():
    """Langflow CLI - Manage Langflow environments and resources."""
    pass


# Register command groups
cli.add_command(env_commands.env, name="env")
cli.add_command(settings_commands.settings, name="settings")
cli.add_command(flows_commands.flows, name="flows")
cli.add_command(projects_commands.projects, name="projects")
cli.add_command(git_commands.git, name="git")
cli.add_command(status_command.status, name="status")


def main():
    """Entry point for the langflow-cli command."""
    cli()

