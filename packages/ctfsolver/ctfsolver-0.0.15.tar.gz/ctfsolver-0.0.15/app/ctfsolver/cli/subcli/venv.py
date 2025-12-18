import typer
from pathlib import Path
from ctfsolver.venv.manager_venv import ManagerVenv

venv_app = typer.Typer(help="Virtual environment operations.")
manager = ManagerVenv()


@venv_app.command("test", help="Test virtual environment management features.")
def test_venv(
    # directory: str = typer.Option(
    #     ..., "-e", "--eir", help="Directory for the operation"
    # )
):
    """Manage virtual environments (implementation TBD)."""

    manager.testing()


@venv_app.command("look_for", help="Look for virtual environment management features.")
def look_for_venv():
    """Manage virtual environments (implementation TBD)."""

    venvs = manager.look_for_venvs()
    print(venvs)
