from ctfsolver.config.global_config import CONFIG
from ctfsolver.managers.manager_file import ManagerFile
from pathlib import Path


class Linking(ManagerFile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = kwargs.get("categories", None)
        self.site = kwargs.get("site", None)
        self.handling_global_config()

    def handling_global_config(self):

        self.directories = CONFIG.content.get("directories", {})
        ctf_folder = self.directories.get("ctf_data", "")
        self.ctf_path = Path(Path.home(), ctf_folder)
        self.exclude_folders = self.directories.get("exclude", [])

    def get_categories(self):
        _, self.all_categories, _ = self.single_folder_search(
            path=self.ctf_path, exclude=self.exclude_folders
        )

        print(f"Found categories: {self.all_categories}")

    def get_all_sites(self):
        self.all_sites = set()

        for category in self.all_categories:
            category_path = self.ctf_path / category
            _, site_dirs, _ = self.single_folder_search(
                path=category_path, exclude=self.exclude_folders
            )
            self.all_sites.update(site_dirs)

    def get_challenges(self, category=None, site=None, folder=True):
        challenges = {}

        if category is not None:
            pass

        categories_root, categories_dir, _ = self.single_folder_search(
            path=self.ctf_path,
            exclude=self.exclude_folders,
        )

    def temp(self):
        # Get the category, and sites
        # Go to documents fetch the challenges from these sites
        # Go to ctf fetch the challenges from that as well
        # Compare
        # Optional get the current working folder and site as an input
        pass

    def main(self):
        self.get_categories()
        # pass


if __name__ == "__main__":
    linking = Linking()
    linking.main()
