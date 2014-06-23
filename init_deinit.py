# Standard modules
import logging
import gzip
import mimetypes
import argparse

# My modules
import state_object

def open_man_file(filename):
    ''' Opens file in text mode and unzips if necessary. '''
    logger = logging.getLogger('man2html5')
    if mimetypes.guess_type(filename)[1] == 'gzip':
        try:
            logger.debug('gzfile:===============' + filename + '=================')
            return gzip.open(filename, mode='rt')
        except FileNotFoundError as err:
            logger.exception(err)
            exit(1)
    else:
        try:
            logger.debug('normfile:===============' + filename + '=================')
            return open(filename)
        except FileNotFoundError as err:
            logger.exception(err)
            exit(1)

def initialize_get_args():
    ''' Returns command line arguments. '''
    parser = argparse.ArgumentParser(description='Manpage to HTML5 converter.')
    parser.add_argument('filename', type=str, help='manpage file to parse')
    return parser.parse_args()

def initialize():
    ''' Initializes program - opens files. '''
    logger = logging.getLogger('man2html5')
    state = state_object.State()
    state.file_manpage = open_man_file(initialize_get_args().filename)
    try:
        state.file_html = open('result.html', 'wt')
    except FileNotFoundError as err:
        logger.exception(err)
        exit(1)

    return state

def deinitialize(state):
    ''' Closes opened files. '''
    state.file_html.close()
    state.file_manpage.close()

