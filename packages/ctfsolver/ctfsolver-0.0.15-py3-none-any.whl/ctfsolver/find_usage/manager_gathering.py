from ctfsolver.managers.manager_folder import ManagerFolder
from ctfsolver.managers.manager_functions import ManagerFunction
from ctfsolver.managers.manager_class import ManagerClass
from ctfsolver.error.manager_error import ManagerError
from pathlib import Path
from ctfsolver.config import CONFIG


class ManagerGathering(ManagerFunction, ManagerFolder):
    def __init__(self, *args, **kwargs):
        self.initializing_all_ancestors(*args, **kwargs)
        self.gathering_target = Path(__file__).parent / "gathering.py"
        self.manager_error = ManagerError()
        self.manager_class = ManagerClass()

    def initializing_all_ancestors(self, *args, **kwargs):
        ManagerFunction.__init__(self, *args, **kwargs)
        k = {**kwargs, "init_for_challenge": False}
        ManagerFolder.__init__(self, *args, **k)

    def handling_global_config(self):

        self.directories = CONFIG.content.get("directories", {})
        ctf_folder = self.directories.get("ctf_data", "")
        self.ctf_path = Path(Path.home(), ctf_folder)
        self.exclude_folders = self.directories.get("exclude", [])

    def get_gathering_target(self):
        # functions = self.get_functions_from_file(self.gathering_target)
        info = self.manager_class.inspect(
            self.gathering_target, "Gathering", include_inherited=False
        )

        return info

    def get_org_information(self):
        root = Path(__file__).parent.parent
        ctfsolver_path = Path(root, "src", "ctfsolver.py")
        inspector = ManagerClass(search_paths=[root])  # look for bases in current dir

        info = inspector.inspect(ctfsolver_path, "CTFSolver", include_inherited=True)

        # print([i["name"] for i in info["methods"].keys()])
        print([i for i in info["methods"].keys()])

    def renaming_method(self):
        # Renames the method enumerating
        pass

    def adding_to_file(self, filename: str, method_source: str):
        # Adds the method , and a comment from which file it is coming from
        print(f"\t# {filename}\n{self.tabbing(method_source)}\n\n")

        # return
        with open(self.gathering_target, "a") as f:

            f.write(f"\t# {filename}\n")
            f.write(f"{self.tabbing(method_source, function=True, space=True)}\n\n")

    def tabbing(self, text: str, num: int = 1, function=False, space=True, space_num=4):
        lines = text.split("\n")
        tab_like = "\t" if not space else " " * space_num
        for i in range(len(lines)):
            lines[i] = tab_like * num + lines[i]
            if function and i == 0:
                break
        return "\n".join(lines)

    def gathering_all_solution_files(self):

        gathering_info = self.get_gathering_target()

        # files = self.manager_error.try_function(
        #     function=self.search_files,
        #     directory=self.ctf_path,
        #     exclude_dirs=self.exclude_folders,
        #     search_string="from ctfsolver import CTFSolver",
        #     save=True,
        # )

        # for speeding up the development process
        from ctfsolver.feature_test.testing_files import files

        # return

        for file_name in files:
            file_path = Path(file_name)
            if file_path.is_file():
                classes = self.manager_class.get_classes_in_file(file_path)

                if "Solution" not in classes:
                    print(
                        f"File {file_path} does not contain Solution class\n{''.join(classes)}"
                    )
                    continue

                info_sol_iter = self.manager_class.inspect(
                    file_path, "Solution", include_inherited=False
                )
                print(
                    f"Challenge: {file_path.as_posix().split("/")[-3]}, Methods: {list(info_sol_iter['methods'].keys())}\n\n"
                )
                # self.exec_on_files(folder = self.ctf_path, function=self.search_files,  )

                self.check_functions(gathering_info, info_sol_iter, file_path)

    def check_functions(self, target_info, solution_info, solution_name):
        # Compare the functions in the target_info with those in the solution_info
        target_methods = target_info.get("methods", {})
        solution_methods = solution_info.get("methods", {})

        # Get the methods that already exist in the target_methods
        existin_methods = []
        for method in solution_methods.keys():
            if method in target_methods:
                existin_methods.append(method)

        # Enumerate the existing methods
        # enumerating = self.method_enumeration()

        for method in solution_methods:
            # if method not in target_methods:
            # self.adding_to_file(
            #     filename=solution_name,
            #     method_source=solution_methods[method]["source"],
            # )
            # else:
            #     print(f"Method {method} found in target info.")
            self.adding_to_file(
                filename=solution_name,
                method_source=solution_methods[method]["source"],
            )

    def method_enumeration(self, target_methods, method_name):
        """
        Enumerates methods in target_methods that match method_name
        with optional numbering (e.g., foo, foo_1, foo_2).
        """
        import re

        pattern = re.compile(rf"\b{re.escape(method_name)}(?:_\d+)?\b")

        return [method for method in target_methods.keys() if pattern.search(method)]

    def main(self):
        # self.get_org_information()
        # self.gather_functions = self.get_gathering_target()
        self.gathering_all_solution_files()


if __name__ == "__main__":
    manager = ManagerGathering()
    manager.main()
