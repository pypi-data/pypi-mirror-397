"""
Global configuration management for the CTFSolverScript package.

This module provides the `GlobalConfig` class, which handles the creation, initialization,
and access of a global configuration file stored in the user's home directory. The configuration
file is used to store persistent settings required by the CTFSolverScript inline tool.

Classes:
    GlobalConfig: Manages the global configuration file, including creation, initialization,
                  reading, and attribute/dictionary-style access to configuration values.

Attributes:
    CONFIG (GlobalConfig): Singleton instance of the GlobalConfig class for global access.

Example:
    >>> from ctfsolver.config.global_config import CONFIG
    >>> from ctfsolver.config import CONFIG
    >>> CONFIG.initializing()  # Initializes the global configuration

Typical usage involves initializing the configuration (creating the file and writing initial
content if necessary) and accessing configuration values via attribute or dictionary-style access.

Raises:
    AttributeError: If an attribute is accessed that does not exist in the configuration.
    KeyError: If a key is accessed that does not exist in the configuration.
"""

import json
from pathlib import Path


class GlobalConfig:
    def __init__(self, *args, **kwargs):
        """
        Initializes the global configuration for the CTF solver application.
        This constructor sets the path to the global configuration file and loads its content.

        Attributes:
            global_config_file_path (Path): Path to the global configuration JSON file.

        Raises:
            Any exceptions raised by `get_content()` will propagate.
        """

        # Path to the global configuration file in the user's home directory

        self.verbose = kwargs.get("verbose", False)
        self.global_config_file_path = Path(
            Path.home(), ".config", "ctfsolver", "global_config.json"
        )
        self.get_content()

    def initializing(self):
        """
        Initialize global configuration settings.
        This method can be used to set up any necessary global configurations
        required by the inline tool.
        """
        self.creating()
        self.initial_content()
        print(f"Global configuration initialized in {self.global_config_file_path}")

    def creating(self):
        """
        Creates a global configuration file in the user's home directory.

        This method ensures that the required directories and configuration file exist,
        creating them if necessary. It is typically called during the initial run of the
        inline tool or when global configuration setup is required.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: If the directory or file cannot be created due to permission issues.
        """

        home_path = Path.home()
        if self.verbose:
            print(f"Setting up global configuration in {home_path}")

        # TODO: This should later be initialized in the ctfsolver to be a global attribute

        # Path  of the config file, creates the folders and the file if they don't exist

        self.global_config_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.global_config_file_path.touch(exist_ok=True)

    def initial_content(self):
        """
        Sets the initial content of the global configuration file.

        This method loads a configuration template from 'config_template.json' and writes it to the global
        configuration file if the file is empty or does not exist. If the template file is missing, a default
        initial content is used instead.

        Args:
            None

        Returns:
            None

        Raises:
            FileNotFoundError: If the template file or global configuration file path does not exist.
            json.JSONDecodeError: If the template file contains invalid JSON.

        Side Effects:
            Writes initial configuration content to the global configuration file if it is empty.
            Prints status messages to the console.
        """

        # Load the template content from config_template.json
        # Changed the location of the config_template, to keep all the data files together.
        # template_path = Path(Path(__file__).parent, "config_template.json")
        template_path = Path(
            Path(__file__).parent.parent, "data", "config_template.json"
        )
        if template_path.exists():
            with open(template_path, "r") as template_file:
                initial_content = json.load(template_file)
        else:
            print(
                f"Template file {template_path} not found. Using default initial content."
            )

        # Check if the file is empty or does not exist
        if self.global_config_file_path.stat().st_size == 0:
            with open(self.global_config_file_path, "w") as f:
                json.dump(initial_content, f, indent=4)
            print(f"Initial content written to {self.global_config_file_path}")
        else:
            print(f"{self.global_config_file_path} already contains initial content.")

    def get_content(self):
        """
        Get the content of the global configuration file.
        This method reads the global configuration file and returns its content
        as a dictionary.
        If the file does not exist or is empty, it returns an empty dictionary.
        It is intended to be used to retrieve the current global configuration
        settings for use in the inline tool or other parts of the application.


        Returns:
            dict: The content of the global configuration file as a dictionary.
        """
        self.content = {}
        with open(self.global_config_file_path, "r") as config_file:
            self.content = json.load(config_file)
        return self.content

    def __getattr__(self, name):
        """
        Retrieves the value associated with the given attribute name from the internal content dictionary.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            Any: The value associated with the attribute name in the content dictionary.

        Raises:
            AttributeError: If the attribute name does not exist in the content dictionary.
        """
        if name in self.content:
            return self.content[name]
        raise AttributeError(f"'GlobalConfig' object has no attribute '{name}'")

    def __getitem__(self, key):
        """
        Retrieves the value associated with the given key from the content dictionary.

        Args:
            key (str): The key to look up in the content dictionary.

        Returns:
            Any: The value associated with the specified key.

        Raises:
            KeyError: If the key does not exist in the content dictionary.
        """
        if key in self.content:
            return self.content[key]
        raise KeyError(f"'GlobalConfig' object has no key '{key}'")

    def check_config_content(self):
        # !TODO Checks the current config if it exists,
        # and the keys of the template config
        pass


# Creates an instance of GlobalConfig to be accessed by all the other files
CONFIG = GlobalConfig()

# Example usage:
if __name__ == "__main__":
    global_config = GlobalConfig()
    global_config.initializing()
