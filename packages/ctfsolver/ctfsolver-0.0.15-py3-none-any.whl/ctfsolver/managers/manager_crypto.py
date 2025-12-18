"""
manager_crypto.py

This module provides cryptographic utility functions for CTF (Capture The Flag) challenges,
including XOR encryption, Base64 decoding, and regular expression-based extraction of flags
and encoded strings from text.

Classes:
    ManagerCrypto: A class containing methods for cryptographic operations and pattern matching.

Typical usage example:
    crypto = ManagerCrypto()
    decoded = crypto.decode_base64(encoded_text)
    flags = crypto.re_match_flag(text, "FLAG")

Methods:
    initializing_all_ancestors(*args, **kwargs):
        Initializes all ancestors of the class (placeholder).

    xor(text: str, key: str) -> str:
        XORs the input text with the provided key.

    decode_base64(text: str) -> str:
        Decodes a Base64-encoded string.

    re_match_base64_string(text: str, strict=False) -> list[str]:
        Finds Base64 strings in the input text using regular expressions.

    re_match_flag(text: str, origin: str) -> list[str]:
        Extracts flags matching the given origin from the text.

    re_match_partial_flag(text: str, origin: str) -> list[str]:
        Extracts partial or complete flags matching the given origin from the text.

"""

import base64
import re


class ManagerCrypto:
    """
    ManagerCrypto provides utility methods for common cryptographic operations and flag extraction used in CTF challenges.
    Methods:
        initializing_all_ancestors(*args, **kwargs):
            Initializes all ancestors of the class. (Currently a placeholder.)
        xor(text: str, key: str) -> str:
            XORs the input text with the provided key and returns the result as a string.
        decode_base64(text: str) -> str:
            Decodes a base64-encoded string and returns the decoded text.
        re_match_base64_string(text: str, strict: bool = False) -> list[str]:
            Finds and returns all base64 strings in the input text. If strict is True, matches only strings with padding.
        re_match_flag(text: str, origin: str) -> list[str]:
            Searches for flags in the input text matching the pattern '{origin}{...}' and returns all matches.
        re_match_partial_flag(text: str, origin: str) -> list[str]:
            Searches for partial flags in the input text matching the pattern '{origin}{...}' or '{...}' and returns all matches.

    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class

        """
        pass

    def xor(self, text: str, key: str) -> str:
        """
        Description:
        XOR the text with the key

        Args:
            text (str): Text to XOR
            key (str): Key to XOR

        Returns:
            str: XORed text
        """
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(text, key))

    def decode_base64(self, text):
        """
        Description:
        Decode the base64 text

        Args:
            text (str): Base64 encoded text

        Returns:
            str: Decoded text
        """
        try:
            return base64.b64decode(text).decode("utf-8")
        except Exception as e:
            print(e)
            return None

    def re_match_base64_string(self, text: str, strict=False) -> list[str]:
        """
        Description:
        Find the base64 string in the text

        Args:
            text (str): Text to search for base64 string
            strict (bool, optional): If True, it will only return the base64 string. Defaults to False.

        Returns:
            str: list of Base64 string found in the text
        """
        if strict:
            base64_pattern = r"[A-Za-z0-9+/]{4,}={1,2}"
        else:
            base64_pattern = r"[A-Za-z0-9+/]{4,}={0,2}"
        base64_strings = re.findall(base64_pattern, text)
        return base64_strings

    def re_match_flag(self, text: str, origin: str) -> list[str]:
        """
        Description:
        Find the flag in the text

        Args:
            text (str): Text to search for the flag
            origin (str): Origin of the flag

        Returns:
            str: list of flag found in the text
        """
        flag_pattern = rf"{origin}{{[A-Za-z0-9_]+}}"
        return re.findall(flag_pattern, text)

    def re_match_partial_flag(self, text: str, origin: str) -> list[str]:
        """
        Description:
        Find the flag in the text or partial flag

        Args:
            text (str): Text to search for the flag
            origin (str): Origin of the flag

        Returns:
            str: list of flag found in the text
        """
        flag_pattern = rf"({origin}{{[^ ]*|[^ ]*}})"
        return re.findall(flag_pattern, text)
