import click
from ghostscale.config import ConfigManager
from ghostscale.tailscale import TailscaleManager
from ghostscale.wrapper import WrapperCreator
import yaml

@click.group()
def cli():
    pass

@cli.command()
def status():
    "Shows the current exit node status."
    manager = TailscaleManager()
    node = manager.get_exit_node()
    if node:
        click.echo(f"Active Exit Node: {node}")
    else:
        click.echo("No exit node active.")

@cli.command()
@click.argument("prog")
def wrap(prog):
    "Creates a wrapper for the specified program. The programm has to be defined in the configuration file."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} is not defined in the configuration file.")
        return
    creator = WrapperCreator()
    creator.create_wrapper(prog, config[prog])


@cli.command()
def list():
    """List all programs with active wrapper rules as YAML."""
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    result = {}
    for prog, cfg in config.items():
        result[prog] = {
            "mode": cfg.get("mode"),
            "trigger": cfg.get("trigger_commands", []),
            "status": "enabled" if cfg.get("enabled", True) else "disabled"
        }
    click.echo(yaml.dump(result, sort_keys=False))

@cli.command()
@click.argument("prog")
def enable(prog):
    "Enable a service in the configuration."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} is not in the configuration.")
        return
    config[prog]["enabled"] = True
    with open(config_mgr.config_path, "w") as f:
        yaml.dump(config, f)
    click.echo(f"{prog} has been enabled.")
    WrapperCreator().create_wrapper(prog, config[prog])

@cli.command()
@click.argument("prog")
def disable(prog):
    "Disable a service in the configuration."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} is not in the configuration.")
        return
    config[prog]["enabled"] = False
    with open(config_mgr.config_path, "w") as f:
        yaml.dump(config, f)
    click.echo(f"{prog} has been disabled.")
    WrapperCreator().create_wrapper(prog, config[prog])

@cli.command()
@click.argument("prog")
def toggle(prog):
    "Toggle the enabled status of a program."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} is not in the configuration.")
        return
    current = config[prog].get("enabled", True)
    config[prog]["enabled"] = not current
    with open(config_mgr.config_path, "w") as f:
        yaml.dump(config, f)
    state = "enabled" if not current else "disabled"
    click.echo(f"{prog} has been {state}.")
    WrapperCreator().create_wrapper(prog, config[prog])

@cli.command()
@click.argument("prog")
def program_status(prog):
    "Show configuration for a specific program."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} is not in the configuration.")
        return
    click.echo(yaml.dump({prog: config[prog]}, sort_keys=False))

@cli.command()
def exits():
    """List all available exit nodes as YAML."""
    manager = TailscaleManager()
    exit_nodes = manager.get_exit_nodes()
    if not exit_nodes:
        click.echo("No exit nodes found.")
        return
    click.echo(yaml.dump({"exit_nodes": exit_nodes}, sort_keys=False))

@cli.command()
def self():
    "Show information about the current device."
    manager = TailscaleManager()
    self_info = manager.get_self_info()
    click.echo(yaml.dump(self_info, sort_keys=False))