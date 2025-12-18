import typer

from ctfsolver.config.global_config import CONFIG
from ctfsolver.find_usage.manager_gathering import ManagerGathering

app = typer.Typer(help="CTFSolver CLI - Manage and solve CTF challenges.")
# challenge_app = typer.Typer(help="Challenge-specific operations.")

from ctfsolver.cli.subcli.venv import venv_app
from ctfsolver.cli.subcli.ctf import ctf_app


# ╭──────────╮
# │ General  │
# ╰──────────╯


@app.command()
def init():
    """Initialize global configuration and required directories/files."""
    CONFIG.initializing()


@app.command()
def gather(verbose: bool = typer.Option(False, help="Verbose output")):
    """Gather all relevant information for the current context."""
    manager = ManagerGathering()
    manager.main()


@app.command("help", help="Show help for all commands and subcommands.")
def show_full_help():
    """
    Display help for the main app and all sub-apps (ctf, venv).
    """
    contexes = {
        "main": {
            "app": app,
            "name": "ctfsolver",
            "help": "CTFSolver CLI - Manage and solve CTF challenges.",
        },
        "ctf": {
            "app": ctf_app,
            "name": "ctf",
            "help": "CTF operations: create, delete, link, etc.",
        },
        "venv": {
            "app": venv_app,
            "name": "venv",
            "help": "Virtual environment operations.",
        },
    }
    # Print main app help
    typer.echo("=" * 40)
    typer.echo("Main Help")
    typer.echo("=" * 40)
    main_cmd = typer.main.get_command(app)
    with main_cmd.make_context("ctfsolver", []) as ctx:
        typer.echo(main_cmd.get_help(ctx))

    # Print ctf sub-app help
    typer.echo("\n" + "=" * 40)
    typer.echo("ctf Commands Help")
    typer.echo("=" * 40)
    ctf_cmd = typer.main.get_command(ctf_app)
    with ctf_cmd.make_context("ctf", []) as ctx:
        typer.echo(ctf_cmd.get_help(ctx))

    # Print venv sub-app help
    typer.echo("\n" + "=" * 40)
    typer.echo("venv Commands Help")
    typer.echo("=" * 40)
    venv_cmd = typer.main.get_command(venv_app)
    with venv_cmd.make_context("venv", []) as ctx:
        typer.echo(venv_cmd.get_help(ctx))

    for context in contexes.values():
        typer.echo("\n" + "=" * 40)
        typer.echo(f"{context['name']} Commands Help")
        typer.echo("=" * 40)
        venv_cmd = typer.main.get_command(context["app"])
        with venv_cmd.make_context(context["name"], []) as ctx:
            typer.echo(venv_cmd.get_help(ctx))


def main():
    # Add sub-apps to main app
    app.add_typer(ctf_app, name="ctf")
    app.add_typer(venv_app, name="venv")
    # app.add_typer(challenge_app, name="challenge")
    app()


if __name__ == "__main__":
    main()
