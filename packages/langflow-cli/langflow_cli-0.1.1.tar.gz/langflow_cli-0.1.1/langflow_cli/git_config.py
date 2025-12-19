"""Git configuration management for Langflow CLI."""

import configparser
import os
from pathlib import Path
from typing import Optional, Dict, Tuple


def get_git_config_path() -> Path:
    """Returns the path to the Git config file."""
    return get_config_dir() / "git_config"


def get_config_dir() -> Path:
    """Returns the path to the ~/.langflow-cli directory."""
    return Path.home() / ".langflow-cli"


def _ensure_git_config_file() -> None:
    """Create the Git config file if it doesn't exist."""
    config_dir = get_config_dir()
    config_dir.mkdir(mode=0o700, exist_ok=True)
    
    config_path = get_git_config_path()
    if not config_path.exists():
        config_path.touch(mode=0o644)
        # Initialize with empty file
        config = configparser.ConfigParser()
        with open(config_path, "w") as f:
            config.write(f)


def add_remote(remote_name: str, url: str, auth_method: str = "gh_cli", token: Optional[str] = None) -> None:
    """
    Add or update a Git remote.
    
    Args:
        remote_name: Name of the remote (e.g., "origin")
        url: Repository URL (must be a GitHub URL)
        auth_method: Authentication method ("gh_cli" or "token")
        token: Optional token for token-based auth
    """
    _ensure_git_config_file()
    
    # Validate GitHub URL (HTTPS, HTTP, or SSH)
    # HTTPS: https://github.com/... or https://<domain>/...
    # SSH: git@<domain>:... or ssh://git@<domain>/...
    is_https = url.startswith("https://") or url.startswith("http://")
    is_ssh = url.startswith("git@") or url.startswith("ssh://git@")
    
    if not (is_https or is_ssh):
        raise ValueError(f"URL must be a GitHub repository URL (HTTPS or SSH): {url}")
    
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    remote_section = f"remote {remote_name}"
    if not config.has_section(remote_section):
        config.add_section(remote_section)
    
    config.set(remote_section, "url", url)
    config.set(remote_section, "auth_method", auth_method)
    
    if token and auth_method == "token":
        config.set(remote_section, "token", token)
    elif config.has_option(remote_section, "token") and auth_method == "gh_cli":
        # Remove token if switching to gh_cli
        config.remove_option(remote_section, "token")
    
    with open(get_git_config_path(), "w") as f:
        config.write(f)
    
    # Set file permissions
    os.chmod(get_git_config_path(), 0o644)


def get_remote(remote_name: str) -> Dict[str, str]:
    """
    Get remote configuration.
    
    Args:
        remote_name: Name of the remote
        
    Returns:
        Dictionary with url, auth_method, and optionally token
        
    Raises:
        ValueError: If remote doesn't exist
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    remote_section = f"remote {remote_name}"
    if not config.has_section(remote_section):
        raise ValueError(f"Remote '{remote_name}' not found.")
    
    result = {
        "url": config.get(remote_section, "url"),
        "auth_method": config.get(remote_section, "auth_method", fallback="gh_cli"),
    }
    
    if config.has_option(remote_section, "token"):
        result["token"] = config.get(remote_section, "token")
    
    return result


def list_remotes() -> Dict[str, Dict[str, str]]:
    """
    List all registered remotes.
    
    Returns:
        Dictionary mapping remote names to their configuration
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    remotes = {}
    for section in config.sections():
        if section.startswith("remote "):
            remote_name = section[7:]  # Remove "remote " prefix
            remotes[remote_name] = get_remote(remote_name)
    
    return remotes


def remove_remote(remote_name: str) -> None:
    """
    Remove a remote.
    
    Args:
        remote_name: Name of the remote to remove
        
    Raises:
        ValueError: If remote doesn't exist
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    remote_section = f"remote {remote_name}"
    if not config.has_section(remote_section):
        raise ValueError(f"Remote '{remote_name}' does not exist.")
    
    config.remove_section(remote_section)
    
    with open(get_git_config_path(), "w") as f:
        config.write(f)


def set_current_remote(profile_name: str, remote_name: str) -> None:
    """
    Set the current remote for a profile.
    
    Args:
        profile_name: Profile name
        remote_name: Name of the remote to set as current
        
    Raises:
        ValueError: If remote doesn't exist
    """
    _ensure_git_config_file()
    
    # Verify remote exists
    get_remote(remote_name)
    
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    profile_section = f"profile {profile_name}"
    if not config.has_section(profile_section):
        config.add_section(profile_section)
    
    config.set(profile_section, "remote", remote_name)
    
    with open(get_git_config_path(), "w") as f:
        config.write(f)


def set_current_branch(profile_name: str, branch_name: str) -> None:
    """
    Set the current branch for a profile.
    
    Args:
        profile_name: Profile name
        branch_name: Name of the branch to set as current
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    profile_section = f"profile {profile_name}"
    if not config.has_section(profile_section):
        config.add_section(profile_section)
    
    config.set(profile_section, "branch", branch_name)
    
    with open(get_git_config_path(), "w") as f:
        config.write(f)


def get_current_remote(profile_name: str) -> Optional[str]:
    """
    Get the current remote for a profile.
    
    Args:
        profile_name: Profile name
        
    Returns:
        Remote name or None if not set
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    profile_section = f"profile {profile_name}"
    if config.has_section(profile_section) and config.has_option(profile_section, "remote"):
        return config.get(profile_section, "remote")
    
    return None


def get_current_branch(profile_name: str) -> Optional[str]:
    """
    Get the current branch for a profile.
    
    Args:
        profile_name: Profile name
        
    Returns:
        Branch name or None if not set
    """
    _ensure_git_config_file()
    config = configparser.ConfigParser()
    config.read(get_git_config_path())
    
    profile_section = f"profile {profile_name}"
    if config.has_section(profile_section) and config.has_option(profile_section, "branch"):
        return config.get(profile_section, "branch")
    
    return None


def get_current_selection(profile_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get both current remote and branch for a profile.
    
    Args:
        profile_name: Profile name
        
    Returns:
        Tuple of (remote_name, branch_name), either may be None
    """
    return (get_current_remote(profile_name), get_current_branch(profile_name))

