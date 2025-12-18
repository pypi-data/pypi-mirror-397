import subprocess
import sys
from ctfsolver.managers.manager_folder import ManagerFolder


def main():
    # result = subprocess.run([sys.executable, "-m", "ctfsolver.run"], check=True)
    # sys.exit(result.returncode)

    manager = ManagerFolder()
    manager.get_current_dir()
    result = subprocess.run(
        [sys.executable, f"{manager.parent}/payloads/solution.py"], check=True
    )
    sys.exit(result.returncode)


if __name__ == "__main__":

    main()
