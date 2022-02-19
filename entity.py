import config
import requests
import logging

from hashes       import Hash
from urllib.parse import urljoin


class Entity:

    __PRIVATE_URL_FIELD = 'private_url'
    __PUBLIC_URL_FIELD  = 'public_url'
    __FILENAME_FIELD    = 'filename'
    __HASH_SUM_FIELD    = 'hash_sum'


    @staticmethod
    def create(filename: str):

        assert config.SERVER_URL

        logging.debug(f'Creating new entity for {filename}')

        create_url = urljoin(config.SERVER_URL, 'create')
        response = requests.get(create_url)
        response.raise_for_status()
        json = response.json()

        entity = Entity()

        entity.__private_url = json['Private link']
        entity.__public_url  = json['Public link']
        entity.__filename    = filename
        entity.__hash_sum    = Hash('')

        return entity


    @staticmethod
    def load(serialized: dict):

        assert type(serialized[Entity.__PRIVATE_URL_FIELD]) == str
        assert type(serialized[Entity.__PUBLIC_URL_FIELD])  == str
        assert type(serialized[Entity.__FILENAME_FIELD])    == str
        assert type(serialized[Entity.__HASH_SUM_FIELD])    == str

        entity = Entity()

        entity.__private_url = serialized[Entity.__PRIVATE_URL_FIELD]
        entity.__public_url  = serialized[Entity.__PUBLIC_URL_FIELD]
        entity.__filename    = serialized[Entity.__FILENAME_FIELD]
        entity.__hash_sum    = Hash.load(serialized[Entity.__HASH_SUM_FIELD])

        return entity


    def public_url(self):
        return self.__public_url


    def update(self, text: str):

        hash_sum = Hash(text)

        if hash_sum == self.__hash_sum:
            logging.debug(f'File {self.__filename} wasn\'t changed')
            return

        logging.info(f'Updating {self.__filename} ({self.__hash_sum} -> {hash_sum})')

        update_url = self.__private_url
        response = requests.put(update_url, text)
        response.raise_for_status()

        self.__hash_sum = hash_sum


    def save(self) -> dict:
        return {
            Entity.__PRIVATE_URL_FIELD: self.__private_url,
            Entity.__PUBLIC_URL_FIELD:  self.__public_url,
            Entity.__FILENAME_FIELD:    self.__filename,
            Entity.__HASH_SUM_FIELD:    self.__hash_sum.save()
        }
