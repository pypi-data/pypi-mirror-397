# This is where the challenge info will be added
import json

from pathlib import Path
from ctfsolver.managers.manager_folder import ManagerFolder


class ChallengeConfig(ManagerFolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "init_for_challenge": False})
        # So now self.parent is the directory where the command is run
        self.challenge_info_location = Path(
            Path(__file__).parent.parent, "data", "challenge_info_template.json"
        )

    def initialize_challenge(self):
        # Initializes the challenge folder with a config file
        self.get_current_dir()
        self.create_challenge_config()

    def create_challenge_config(self):
        # Creates the challenge config file from the template
        template_data = self.get_template_data()

        template_data = self.update_challenge_info(template_data)

        challenge_config_path = Path(self.parent, "challenge_config.json")
        if challenge_config_path.exists():
            raise FileExistsError("Challenge config already exists in this directory.")
        with open(challenge_config_path, "w") as f:
            json.dump(template_data, f, indent=4)
        print(f"Challenge config created at {challenge_config_path}")

    def get_template_data(self):
        if not self.challenge_info_location.exists():
            raise FileNotFoundError("Challenge info template not found.")
        with open(self.challenge_info_location, "r") as f:
            template_data = json.load(f)
        return template_data

    def update_challenge_info(self, data):
        # Update the challenge info with user input
        data["info"]["title"] = self.parent.name
        data["info"]["category"] = self.parent.parent.name
        data["info"]["site"] = self.parent.parent.parent.name
        # data["info"]["description"] = input("Description: ").strip()
        # data["info"]["author"] = input("Author: ").strip()
        return data
