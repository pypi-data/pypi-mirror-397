"""
manager_functions.py

This module provides the ManagerFunction class, which offers utility methods for
introspecting and managing functions within a class and Python source files. It includes
methods to list class functions, retrieve references to function usages in files, and
extract function definitions from Python files using the AST module.

Classes:
    ManagerFunction: Provides methods for function introspection and management.

Example:
    manager = ManagerFunction()
    functions = manager.get_self_functions()
    references = manager.get_function_reference('my_func', 'my_file.py')
    ast_functions = manager.get_functions_from_file(Path('my_file.py'))

"""

import ast
from ctfsolver.find_usage.function_definition_class import FunctionDefFinder
from pathlib import Path


class ManagerFunction:
    """
    ManagerFunction provides utility methods for introspecting and managing functions within a class and Python source files.

    This class includes methods to:
        - List all callable functions defined in the class.
        - Retrieve references to function usages in a given file.
        - Extract function definitions from Python files using the AST module.

    Methods:
        get_self_functions():
            Lists all callable functions of the class instance, excluding special methods.

        get_function_reference(function, file):
            Finds and returns all lines in the specified file where the given function name appears.

            Args:
                function (str): The name of the function to search for.
                file (str): The path to the file to search in.

            Returns:
                list[str]: Lines from the file containing the function name.

            Raises:
                ValueError: If the function is not found in the class.

        get_functions_from_file(file_path, function_name=None):
            Parses the given Python file and returns function definitions using AST.

            Args:
                file_path (Path): Path to the Python file.
                function_name (str, optional): Specific function name to search for.

            Returns:
                list[ast.FunctionDef] | ast.FunctionDef | None: List of function definitions, a single function definition, or None.

        find_function_from_file(file_path, function_name):
            Deprecated. Use get_functions_from_file instead.
    """

    def __init__(self, *args, **kwargs):
        self.funcCrawler = FunctionDefFinder()
        self.ignored_functions: set[str] = ["__init__"]

    def get_self_functions(self):
        """
        Retrieves a list of all callable methods of the current instance, excluding special methods.
        Returns:
            list: A list of method names (str) that are callable and do not start with double underscores.
        """

        return [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("__")
        ]

    def get_function_reference(self, function, file):
        """
        Retrieves all lines from a file that reference a specified function.
        Args:
            function (str): The name of the function to search for.
            file (str): The path to the file in which to search for the function reference.
        Returns:
            list: A list of strings, each representing a line from the file where the function is referenced.
        Raises:
            ValueError: If the specified function is not found in the class.
        """

        if function not in self.get_self_functions():
            raise ValueError(f"Function {function} not found in the class")

        output = []

        with open(file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if function in line:
                    output.append(line)
        return output

    def function_object(self, file_path: Path, function_name: str) -> FunctionDefFinder:
        with open(file_path, "r") as file_path:
            file_content = file_path.read()

        # Parse the file content into an AST
        tree = ast.parse(file_content)

        # Create an instance of the visitor and visit the AST
        finder = FunctionDefFinder(
            function_target=function_name, tree=tree, source_file=file_content
        )
        finder.visit(tree)

        return finder

    def get_functions_from_file(
        self, file_path: Path, function_name: str = None
    ) -> list[ast.FunctionDef] | None | ast.FunctionDef:
        """
        Extracts function definitions from a Python file using AST parsing.
        Args:
            file_path (Path): The path to the Python file to analyze.
            function_name (str, optional): The name of a specific function to find. If None, all function definitions are returned.
        Returns:
            list[ast.FunctionDef] | None | ast.FunctionDef:
                - If function_name is provided and found, returns the corresponding ast.FunctionDef object.
                - If function_name is not provided, returns a list of all ast.FunctionDef objects found in the file.
                - Returns None if the specified function_name is not found.
        Raises:
            FileNotFoundError: If the specified file_path does not exist.
            SyntaxError: If the file contains invalid Python syntax.
        """

        finder = self.function_object(file_path, function_name)

        if function_name is not None:
            return finder.info.get(function_name, None)
        return finder.info

    def find_function_from_file(self, file_path, function_name):
        """
        Depracated
        """
        raise DeprecationWarning(
            "This method is deprecated and will be removed in future versions."
        )
