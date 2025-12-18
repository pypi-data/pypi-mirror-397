"""
manager_class.py

Provides the ManagerClass for inspecting Python classes in source files, including their methods,
class attributes, and instance attributes, with optional support for inherited members from base classes
located in nearby files or directories.

This module is useful for static analysis, code introspection, and documentation generation tasks
where understanding the structure and inheritance of Python classes is required.

Classes:
    ManagerClass: Inspects Python class definitions and their members, supporting inheritance resolution
                  across multiple files and directories.

Example:
    inspector = ManagerClass(search_paths=["src", "package"])

Attributes:
    None



About self.inspect return :


from typing import TypedDict, Dict, List, Optional
from typing import Literal  # if on 3.8, use: from typing_extensions import Literal


class MethodInfo(TypedDict):
    kind: Literal["instance", "class", "static", "property", "property-setter", "property-deleter"]
    async: bool
    decorators: List[Optional[str]]   # result of unparse; may be None
    args: List[str]                   # parameter names as written
    returns: Optional[str]            # return annotation (unparsed) or None
    source: Optional[str]             # exact segment if available, else unparsed; may be None
    defined_in: str                   # class name where defined
    file: str                         # file path where defined (string path)
    inherited: bool                   # True if came from a base class


class ClassAttrInfo(TypedDict):
    source: Optional[str]             # assignment statement source
    value_source: Optional[str]       # RHS expression source (if present)
    defined_in: str
    file: str
    inherited: bool


class InstanceAttrOccurrence(TypedDict):
    method: str                       # method where self.<attr> was assigned
    lineno: Optional[int]             # line number (if available)
    source: Optional[str]             # assignment statement source
    defined_in: str
    file: str
    inherited: bool


class OriginInfo(TypedDict):
    class_: str                       # class name of origin (key name 'class' in dict; see below)
    file: str
    inherited: bool


# Because 'class' is a reserved word in Python, we store it in the dict as 'class'
# but expose a typing alias that maps to 'class' at runtime. Type checkers accept this pattern:
OriginMap = Dict[str, OriginInfo]     # maps symbol name -> origin info


class Origins(TypedDict):
    methods: OriginMap
    class_attributes: OriginMap
    instance_attributes: OriginMap


class ClassRefInfo(TypedDict):
    file: str
    source: Optional[str]             # class block source
    bases: List[Optional[str]]        # base expressions (unparsed); may be None
    decorators: List[Optional[str]]   # class decorators (unparsed); may be None


class ClassInspectionResult(TypedDict):
    name: str
    mro: List[str]                                      # best-effort: derived first, then bases
    methods: Dict[str, MethodInfo]                      # method name -> details
    class_attributes: Dict[str, ClassAttrInfo]          # class attr name -> details
    instance_attributes: Dict[str, List[InstanceAttrOccurrence]]  # self.<attr> -> occurrences
    origins: Origins
    classes: Dict[str, ClassRefInfo]                    # per-class summary (derived and bases)





"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


class ManagerClass:
    """
    Inspect Python classes in source files, including inherited members found in nearby files.

    Usage:
        inspector = ClassInspector(search_paths=["src", "package"])
        details = inspector.inspect("path/to/file.py", "MyClass", include_inherited=True)
    """

    # ---------- public API ----------

    def __init__(self, search_paths: Optional[List[str | Path]] = None):
        self.default_search_paths: List[Path] = []
        if search_paths:
            self.default_search_paths = [Path(p).resolve() for p in search_paths]

    def inspect(
        self,
        file_path: str | Path,
        class_name: str,
        include_inherited: bool = True,
        extra_search_paths: Optional[List[str | Path]] = None,
    ) -> Dict[str, Any]:
        """
        Parse a Python file, locate `class_name`, and return its functions/attributes.
        If `include_inherited` is True, also pulls in members from base classes found
        within search paths (default: the file's directory + self.default_search_paths + extra_search_paths).

        Returns:
          {
            "name": str,
            "mro": [derived, base1, base2, ...],      # best-effort order
            "methods": { name: {..., defined_in, file, inherited } },
            "class_attributes": { name: {..., defined_in, file, inherited } },
            "instance_attributes": { name: [ {..., defined_in, file, inherited }, ...] },
            "origins": {...},                          # where each symbol came from
            "classes": { class_name: {"file": str, "source": str, "bases": [...], "decorators":[...]} }
          }
        """
        base_path = Path(file_path).resolve()
        src, tree = self._read_parse(base_path)

        # Find target class in this file
        target_node: Optional[ast.ClassDef] = None
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef) and n.name == class_name:
                target_node = n
                break
        if target_node is None:
            raise ValueError(f"Class {class_name!r} not found in {file_path}")

        # Collect info for the target
        target_info = self._collect_class_info_from_ast(src, target_node)

        if not include_inherited:
            return self._merge_class_infos([(target_info, base_path, class_name)])

        # Build search path list
        paths: List[Path] = [base_path.parent]
        paths.extend(self.default_search_paths)
        if extra_search_paths:
            paths.extend([Path(p) for p in extra_search_paths])

        py_files = self._iter_python_files(paths)

        # Index classes across the project area (plus current file)
        if base_path not in py_files:
            py_files.append(base_path)
        idx = self._index_classes(py_files)

        # Build a best-effort MRO list: [derived, base1, base1_base, base2, ...]
        mro_infos: List[Tuple[Dict[str, Any], Path, str]] = [
            (target_info, base_path, class_name)
        ]

        # BFS over bases, skip builtins
        queue: List[Tuple[str, Optional[Path]]] = []
        seen_class_names = {class_name, "object"}

        for b in target_node.bases:
            bn = self._base_name(b)
            if bn and bn not in seen_class_names:
                queue.append((bn, base_path))
                seen_class_names.add(bn)

        while queue:
            bn, preferred = queue.pop(0)
            rec = self._choose_class_record(idx, bn, preferred)
            if rec is None:
                continue  # unknown / external base
            b_info = self._collect_class_info_from_ast(rec["src"], rec["node"])
            mro_infos.append((b_info, rec["file"], rec["node"].name))
            # enqueue that base's bases
            for bb in rec["node"].bases:
                name2 = self._base_name(bb)
                if name2 and name2 not in seen_class_names:
                    queue.append((name2, rec["file"]))
                    seen_class_names.add(name2)

        # Merge child over bases
        return self._merge_class_infos(mro_infos)

    # ---------- helpers ----------

    def _read_parse(self, path: Path) -> Tuple[str, ast.AST]:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        return src, tree

    def _safe_unparse(self, node: Optional[ast.AST]) -> Optional[str]:
        if node is None:
            return None
        try:
            return ast.unparse(node)
        except Exception:
            return None

    def _segment(self, src: str, node: ast.AST) -> Optional[str]:
        try:
            s = ast.get_source_segment(src, node)
            if s is not None:
                return s
        except Exception:
            pass
        return self._safe_unparse(node)

    def _iter_python_files(self, paths: List[Path]) -> List[Path]:
        files: List[Path] = []
        seen: set[Path] = set()
        for p in paths:
            p = p.resolve()
            if p in seen:
                continue
            seen.add(p)
            if p.is_file() and p.suffix == ".py":
                files.append(p)
            elif p.is_dir():
                for q in p.rglob("*.py"):
                    qp = q.resolve()
                    if qp not in seen:
                        files.append(qp)
                        seen.add(qp)
        return files

    def _index_classes(self, py_files: List[Path]) -> Dict[str, List[Dict[str, Any]]]:
        """
        class_name -> [ {file, src, tree, node}, ... ]
        Names are unqualified. If duplicates exist, we keep all and prefer same-file matches later.
        """
        idx: Dict[str, List[Dict[str, Any]]] = {}
        for f in py_files:
            try:
                src = f.read_text(encoding="utf-8")
                tree = ast.parse(src, filename=str(f))
            except Exception:
                continue
            for n in ast.walk(tree):
                if isinstance(n, ast.ClassDef):
                    idx.setdefault(n.name, []).append(
                        {"file": f, "src": src, "tree": tree, "node": n}
                    )
        return idx

    def _base_name(self, b: ast.expr) -> Optional[str]:
        """
        Extract a best-effort class name from a base expression.
        - Name: Foo -> "Foo"
        - Attribute: pkg.Foo -> "Foo"
        - Subscript: Generic[Foo] -> "Generic"
        Fallback: last token after dot in unparse.
        """
        if isinstance(b, ast.Name):
            return b.id
        if isinstance(b, ast.Attribute):
            return b.attr
        if isinstance(b, ast.Subscript):
            return self._base_name(b.value)
        s = self._safe_unparse(b) or ""
        if "." in s:
            return s.split(".")[-1]
        return s or None

    def _choose_class_record(
        self,
        idx: Dict[str, List[Dict[str, Any]]],
        name: str,
        preferred_file: Optional[Path],
    ) -> Optional[Dict[str, Any]]:
        """
        Choose a class record by name. Prefer one defined in preferred_file, else the first.
        """
        items = idx.get(name) or []
        if not items:
            return None
        if preferred_file is not None:
            for rec in items:
                if rec["file"].resolve() == preferred_file.resolve():
                    return rec
        return items[0]

    def _collect_class_info_from_ast(
        self, src: str, cls_node: ast.ClassDef
    ) -> Dict[str, Any]:
        """
        Collect methods, class attrs, and instance attrs for a single ClassDef node.
        """
        info: Dict[str, Any] = {
            "name": cls_node.name,
            "bases": [self._safe_unparse(b) for b in cls_node.bases],
            "decorators": [
                self._safe_unparse(d) for d in getattr(cls_node, "decorator_list", [])
            ],
            "source": self._segment(src, cls_node),
            "methods": {},
            "class_attributes": {},
            "instance_attributes": {},
        }

        for n in cls_node.body:
            # ----- class attributes -----
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                names = []
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            names.append(t.id)
                else:  # AnnAssign
                    if isinstance(n.target, ast.Name):
                        names.append(n.target.id)
                for nm in names:
                    info["class_attributes"][nm] = {
                        "source": self._segment(src, n),
                        "value_source": (
                            self._segment(src, n.value)
                            if getattr(n, "value", None) is not None
                            else None
                        ),
                    }

            # ----- methods -----
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_name = n.name

                # Determine kind
                kind = "instance"
                decorators_src = [self._safe_unparse(d) for d in n.decorator_list]
                for d in n.decorator_list:
                    if isinstance(d, ast.Name):
                        if d.id == "staticmethod":
                            kind = "static"
                            break
                        if d.id == "classmethod":
                            kind = "class"
                            break
                        if d.id == "property":
                            kind = "property"
                            break
                    elif isinstance(d, ast.Attribute):
                        # e.g. @prop.setter / @prop.deleter
                        if d.attr in {"setter", "deleter"}:
                            kind = f"property-{d.attr}"
                            break

                info["methods"][method_name] = {
                    "kind": kind,
                    "async": isinstance(n, ast.AsyncFunctionDef),
                    "decorators": decorators_src,
                    "args": [a.arg for a in n.args.args],
                    "returns": (
                        self._safe_unparse(n.returns)
                        if getattr(n, "returns", None)
                        else None
                    ),
                    "source": self._segment(src, n),
                }

                # instance attributes in this method
                for sub in ast.walk(n):
                    if isinstance(sub, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                        targets = []
                        if isinstance(sub, ast.Assign):
                            targets = sub.targets
                        else:
                            targets = [sub.target]
                        for t in targets:
                            if (
                                isinstance(t, ast.Attribute)
                                and isinstance(t.value, ast.Name)
                                and t.value.id == "self"
                            ):
                                entry = {
                                    "method": method_name,
                                    "lineno": getattr(t, "lineno", None),
                                    "source": self._segment(src, sub),
                                }
                                info["instance_attributes"].setdefault(
                                    t.attr, []
                                ).append(entry)

        return info

    def _merge_class_infos(
        self,
        infos_in_mro_order: List[Tuple[Dict[str, Any], Path, str]],
    ) -> Dict[str, Any]:
        """
        Merge child-first over bases. Each element is (info, file, class_name).
        Child definitions win; inherited ones are added if missing.
        Annotate each method/attr with origin.
        """
        if not infos_in_mro_order:
            return {}

        # start with the most-derived
        merged = {
            "name": infos_in_mro_order[0][0]["name"],
            "mro": [clsname for (_info, _file, clsname) in infos_in_mro_order],
            "methods": {},
            "class_attributes": {},
            "instance_attributes": {},
            "origins": {
                "methods": {},  # name -> {"class": str, "file": str, "inherited": bool}
                "class_attributes": {},  # name -> {...}
                "instance_attributes": {},  # name -> {...}
            },
            "classes": {},  # per-class raw info (file, source, bases, decorators)
        }

        # Keep a copy of each class's info for reference
        for info, file_path, clsname in infos_in_mro_order:
            merged["classes"][clsname] = {
                "file": str(file_path),
                "source": info.get("source"),
                "bases": info.get("bases", []),
                "decorators": info.get("decorators", []),
            }

        for idx, (info, file_path, clsname) in enumerate(infos_in_mro_order):
            inherited = idx != 0

            # methods
            for k, v in info["methods"].items():
                if k not in merged["methods"]:
                    merged["methods"][k] = v | {
                        "defined_in": clsname,
                        "file": str(file_path),
                        "inherited": inherited,
                    }
                    merged["origins"]["methods"][k] = {
                        "class": clsname,
                        "file": str(file_path),
                        "inherited": inherited,
                    }

            # class attrs
            for k, v in info["class_attributes"].items():
                if k not in merged["class_attributes"]:
                    entry = v | {
                        "defined_in": clsname,
                        "file": str(file_path),
                        "inherited": inherited,
                    }
                    merged["class_attributes"][k] = entry
                    merged["origins"]["class_attributes"][k] = {
                        "class": clsname,
                        "file": str(file_path),
                        "inherited": inherited,
                    }

            # instance attrs (union; keep per-attr list with entries annotated)
            for k, lst in info["instance_attributes"].items():
                for item in lst:
                    annotated = item | {
                        "defined_in": clsname,
                        "file": str(file_path),
                        "inherited": inherited,
                    }
                    merged["instance_attributes"].setdefault(k, []).append(annotated)
                    merged["origins"]["instance_attributes"].setdefault(
                        k,
                        {
                            "class": clsname,
                            "file": str(file_path),
                            "inherited": inherited,
                        },
                    )

        return merged

    def example_printing(
        self,
        file_path: str,
        classname: str,
    ):
        info = self.inspect(file_path, classname, include_inherited=True)

        print("MRO (best-effort):", info["mro"])
        print("\n=== Methods (incl. inherited) ===")
        for name, m in info["methods"].items():
            print(
                f"- {name:12s} kind={m['kind']:9s} inherited={m['inherited']} defined_in={m['defined_in']}"
            )

        print("\n=== Class attributes (incl. inherited) ===")
        for name, a in info["class_attributes"].items():
            print(
                f"- {name:12s} inherited={a['inherited']} defined_in={a['defined_in']}"
            )

        print("\n=== Instance attributes (assignments to self.<attr>) ===")
        for attr, occurrences in info["instance_attributes"].items():
            origins = {f"{o['defined_in']}:{o['method']}" for o in occurrences}
            print(f"- {attr:12s} set in -> {sorted(origins)}")

    def get_classes_in_file(self, file_path: str | Path) -> list[str]:
        """
        Opens a Python file and returns a list of class names defined in that file.

        Args:
            file_path (str | Path): Path to the Python source file.

        Returns:
            list[str]: List of class names found in the file.
        """
        path = Path(file_path)
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    inspector = ManagerClass(search_paths=[root])  # look for bases in current dir

    inspector.example_printing("app/ctfsolver/src/ctfsolver.py", "CTFSolver")

    # # 1) Include inherited members (default: True)
    # info = inspector.inspect(
    #     "app/ctfsolver/src/ctfsolver.py", "CTFSolver", include_inherited=True
    # )

    # print("MRO (best-effort):", info["mro"])
    # print("\n=== Methods (incl. inherited) ===")
    # for name, m in info["methods"].items():
    #     print(
    #         f"- {name:12s} kind={m['kind']:9s} inherited={m['inherited']} defined_in={m['defined_in']}"
    #     )

    # print("\n=== Class attributes (incl. inherited) ===")
    # for name, a in info["class_attributes"].items():
    #     print(f"- {name:12s} inherited={a['inherited']} defined_in={a['defined_in']}")

    # print("\n=== Instance attributes (assignments to self.<attr>) ===")
    # for attr, occurrences in info["instance_attributes"].items():
    #     origins = {f"{o['defined_in']}:{o['method']}" for o in occurrences}
    #     print(f"- {attr:12s} set in -> {sorted(origins)}")

    # Show full source of a method (child or inherited)
    # print("\n--- Source of Dog.speak ---")
    # print(info["methods"]["folfil"]["source"])

    # # 2) Only the class itself (no inheritance)
    # info_own = inspector.inspect("child_mod.py", "Dog", include_inherited=False)
    # print("\nOwn methods only:", sorted(info_own["methods"].keys()))
