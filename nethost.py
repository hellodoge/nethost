import os
import sys
import json
import config
import logging
import argparse

from entity         import Entity
from context        import Context
from links_resolver import LinksResolver
from typing         import Optional, Dict


def host_file(requested_file: str, context: Context):

    files = set()
    filename_to_links_resolver = dict()

    def add_file(filename):
        nonlocal files, filename_to_links_resolver

        links_resolver = LinksResolver(filename)
        filename_to_links_resolver[filename] = links_resolver

        files = set.union(files, links_resolver.get_deps(), {filename})

    add_file(requested_file)

    while files.difference(filename_to_links_resolver):
        for filename in files.difference(filename_to_links_resolver):
            add_file(filename)

    logging.debug(f'Total number of files: {len(files)}')

    filename_to_public_url = dict()

    for filename in files:
        entity = context.get_entity(filename)
        filename_to_public_url[filename] = entity.public_url()

    for links_resolver in filename_to_links_resolver.values():
        links_resolver.insert_links(filename_to_public_url)

    for filename, links_resolver in filename_to_links_resolver.items():
        entity = context.get_entity(filename)
        entity.update(links_resolver.get_text())
        logging.debug(f'{filename} hosted at {entity.public_url()}')


    logging.info(f'Public URL: {filename_to_public_url[requested_file]}')


def main(filename):

    if os.path.isfile(config.CONTEXT_PATH):
        with open(config.CONTEXT_PATH, 'r') as f:
            logging.debug(f'Loading the context from {config.CONTEXT_PATH}')
            context = Context.load(json.load(f))
    else:
        logging.info(f'Initializing new context ({config.CONTEXT_PATH})')
        context = Context.new_context()

    host_file(filename, context)

    if os.path.isfile(config.CONTEXT_PATH):
        backup_filename = config.CONTEXT_PATH + '.backup'
        logging.debug(f'Creating context backup ({backup_filename})')
        os.rename(config.CONTEXT_PATH, backup_filename)

    with open(config.CONTEXT_PATH, 'w') as f:
        json.dump(context.save(), f, indent=2)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('filename')

    parser.add_argument('--verbose', '-v',
                        dest='log_level', action='store_const',
                        const=logging.DEBUG, default=logging.INFO)

    parser.add_argument('--server', '-s', help='Netpipe server URL')

    parser.add_argument('--context', '-c', help='Path to context file',
                        default=config.CONTEXT_PATH)

    args = parser.parse_args()

    config.CONTEXT_PATH = args.context
    config.SERVER_URL   = args.server

    log_format = '%(levelname)s: %(message)s'
    logging.basicConfig(level=args.log_level, format=log_format)

    main(args.filename)
