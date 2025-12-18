# ctfsolver/managers/__init__.py

import importlib
import inspect
import pkgutil
from pathlib import Path


# Currently unused
def load_managers():
    """
    Dynamically import all 'Manager*' classes from the managers package.
    Returns a list of class objects.
    """
    base_path = Path(__file__).parent
    module_prefix = __name__  # 'ctfsolver.managers'
    manager_classes = []

    for _, module_name, _ in pkgutil.iter_modules([str(base_path)]):
        if not module_name.startswith("manager_"):
            continue

        full_module = f"{module_prefix}.{module_name}"
        print(full_module)
        # try:
        #     mod = importlib.import_module(full_module)
        #     for _, obj in inspect.getmembers(mod, inspect.isclass):
        #         if obj.__name__.startswith("Manager"):
        #             manager_classes.append(obj)
        # except Exception as e:
        #     print(f"[!] Failed to import {full_module}: {e}")

    return manager_classes


from .manager_file import ManagerFile
from .manager_connections import ManagerConnections
from .manager_crypto import ManagerCrypto
