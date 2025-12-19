"""Git-like commands for flow management."""

import json
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from langflow_cli.git_config import (
    add_remote,
    list_remotes,
    remove_remote,
    set_current_remote,
    set_current_branch,
    get_current_remote,
    get_current_branch,
    get_current_selection,
)
from langflow_cli.git_client import GitHubClient
from langflow_cli.api_client import LangflowAPIClient
from langflow_cli.config import get_default_profile
from langflow_cli.utils import print_json


console = Console()


@click.group()
def git():
    """Git-like commands for managing flows in GitHub repositories."""
    pass


# Remote Management Commands

@git.group()
def remote():
    """Manage Git remotes (origins)."""
    pass


@remote.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--auth-method", type=click.Choice(["gh_cli", "token"]), default="gh_cli", help="Authentication method")
@click.option("--token", help="GitHub token (required if auth-method is token)")
def remote_add(name: str, url: str, auth_method: str, token: Optional[str]):
    """Register a new remote (origin)."""
    try:
        if auth_method == "token" and not token:
            console.print("[red]✗[/red] Token required when using token authentication")
            raise click.Abort()
        
        add_remote(name, url, auth_method, token)
        console.print(f"[green]✓[/green] Remote '{name}' added successfully")
        console.print(f"[dim]URL: {url}[/dim]")
        console.print(f"[dim]Auth method: {auth_method}[/dim]")
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to add remote: {str(e)}")
        raise click.Abort()


@remote.command("list")
def remote_list():
    """List all registered remotes."""
    try:
        remotes = list_remotes()
        
        if not remotes:
            console.print("[yellow]No remotes registered.[/yellow]")
            return
        
        table = Table(title="Git Remotes")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="green")
        table.add_column("Auth Method", style="magenta")
        
        for name, config in remotes.items():
            table.add_row(
                name,
                config["url"],
                config.get("auth_method", "gh_cli")
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list remotes: {str(e)}")
        raise click.Abort()


@remote.command("remove")
@click.argument("name")
def remote_remove(name: str):
    """Remove a remote."""
    try:
        remove_remote(name)
        console.print(f"[green]✓[/green] Remote '{name}' removed successfully")
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove remote: {str(e)}")
        raise click.Abort()


@remote.command("select")
@click.argument("name")
@click.option("--profile", help="Profile to use (overrides default)")
def remote_select(name: str, profile: Optional[str]):
    """Set the active remote (origin)."""
    try:
        profile_name = profile or get_default_profile()
        if not profile_name:
            raise ValueError("No profile selected. Use 'langflow-cli env register' to create one.")
        
        # Verify remote exists
        from langflow_cli.git_config import get_remote
        get_remote(name)
        
        set_current_remote(profile_name, name)
        console.print(f"[green]✓[/green] Remote '{name}' selected for profile '{profile_name}'")
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to select remote: {str(e)}")
        raise click.Abort()


# Branch Management Commands

@git.command("branch")
@click.argument("action", type=click.Choice(["list"]))
@click.option("--remote", help="Remote name (overrides current selection)")
@click.option("--profile", help="Profile to use (overrides default)")
def branch(action: str, remote: Optional[str], profile: Optional[str]):
    """List available branches."""
    try:
        profile_name = profile or get_default_profile()
        if not profile_name:
            raise ValueError("No profile selected. Use 'langflow-cli env register' to create one.")
        
        remote_name = remote or get_current_remote(profile_name)
        if not remote_name:
            raise ValueError("No remote selected. Use 'langflow-cli git remote select <name>' first.")
        
        client = GitHubClient(remote_name)
        branches = client.get_branches()
        
        if not branches:
            console.print("[yellow]No branches found.[/yellow]")
            return
        
        current_branch = get_current_branch(profile_name)
        
        table = Table(title=f"Branches in {remote_name}")
        table.add_column("Branch", style="cyan")
        table.add_column("Status", style="green")
        
        for branch_name in sorted(branches):
            status = "← current" if branch_name == current_branch else ""
            table.add_row(branch_name, status)
        
        console.print(table)
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list branches: {str(e)}")
        raise click.Abort()


@git.command("checkout")
@click.argument("branch_name")
@click.option("--remote", help="Remote name (overrides current selection)")
@click.option("--profile", help="Profile to use (overrides default)")
def checkout(branch_name: str, remote: Optional[str], profile: Optional[str]):
    """Select/checkout a branch."""
    try:
        profile_name = profile or get_default_profile()
        if not profile_name:
            raise ValueError("No profile selected. Use 'langflow-cli env register' to create one.")
        
        remote_name = remote or get_current_remote(profile_name)
        if not remote_name:
            raise ValueError("No remote selected. Use 'langflow-cli git remote select <name>' first.")
        
        # Verify branch exists
        client = GitHubClient(remote_name)
        branches = client.get_branches()
        
        if branch_name not in branches:
            console.print(f"[red]✗[/red] Branch '{branch_name}' not found")
            console.print(f"[yellow]Available branches: {', '.join(branches)}[/yellow]")
            raise click.Abort()
        
        set_current_branch(profile_name, branch_name)
        console.print(f"[green]✓[/green] Switched to branch '{branch_name}'")
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to checkout branch: {str(e)}")
        raise click.Abort()


# Push/Pull Commands

@git.command("push")
@click.argument("flow_id")
@click.option("--remote", help="Remote name (overrides current selection)")
@click.option("--branch", help="Branch name (overrides current selection)")
@click.option("--message", "-m", help="Commit message")
@click.option("--profile", help="Profile to use (overrides default)")
def push(flow_id: str, remote: Optional[str], branch: Optional[str], message: Optional[str], profile: Optional[str]):
    """Push a flow to GitHub repository."""
    try:
        profile_name = profile or get_default_profile()
        if not profile_name:
            raise ValueError("No profile selected. Use 'langflow-cli env register' to create one.")
        
        # Get Langflow flow
        langflow_client = LangflowAPIClient(profile_name=profile_name)
        flow = langflow_client.get_flow(flow_id)
        
        # Get project information
        project_id = flow.get("folder_id") or flow.get("project_id")
        project_name = None
        
        if project_id:
            projects = langflow_client.list_projects()
            project = next((p for p in projects if p.get("id", p.get("project_id")) == project_id), None)
            if not project:
                raise ValueError(f"Project not found: {project_id}")
            project_name = project.get("name", "Unknown")
        
        # Get remote and branch
        remote_name = remote or get_current_remote(profile_name)
        if not remote_name:
            raise ValueError("No remote selected. Use 'langflow-cli git remote select <name>' first.")
        
        branch_name = branch or get_current_branch(profile_name)
        if not branch_name:
            raise ValueError("No branch selected. Use 'langflow-cli git checkout <branch>' first.")
        
        # Initialize GitHub client
        github_client = GitHubClient(remote_name)
        
        # Sanitize names
        if project_name:
            sanitized_project = GitHubClient.sanitize_name(project_name)
        else:
            sanitized_project = "_no_project"
        
        sanitized_flow = GitHubClient.sanitize_name(flow.get("name", "Unnamed"))
        flow_id_str = str(flow_id)
        
        # Create file path
        file_path = f"{sanitized_project}/{sanitized_flow}_{flow_id_str}.json"
        
        # Serialize flow to JSON
        flow_json = json.dumps(flow, indent=2, ensure_ascii=False, default=str)
        
        # Create commit message
        commit_message = message or f"Push flow: {flow.get('name', flow_id)}"
        
        # Push to GitHub
        console.print(f"[cyan]Pushing flow to {remote_name}/{branch_name}...[/cyan]")
        github_client.create_or_update_file(file_path, flow_json, commit_message, branch_name)
        
        console.print(f"[green]✓[/green] Flow pushed successfully")
        console.print(f"[dim]File: {file_path}[/dim]")
        if project_name:
            console.print(f"[dim]Project: {project_name}[/dim]")
        else:
            console.print(f"[yellow]Note: Flow has no project association[/yellow]")
        console.print(f"[dim]Branch: {branch_name}[/dim]")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to push flow: {str(e)}")
        raise click.Abort()


@git.command("pull")
@click.argument("flow_path")
@click.option("--remote", help="Remote name (overrides current selection)")
@click.option("--branch", help="Branch name (overrides current selection)")
@click.option("--project-id", help="Project ID to associate the flow with")
@click.option("--project-name", help="Project name to associate the flow with")
@click.option("--profile", help="Profile to use (overrides default)")
@click.option("--ignore-version-check", is_flag=True, help="Ignore version mismatch warning")
def pull(
    flow_path: str,
    remote: Optional[str],
    branch: Optional[str],
    project_id: Optional[str],
    project_name: Optional[str],
    profile: Optional[str],
    ignore_version_check: bool
):
    """Pull a flow from GitHub repository to Langflow."""
    try:
        profile_name = profile or get_default_profile()
        if not profile_name:
            raise ValueError("No profile selected. Use 'langflow-cli env register' to create one.")
        
        # Get remote and branch
        remote_name = remote or get_current_remote(profile_name)
        if not remote_name:
            raise ValueError("No remote selected. Use 'langflow-cli git remote select <name>' first.")
        
        branch_name = branch or get_current_branch(profile_name)
        if not branch_name:
            raise ValueError("No branch selected. Use 'langflow-cli git checkout <branch>' first.")
        
        # Initialize GitHub client
        github_client = GitHubClient(remote_name)
        
        # Determine file path
        # If flow_path contains a slash, treat as full path
        # Otherwise, search for the file in all project folders
        if "/" in flow_path:
            file_path = flow_path
        else:
            # Search for file matching the pattern
            matches = github_client.find_files_by_pattern(flow_path, "", branch_name)
            if not matches:
                raise ValueError(f"File not found: {flow_path}")
            if len(matches) > 1:
                console.print(f"[yellow]Multiple files found matching '{flow_path}':[/yellow]")
                for match in matches:
                    console.print(f"  - {match}")
                raise ValueError("Multiple files found. Please specify full path.")
            file_path = matches[0]
        
        # Get file from GitHub
        console.print(f"[cyan]Pulling flow from {remote_name}/{branch_name}...[/cyan]")
        flow_json = github_client.get_file(file_path, branch_name)
        flow_data = json.loads(flow_json)
        
        # Get Langflow client
        langflow_client = LangflowAPIClient(profile_name=profile_name)
        projects_list = langflow_client.list_projects()
        
        # Resolve project
        resolved_project_id = None
        
        if project_id:
            # Validate project-id
            project_ids = [str(p.get("id", p.get("project_id", ""))) for p in projects_list]
            if str(project_id) not in project_ids:
                raise ValueError(f"Project not found: {project_id}")
            resolved_project_id = project_id
        elif project_name:
            # Find project by name
            matching_project = next(
                (p for p in projects_list if p.get("name") == project_name),
                None
            )
            if not matching_project:
                raise ValueError(f"Project not found: {project_name}")
            resolved_project_id = matching_project.get("id", matching_project.get("project_id"))
        else:
            # Try to infer from file path (project folder name)
            # Extract project folder from path
            path_parts = file_path.split("/")
            if len(path_parts) > 1:
                project_folder = path_parts[0]
                # Try to find project by matching sanitized name
                for project in projects_list:
                    sanitized = GitHubClient.sanitize_name(project.get("name", ""))
                    if sanitized == project_folder:
                        resolved_project_id = project.get("id", project.get("project_id"))
                        break
        
        # If still no project, use the one from flow_data
        if not resolved_project_id:
            resolved_project_id = flow_data.get("folder_id") or flow_data.get("project_id")
        
        # Validate project exists if project_id is provided
        if resolved_project_id:
            project_ids = [str(p.get("id", p.get("project_id", ""))) for p in projects_list]
            if str(resolved_project_id) not in project_ids:
                console.print(f"[yellow]Warning: Project {resolved_project_id} not found. Flow will be created without project association.[/yellow]")
                resolved_project_id = None
        
        # Update flow_data with resolved project
        if resolved_project_id:
            flow_data["folder_id"] = resolved_project_id
        
        # Check if flow already exists (by ID)
        flow_id = flow_data.get("id") or flow_data.get("flow_id")
        flow_name = flow_data.get("name", "Unnamed")
        
        # Check version compatibility
        if "last_tested_version" in flow_data and not ignore_version_check:
            version_info = langflow_client.get_version()
            current_version = version_info.get("version")
            last_tested = flow_data.get("last_tested_version")
            
            if current_version and last_tested:
                current_version_str = str(current_version).strip()
                last_tested_str = str(last_tested).strip()
                
                if current_version_str != last_tested_str:
                    console.print(
                        f"\n[yellow]⚠[/yellow]  Version mismatch detected:\n"
                        f"  Flow was tested with version: [cyan]{last_tested_str}[/cyan]\n"
                        f"  Current environment version: [cyan]{current_version_str}[/cyan]\n"
                        f"  Use [bold]--ignore-version-check[/bold] to proceed anyway.\n"
                    )
                    if not click.confirm("Continue with flow pull?"):
                        console.print("[yellow]Flow pull cancelled.[/yellow]")
                        raise click.Abort()
        
        # Create or update flow
        if flow_id:
            try:
                # Try to get existing flow
                existing_flow = langflow_client.get_flow(flow_id)
                # Update existing flow
                result = langflow_client.update_flow(flow_id, flow_data)
                console.print(f"[green]✓[/green] Flow updated successfully")
            except Exception:
                # Flow doesn't exist, create new one
                result = langflow_client.create_flow(flow_name, flow_data)
                console.print(f"[green]✓[/green] Flow created successfully")
        else:
            # No ID, create new flow
            result = langflow_client.create_flow(flow_name, flow_data)
            console.print(f"[green]✓[/green] Flow created successfully")
        
        # Display result
        result_id = result.get("id", result.get("flow_id", "N/A"))
        result_name = result.get("name", "N/A")
        result_project_id = result.get("folder_id", result.get("project_id", "N/A"))
        
        # Get project name
        result_project_name = "N/A"
        if result_project_id and result_project_id != "N/A":
            project = next(
                (p for p in projects_list if p.get("id", p.get("project_id")) == result_project_id),
                None
            )
            if project:
                result_project_name = project.get("name", "N/A")
        
        filtered_result = {
            "id": result_id,
            "name": result_name,
            "project_id": result_project_id,
            "project_name": result_project_name
        }
        
        print_json(filtered_result, console)
        
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to pull flow: {str(e)}")
        raise click.Abort()

