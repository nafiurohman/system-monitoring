#!/usr/bin/env python3
"""
BMonitor CLI Tool

Manage the bmonitor system monitoring service.
"""

import click
import subprocess
import sys
import os
import json
import configparser
import getpass

CONFIG_DIR = "/opt/bmonitor/config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "app.ini")
USERS_FILE = os.path.join(CONFIG_DIR, "users.json")
SERVICE_NAME = "bmonitor"


def run(cmd, capture=True):
    """Run a shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result


def load_config():
    """Load app.ini config."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    return config


def save_config(config):
    """Save app.ini config."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def load_users():
    """Load users.json."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


@click.group()
def cli():
    """BMonitor — System Monitoring Service Manager"""
    pass


@cli.command()
def status():
    """Check the status of the bmonitor service."""
    r = run(f"systemctl is-active {SERVICE_NAME}")
    state = r.stdout.strip()
    if state == "active":
        click.secho(f"● bmonitor is running", fg="green")
    else:
        click.secho(f"● bmonitor is {state}", fg="red")
    run(f"systemctl status {SERVICE_NAME} --no-pager -l", capture=False)


@cli.command()
def start():
    """Start the bmonitor service."""
    r = run(f"sudo systemctl start {SERVICE_NAME}")
    if r.returncode == 0:
        click.secho("bmonitor started.", fg="green")
    else:
        click.secho("Failed to start bmonitor.", fg="red")
        click.echo(r.stderr)


@cli.command()
def stop():
    """Stop the bmonitor service."""
    r = run(f"sudo systemctl stop {SERVICE_NAME}")
    if r.returncode == 0:
        click.secho("bmonitor stopped.", fg="yellow")
    else:
        click.secho("Failed to stop bmonitor.", fg="red")
        click.echo(r.stderr)


@cli.command()
def restart():
    """Restart the bmonitor service."""
    r = run(f"sudo systemctl restart {SERVICE_NAME}")
    if r.returncode == 0:
        click.secho("bmonitor restarted.", fg="green")
    else:
        click.secho("Failed to restart bmonitor.", fg="red")
        click.echo(r.stderr)


@cli.command()
@click.option("-n", "--lines", default=50, help="Number of log lines to show.")
@click.option("-f", "--follow", is_flag=True, help="Follow log output.")
def logs(lines, follow):
    """Show bmonitor service logs."""
    cmd = f"journalctl -u {SERVICE_NAME} --no-pager -n {lines}"
    if follow:
        cmd = f"journalctl -u {SERVICE_NAME} -f"
    run(cmd, capture=False)


@cli.command()
@click.argument("number", type=int)
def port(number):
    """Change the bmonitor listening port."""
    if number < 1 or number > 65535:
        click.secho("Port must be between 1 and 65535.", fg="red")
        return
    config = load_config()
    if not config.has_section("server"):
        config.add_section("server")
    config.set("server", "port", str(number))
    save_config(config)
    click.secho(f"Port set to {number}. Restart bmonitor to apply.", fg="green")


@cli.command("add-user")
def add_user():
    """Add a web UI user."""
    import bcrypt

    username = click.prompt("Username")
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        click.secho("Passwords do not match.", fg="red")
        return

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users = load_users()
    users[username] = {"password": hashed}
    save_users(users)
    click.secho(f"User '{username}' added.", fg="green")


@cli.command("change-password")
@click.argument("username")
def change_password(username):
    """Change password for an existing user."""
    import bcrypt

    users = load_users()
    if username not in users:
        click.secho(f"User '{username}' not found.", fg="red")
        return

    password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        click.secho("Passwords do not match.", fg="red")
        return

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username]["password"] = hashed
    save_users(users)
    click.secho(f"Password updated for '{username}'.", fg="green")


@cli.command("list-users")
def list_users():
    """List all web UI users."""
    users = load_users()
    if not users:
        click.echo("No users found.")
        return
    click.echo("Users:")
    for name in users:
        click.echo(f"  - {name}")


@cli.command()
def update():
    """Update bmonitor to the latest version."""
    script = "/opt/bmonitor/src/scripts/update.sh"
    if os.path.exists(script):
        os.execvp("sudo", ["sudo", "bash", script])
    else:
        click.secho("Update script not found.", fg="red")


@cli.command()
def uninstall():
    """Uninstall bmonitor from this system."""
    if not click.confirm("Are you sure you want to uninstall bmonitor?"):
        return
    script = "/opt/bmonitor/src/scripts/uninstall.sh"
    if os.path.exists(script):
        os.execvp("sudo", ["sudo", "bash", script])
    else:
        click.secho("Uninstall script not found.", fg="red")


if __name__ == "__main__":
    cli()
