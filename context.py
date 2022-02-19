import config
import logging

from typing import Dict
from entity import Entity

class Context:

    __SERVER_URL_FIELD = 'server_url'
    __FILES_FIELD      = 'files'


    @staticmethod
    def new_context():
        context = Context()

        if not config.SERVER_URL:
            raise RuntimeError('Please, specify the server URL')

        context.__server_url = config.SERVER_URL
        context.__filename_to_entity: Dict[str, Entity] = dict()

        return context


    @staticmethod
    def load(serialized):
        context = Context()

        assert type(serialized[Context.__SERVER_URL_FIELD]) == str
        assert type(serialized[Context.__FILES_FIELD])      == dict

        context.__server_url         = serialized[Context.__SERVER_URL_FIELD]
        context.__filename_to_entity = dict()

        for file, entity in serialized[Context.__FILES_FIELD].items():
            context.__filename_to_entity[file] = Entity.load(entity)

        if not config.SERVER_URL:
            logging.debug('Loading server URL from the context')
            config.SERVER_URL = context.__server_url

        if config.SERVER_URL != context.__server_url:
            logging.warning(f'Server URL has changed! Entity information will be recreated')
            context.__filename_to_entity.clear()

        return context


    def get_entity(self, filename) -> Entity:
        if filename not in self.__filename_to_entity:
            self.__filename_to_entity[filename] = Entity.create(filename)
        return self.__filename_to_entity[filename]


    def save(self) -> dict:

        files = {k: v.save() for k, v in self.__filename_to_entity.items()}

        return {
            Context.__SERVER_URL_FIELD: self.__server_url,
            Context.__FILES_FIELD: files
        }

