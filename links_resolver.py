import re
import logging

from os          import path
from typing      import Set, Dict
from collections import defaultdict


PATTERN = r'{{\ *([\w\._-]+)\ * }}'


class LinksResolver:

    def __init__(self, filename: str):

        self.__filename = filename
        self.__dependency_to_matches: Dict[str, Set[str]] = defaultdict(set)

        with open(filename, 'r') as f:
            self.__text = f.read()

        for match in re.finditer(PATTERN, self.__text):
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
        assert len(re.findall(PATTERN, self.__text)) == 0
        return self.__text


    def get_filename(self):
        return self.__filename
