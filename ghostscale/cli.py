import click
from ghostscale.config import ConfigManager
from ghostscale.tailscale import TailscaleManager
from ghostscale.wrapper import WrapperCreator

@click.group()
def cli():
    pass

@cli.command()
def status():
    "Zeigt den aktuellen Exit Node Status an."
    manager = TailscaleManager()
    node = manager.get_exit_node()
    if node:
        click.echo(f"Aktiver Exit Node: {node}")
    else:
        click.echo("Kein Exit Node aktiv.")

@cli.command()
@click.argument("prog")
def wrap(prog):
    "Erstellt einen Wrapper für das angegebene Programm."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    if prog not in config:
        click.echo(f"{prog} ist nicht in der Konfigurationsdatei definiert.")
        return
    creator = WrapperCreator()
    creator.create_wrapper(prog, config[prog])

@cli.command()
def list():
    "Listet alle Programme mit aktiven Wrapper-Regeln."
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    for prog, cfg in config.items():
        click.echo(f"{prog}: Modus={cfg.get('mode')} | Trigger={cfg.get('trigger_commands', [])}")