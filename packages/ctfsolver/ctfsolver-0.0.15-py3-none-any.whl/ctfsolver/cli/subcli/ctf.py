import typer
from pathlib import Path
from ctfsolver.managers.manager_file import ManagerFile
from ctfsolver.error.manager_error import ManagerError
from ctfsolver.config.challenge_config import ChallengeConfig


ctf_app = typer.Typer(help="CTF operations: create, delete, link, etc.")


manager_error = ManagerError()
manager_file = ManagerFile()
challenge_config = ChallengeConfig()


# ╭───────────╮
# │ CTF Stuff │
# ╰───────────╯


@ctf_app.command()
def folders():
    """Create the folder structure as specified by the global configuration."""
    manager_file.create_parent_folder()


@ctf_app.command()
def create(
    category: str = typer.Option(
        ..., "-c", "--category", help="Category for the operation"
    ),
    site: str = typer.Option(..., "-s", "--site", help="Site inside the category"),
    name: str = typer.Option(..., "-n", "--name", help="Name of the CTF challenge"),
    checker: bool = typer.Option(
        False, "-y", "--checker", help="Checker for the CTF challenge"
    ),
    download: bool = typer.Option(
        False, "-d", "--download", help="Auto move downloaded files"
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
):
    """Create a new CTF challenge structure."""
    if verbose:
        print(f"Creating new CTF: {name} in category {category} at site {site}")
    manager_file.create_ctf_structure(
        category, site, name, download=download, verbose=verbose, checker=checker
    )
    if verbose:
        print(f"Created new CTF: {name} in category {category} at site {site}")


@ctf_app.command()
def automove(
    checker: bool = typer.Option(False, "-y", "--no-check", help="No checking"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
):
    """Automatically move downloaded CTF files to their respective challenge folders."""
    # Get the folder that
    manager_file.get_current_dir()
    category = manager_file.parent.parent.parent.name
    challenge_name = manager_file.parent.name
    manager_file.download_automove(
        category=category,
        challenge_name=challenge_name,
        challenge_path=manager_file.parent,
        checker=checker,
        verbose=verbose,
    )


@ctf_app.command()
def show(
    category: str = typer.Option(
        ..., "-c", "--category", help="Category for the operation"
    ),
    site: str = typer.Option(..., "-s", "--site", help="Site inside the category"),
):
    """Navigate CTF categories/sites and list subdirectories."""
    CONFIG.get_content()
    ctf_data_dir = CONFIG.content.get("directories").get("ctf_data")
    path_building = Path(Path.home(), ctf_data_dir, category, site)
    if not path_building.exists():
        raise FileNotFoundError(f"Path does not exist: {path_building}")
    _, dirs, _ = manager_file.single_folder_search(path=path_building)
    print(dirs)


@ctf_app.command()
def link():
    """Link CTF folders (implementation TBD)."""
    pass


@ctf_app.command()
def find_usage(directory: str = typer.Option(None, help="Directory for the operation")):
    """Find usage of a specific import statement in project files."""
    search_string = "from ctfsolver import CTFSolver"
    exclude_dirs = ["app_venv", ".git"]
    current_directory = None
    if directory:
        current_directory = manager_file.check_folder_exists(directory)
    if current_directory is False:
        raise ValueError("Invalid directory specified.")
    if current_directory is None:
        current_directory = "."
    manager_error.try_function(
        function=manager_file.search_files,
        directory=current_directory,
        exclude_dirs=exclude_dirs,
        search_string=search_string,
        display=True,
    )


@ctf_app.command("init", help="Initialize challenge configuration.")
def init_challenge():
    """Initialize challenge configuration in the current directory."""
    challenge_config.initialize_challenge()
