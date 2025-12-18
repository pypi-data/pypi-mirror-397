# from ctfsolver import CTFSolver
from string import ascii_letters, digits, punctuation
from collections import defaultdict
import itertools


class PositionCipher:

    def load_lyrics(self):

        files = [
            "lyrics_partial.txt",
            "lyrics.txt",
            "greek_lyrics.txt",
            "genius_lyrics.txt",
        ]

        with open(self.folfil("data", files[1]), "r") as f:
            lyrics = f.read().strip()
        return lyrics

    def dictionary_analysis(self, lyrics):
        d = defaultdict(list)
        for i, c in enumerate(lyrics):
            d[c].append(i)
        return d

    def print_dictionary(self, d):
        sorted_items = sorted(d.items(), key=lambda x: x[0])
        for key, value in sorted_items:
            print(f"{key}: {value}")

    def lyric_transpose(self, lyrics, offset, wrap=True):
        if offset > len(lyrics):
            offset = offset % len(lyrics)

        result = lyrics[offset:]
        if wrap:
            result += lyrics[:offset]

        return result

    def lyric_transformation(self, lyrics):

        punctuation_used = set()
        for c in lyrics:
            if c not in ascii_letters + digits + " ":
                punctuation_used.add(c)

        lyrics_only_letters = "".join([c for c in lyrics if c.isalnum()])
        lyrics_with_spaces = lyrics.replace("\n", " ")
        lyrics_without_punctuation = lyrics_with_spaces.replace("'", "").replace(
            ",", ""
        )
        return lyrics_only_letters, lyrics_with_spaces, lyrics_without_punctuation

    def lyrics_all(self):
        """
        Description:
            This function generates all possible combinations of lyrics transformations
            based on the provided replace_combos and control_combos.
            It uses itertools.product to create combinations of the specified number
            of transformations, allowing for flexible lyric manipulation.
        Returns:
            list: A list of transformed lyrics combinations.
        """
        lyrics = self.load_lyrics()
        control_combos = self.creating_control_combos(
            start=0, end=1, number=len(self.replace_combos)
        )
        return [
            self.lyrics_transformation(lyrics, self.replace_combos, control)
            for control in control_combos
        ]

    def creating_control_combos(self, start=0, end=1, number=8):
        if start >= end:
            raise ValueError("Start must be less than end.")
        if number < 1:
            raise ValueError("Number of combinations must be at least 1.")
        return list(itertools.product(range(start, end + 1), repeat=number))

    def lyrics_transformation(self, lyrics, replace_combos, control_combos=None):
        if control_combos is None:
            return lyrics

        for control, combo in zip(control_combos, replace_combos):
            if control:
                if len(combo[0]) > 1:
                    lyrics = lyrics.replace(*combo[0]).replace(*combo[1])
                else:
                    lyrics = lyrics.replace(*combo)
        return lyrics

    def brute_transpose_find_flag(
        self,
        lyrics: str,
        partial_flag: str,
        keys: list,
        verbose: bool = False,
        wrap: bool = True,
    ):
        """
        Description:
            For the lyrics given

        Args:
            lyrics (str): Lyrics given
            partial_flag (str): partial flag to look
            verbose (bool, optional): _description_. Defaults to False.

        Returns:
            str: possible flag
        """

        for i in range(len(lyrics)):
            transposed = self.lyric_transpose(lyrics, i, wrap=wrap)
            if verbose and i % 100 == 0:
                print(f"Trying offset: {i}")
            temp_flag = self.position_cipher(transposed, keys)
            if "ecsc" in temp_flag.lower() or self.check_for_rot(
                temp_flag, partial_flag
            ):
                print(f"Found flag: {temp_flag} - Offset: {i}")
                return temp_flag

    def check_for_rot(self, text, partial="ecsc"):
        """
        Description:
            Checks if the text is a rotation of "ecsc".
            This function checks if the first four characters of the text
            can be rearranged to form the string "ecsc". It does this by
            comparing the ASCII values of the characters in the text with
            the ASCII values of the characters in "ecsc". If the conditions
            are met, it returns True, indicating that the text is a rotation
            of "ecsc". Otherwise, it returns False.
            This function is useful for identifying specific patterns in the text
            that match the structure of "ecsc", which could be relevant in certain

            Challenge_specific
        Args:
            text (_type_): _description_

            
            
        Returns:
            _type_: _description_
        """

        if len(partial) != 4:
            raise ValueError(
                "Partial must be exactly 4 characters long. Challenge_specific"
            )
        text = text.lower()

        check1 = (ord(partial[0]) - ord(partial[1])) == (ord(text[0]) - ord(text[1]))
        check2 = (ord(partial[2]) - ord(partial[1])) == (ord(text[2]) - ord(text[1]))
        check3 = ord(text[3]) == ord(text[1])

        return check1 and check2 and check3

    def position_cipher(self, text: str, keys: list):
        """
        Description:
            This function takes a text and a list of keys, and returns a new string
            where each character in the text is replaced by the character at the
            corresponding index in the keys list. If the index exceeds the length of
            the text, it wraps around using modulo operation.
        Args:
            text (str): The input text to be transformed.
            keys (list): A list of integers representing the positions in the text.
        Returns:
            str: A new string formed by replacing characters in the text based on the keys.
        """

        return "".join(text[i % len(text)] for i in keys)

    def bruteforce_all_lyrics(
        self,
        all_lyrics: list,
        partial_flag: str,
        keys: list,
        verbose: bool = False,
        wrap: bool = True,
    ):
        results = []
        for lyric_i, lyrics in enumerate(all_lyrics):
            if verbose:
                print(f"Processing lyrics {lyric_i + 1}/{len(all_lyrics)}")
            result = self.brute_transpose_find_flag(
                lyrics=lyrics,
                partial_flag=partial_flag,
                keys=keys,
                verbose=verbose,
                wrap=wrap,
            )
            if result:
                results.append([lyric_i, result])

        return results

    def init_some_values(self):
        self.key = [
            7,
            58,
            391,
            58,
            129,
            80,
            537,
            80,
            389,
            33,
            80,
            107,
            522,
            391,
            389,
            148,
            386,
            522,
            389,
            58,
            240,
            240,
            107,
            1,
        ]

        self.replace_combos = [
            (" ", ""),
            (",", " "),
            ((",", " "), ("'", " ")),
            ((",", ""), ("'", "")),
            (",", ""),
            ("'", " "),
            ("'", ""),
            ("\n", " "),
            ("\n", ""),
        ]

    def another_attempt(self):

        lyrics = self.load_lyrics()

        lyrics_only_letters, lyrics_with_spaces, lyrics_without_punctuation = (
            self.lyric_transformation(lyrics)
        )

        print(lyrics_only_letters)
        print(lyrics_with_spaces)
        print(lyrics_without_punctuation)

        # flag = self.bruteforce(lyrics, self.key)
        # print(flag)
        # flag = self.bruteforce(lyrics_only_letters, self.key)
        # print(flag)
        flag = self.brute_transpose_find_flag(lyrics_with_spaces, self.key)
        print(flag)
        flag = self.brute_transpose_find_flag(lyrics_without_punctuation, self.key)
        print(flag)

    def main(self):

        self.init_some_values()

        all_lyrics = self.lyrics_all()

        partial_flag = "ecsc"

        results = self.bruteforce_all_lyrics(
            all_lyrics, partial_flag, keys=self.key, verbose=True, wrap=True
        )
        if results:
            for lyric_i, result in results:
                print(f"Lyric {lyric_i + 1}: {result}")
        else:
            print("No results found.")
