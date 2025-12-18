"""
function_definition_class.py

Provides a class for traversing Python Abstract Syntax Trees (AST) to locate specific function definitions.

This module defines the FunctionDefFinder class, which extends ast.NodeVisitor to search for a function definition node by name within a Python AST. It is useful for static code analysis, refactoring tools, or any application that requires inspection of Python source code structure.

Classes:
    FunctionDefFinder: AST NodeVisitor to find a specific function definition by name.

Example:
    finder = FunctionDefFinder(function_target="my_function")
    finder.visit(ast.parse(source_code))
    found_node = finder.function_def
"""

import ast


class FunctionDefFinder(ast.NodeVisitor):
    """
    AST NodeVisitor to find a specific function definition in a Python AST.

    Attributes:
        function_def (Optional[ast.FunctionDef]): The found function definition node.
        function_target (Optional[str]): The name of the function to search for.
        visit_list (List[ast.FunctionDef]): List of visited function definition nodes.

    Functions:
        visit_FunctionDef: Visits a function definition node in the AST.

    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the FunctionDefFinder.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Can include 'function_target' (str).
        """
        self.tree = kwargs.get("tree", None)
        self.function_target: str | None = kwargs.get("function_target", None)
        self.source_file: str | None = kwargs.get("source_file", None)
        self.function_def: ast.FunctionDef | None = None
        self.visit_list: list[ast.FunctionDef] = []
        self.info = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visits a function definition node in the AST.

        Args:
            node (ast.FunctionDef): The function definition node to visit.
        """
        if node.name == self.function_target:
            self.function_def = node
        self.visit_list.append(node.name)
        # self.info[node.name] = {
        #     "node": node,
        #     "source": ast.get_source_segment(self.tree, node),
        # }
        # self.generic_visit(node)

        # Try to extract the *exact* source first (needs the original source text),
        # otherwise fall back to ast.unparse for a reconstructed version.
        src = None
        try:
            # Prefer a dedicated 'source' attribute if present
            source_text = getattr(self, "source", None)
            if isinstance(source_text, str):
                src = ast.get_source_segment(source_text, node)
            # Backward-compat: some callers may have (incorrectly) put the source in self.tree
            elif isinstance(self.tree, str):
                src = ast.get_source_segment(self.tree, node)
        except Exception:
            src = None

        if src is None:
            try:
                # Reconstruct source (not byte-for-byte identical, but valid code)
                src = ast.unparse(node)
            except Exception:
                src = None

        self.info[node.name] = {
            "node": node,
            "source": src,
        }

        self.generic_visit(node)
