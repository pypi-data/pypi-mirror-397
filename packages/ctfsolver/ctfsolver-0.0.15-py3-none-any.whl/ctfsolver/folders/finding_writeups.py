from ctfsolver import CTFSolver
import string


class Folder_Structure(CTFSolver):
    """
    Handles operations related to organizing, comparing, and displaying CTF challenge folders and writeups.

    This class provides methods to:
    - Retrieve and structure challenge and writeup directories.
    - Clean up writeup data by filtering out unwanted files and folders.
    - Normalize challenge and writeup names for comparison.
    - Find differences between available challenges and writeups.
    - Print formatted tables summarizing challenges, writeups, and their differences.

    Attributes:
        Inherits from CTFSolver, which should provide methods like single_folder_search and Path.

    Methods:
        printing_table(challenges):
            Prints a formatted table of challenges grouped by category and site.

        printing_table_diff(challenges):
            Prints a formatted table showing differences between challenges and writeups, including their source.

        getting_challenges(path=None, folder=True):
            Retrieves a nested dictionary of challenges or writeups from the specified directory path.

        writeup_cleanup(writeups, exclude=None):
            Cleans up the writeups dictionary by removing excluded categories and filtering out non-writeup files.

        lowering(challenges):
            Normalizes challenge names by removing punctuation, spaces, and converting to lowercase.

        differ(challenges, writeups):
            Compares challenges and writeups, returning a dictionary of differences by category and site.

        main():
            Main workflow to retrieve challenges and writeups, clean and compare them, and print the results.

    """

    def printing_table(self, challenges):
        """
        Prints a formatted table displaying CTF challenges grouped by category and site.
        Args:
            challenges (dict): A nested dictionary where the first-level keys are category names (str),
            the second-level keys are site names (str), and the innermost values are lists of challenge names (str).
        Example:
            challenges = {
            "Crypto": {
                "CTFsite1": ["ChallengeA", "ChallengeB"],
                "CTFsite2": ["ChallengeC"]
            },
            "Web": {
                "CTFsite3": ["ChallengeD"]
            }
            }
            printing_table(challenges)
        Output:
            Prints a table to the console with columns: index, category, site, and challenge name.
        """

        print(f"| {'i':^5} | {'Categories':^20} | {'Sites':^30} | {'Challenges':^30} |")
        # 30+30+20+5+2*4
        num = 30 + 30 + 20 + 5 + 2 * 4 + 3
        print(f"|{'-'*num:^{num}}|")
        counter = 1
        for category in challenges:
            for site in challenges[category]:
                for challenge in challenges[category][site]:
                    counter += 1
                    # challenge = str(challenge)
                    print(
                        f"| {counter:^5} | {category:^20} | {site:^30} | {challenge:^30} | "
                    )

    def printing_table_diff(self, challenges):
        print(
            f"| {'i':^5} | {'Categories':^20} | {'Sites':^30} | {'Challenges':^30} | {'Source':^20} |"
        )
        # 30+30+20+5+2*4
        num = 30 + 30 + 20 + 20 + 5 + 2 * 5 + 4
        print(f"|{'-'*num:^{num}}|")
        counter = 1

        for category in sorted(challenges.keys()):
            for site in sorted(challenges[category].keys()):
                for challenge in challenges[category][site]:
                    counter += 1
                    print(
                        f"| {counter:^5} | {category:^20} | {site:^30} | {challenge['name']:^30} | {challenge['source']:^20} |"
                    )

    def getting_challenges(self, path=None, folder=True):
        # path = "/home/figaro/Programms/Github_Projects/NikolasProjects/CTFSolverScript"
        # path = "/home/figaro/CTF/Categories"
        # path = None
        exclude = [
            "__pycache__",
            ".git",
            "tools",
            ".idea",
            "venv",
            "temp",
            "temp2",
            "app_venv",
            "venv_app",
            "venv_testing",
            ".github",
            "Cloned",
            "Events",
            "youtube",
        ]

        challenges = {}

        categories_root, categories_dir, _ = self.single_folder_search(
            path=path,
            exclude=exclude,
        )

        for category in categories_dir:

            challenges[category] = {}

            site_root, site_dirs, _ = self.single_folder_search(
                path=self.Path(categories_root, category),
                exclude=exclude,
            )

            for site in site_dirs:

                challenges[category][site] = []
                challenge_root, challenge_dirs, challenge_files = (
                    self.single_folder_search(
                        path=self.Path(site_root, site),
                        exclude=exclude,
                    )
                )

                if folder:
                    for challenge in challenge_dirs:
                        challenges[category][site].append(challenge)
                else:
                    for challenge in challenge_files:
                        challenges[category][site].append(challenge)

        return challenges

    def writeup_cleanup(self, writeups, exclude=None):

        if exclude is None:
            exclude = [
                "Aa_pics",
                "Events",
                "Learning",
                "Notes",
                "Resources",
                "Uncategorized",
                "ctflearn",
                "indexes",
                "youtube",
            ]
        new_writeups = {}
        for category in writeups:
            if category in exclude:
                continue
            new_writeups[category] = {}
            for site in writeups[category]:
                new_writeups[category][site] = []

                for challenge in writeups[category][site]:
                    extension = challenge.split(".")
                    if extension[1] in ["png", "jpg", "jpeg", "gif"]:
                        continue

                    if extension[1] == "md":
                        challenge = extension[0]

                    if challenge != site:
                        new_writeups[category][site].append(challenge)

        return new_writeups

    def lowering(self, challenges):
        for category in challenges:
            for site in challenges[category]:
                challs = challenges[category][site][::]
                challenges[category][site] = []
                for chall in challs:
                    for pun in string.punctuation:
                        chall = chall.replace(pun, "")
                    chall = chall.replace(" ", "")
                    chall = chall.lower()
                    challenges[category][site].append(chall)

        return challenges

    def differ(self, challenges, writeups):
        diffs = {}
        challenges = self.lowering(challenges)
        writeups = self.lowering(writeups)

        # Combine all unique categories from both dictionaries
        categories = set(challenges.keys()).union(writeups.keys())

        for category in categories:
            diffs[category] = {}

            # Combine all unique sites for the current category
            sites = set(challenges.get(category, {}).keys()).union(
                writeups.get(category, {}).keys()
            )

            for site in sites:
                diffs[category][site] = []

                # Get the challenge lists for both challenges and writeups
                challs_iter = challenges.get(category, {}).get(site, [])
                writeups_iter = writeups.get(category, {}).get(site, [])

                # Find challenges present in `challenges` but not in `writeups`
                for challenge in challs_iter:
                    if challenge not in writeups_iter:
                        diffs[category][site].append(
                            {"name": challenge, "source": "challenge"}
                        )

                # Find writeups present in `writeups` but not in `challenges`
                for writeup in writeups_iter:
                    if writeup not in challs_iter:
                        diffs[category][site].append(
                            {"name": writeup, "source": "writeup"}
                        )

            # Remove empty sites for the current category
            diffs[category] = {
                site: diff for site, diff in diffs[category].items() if diff
            }

        # Remove empty categories
        diffs = {category: sites for category, sites in diffs.items() if sites}

        return diffs

    def main(self):
        challenges = self.getting_challenges(path="/home/figaro/CTF/Categories")

        # self.printing_table(challenges)

        print("=" * 100)

        writeups = self.getting_challenges(
            path="/home/figaro/Documents/obsidianVault/CTF", folder=False
        )

        writeups = self.writeup_cleanup(writeups)
        # self.printing_table(writeups)

        diffs = self.differ(challenges, writeups)

        self.printing_table_diff(diffs)


if __name__ == "__main__":
    Folder_Structure().main()
