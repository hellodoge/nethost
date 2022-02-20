import re
import logging

from os          import path
from typing      import Set, Dict
from collections import defaultdict


PATTERNS = [r'{{ *([/\w\._-]+) * }}', r'href\s*=\s*"([/\w\._-]+)"', r'src\s*=\s*"([/\w\._-]+)"']


class LinksResolver:

    def __init__(self, filename: str):

        self.__filename = filename
        self.__dependency_to_matches: Dict[str, Set[str]] = defaultdict(set)

        logging.debug(f"LinksResolver: reading {filename}")

        try:
            with open(filename, 'r') as f:
                self.__text = f.read()
        except UnicodeDecodeError:
            logging.error("Nethost does not support non-utf-8 files, please host them elsewhere")
            raise

        for pattern in PATTERNS:
            for match in re.finditer(pattern, self.__text):
                dependency = match.group(1)
                if not path.isabs(dependency):
                    dependency = path.join(path.dirname(filename), dependency)

                dependency = path.normpath(dependency)

                logging.debug(f'Found dependency: {filename} -> {dependency}')

                self.__dependency_to_matches[dependency].add(match.group(0))


    def get_deps(self):
        return self.__dependency_to_matches.keys()


    def insert_links(self, filename_to_public_link: Dict[str, str]):
        for filename, public_link in filename_to_public_link.items():
            for match in self.__dependency_to_matches[filename]:
                self.__text = self.__text.replace(match, public_link)


    def get_text(self):

        for pattern in PATTERNS:
            assert len(re.findall(pattern, self.__text)) == 0

        return self.__text


    def get_filename(self):
        return self.__filename
