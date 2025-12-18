"""
manager_files_re.py

This module provides the ManagerFileRegex class for extracting printable strings from files using regular expressions.

Classes:
    ManagerFileRegex:
        A manager class for file operations involving regular expressions,
        including extracting printable ASCII strings from binary files.

Usage:
    Instantiate ManagerFileRegex and use its methods to process files for printable string extraction.

Example:
    manager = ManagerFileRegex()
    strings = manager.extract_strings("/path/to/file", min_length=4)

Attributes:
    None

"""

from email import utils
import re
from rapidfuzz import fuzz


class ManagerFileRegex:
    def __init__(self, *args, **kwargs):
        # self.re = re
        pass

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class
        """
        pass

    def extract_strings(self, file_path, min_length=4):
        """
        Description:
            Extracts printable strings from a file

        Args:
            file_path (str): The path to the file
            min_length (int): The minimum length of the string to extract

        Returns:
            list: The list of strings

        """
        with open(file_path, "rb") as f:
            # Read the entire file as binary
            data = f.read()

            # Use a regular expression to find sequences of printable characters
            # The regex matches sequences of characters that are printable (ASCII 32-126)
            # and have a minimum length defined by min_length
            strings = re.findall(rb"[ -~]{%d,}" % min_length, data)

            # Decode the byte strings to regular strings
            return [s.decode("utf-8", errors="ignore") for s in strings]

    def normalize_name(self, name: str) -> str:
        """
        Normalize a file or folder name so different naming styles correlate.
        """
        name = name.lower()

        # Remove archive extensions
        name = re.sub(r"\.(zip|tar|gz|7z)$", "", name)

        # Split on common separators
        parts = re.split(r"[_\- ]+", name)

        # Join and remove non-alphanumerics
        normalized = "".join(parts)
        normalized = re.sub(r"[^a-z0-9]", "", normalized)

        return normalized

    def string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate the similarity ratio between two strings using rapidfuzz.

        Args:
            str1 (str): The first string.
            str2 (str): The second string.

        Returns:
            float: Similarity ratio between 0 and 100.
        """
        # return fuzz.ratio(str1, str2)
        return fuzz.WRatio(str1, str2)

    def check_name_similarity_in_files(
        self, files: list, information: list, threshold: float = 70.0
    ) -> list:
        """
        Check for similar names in a list of files based on provided information.

        Args:
            information (list): List of strings to compare against file names.
            files (list): List of file names to check.
            threshold (float): Similarity threshold (0-100) to consider a match.

        Returns:
            list: List of files that have similar names above the threshold.
        """
        matched_files = []

        for file in files:
            normalized_file_name = self.normalize_name(file.name)
            for info in information:
                normalized_info = self.normalize_name(info)
                similarity = self.string_similarity(
                    normalized_file_name, normalized_info
                )
                if similarity >= threshold:
                    matched_files.append(file)
                    break  # No need to check other information strings

        return matched_files
