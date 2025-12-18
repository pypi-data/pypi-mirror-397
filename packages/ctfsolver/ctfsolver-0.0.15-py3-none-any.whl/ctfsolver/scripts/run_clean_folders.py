"""

This way , the frame of the script can be calibrated and it will know in which folder
the bash script of the python package is called

"""

import subprocess
import sys


def main():
    result = subprocess.run(
        [sys.executable, "-m", "ctfsolver.scripts.clean_folders"], check=True
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
