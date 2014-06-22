from logging import getLogger
import gzip
from mimetypes import guess_type
from argparse import ArgumentParser
from program_state import State

def open_man_file(filename):
    ''' Opens file in text mode and unzips if necessary. '''
    logger = getLogger('man2html5')
    if guess_type(filename)[1] == 'gzip':
        try:
            return gzip.open(filename, mode='rt')
        except FileNotFoundError as err:
            logger.exception(err)
            exit(1)
    else:
        try:
            return open(filename)
        except FileNotFoundError as err:
            logger.exception(err)
            exit(1)

def initialize_get_args():
    ''' Returns command line arguments. '''
    parser = ArgumentParser(description='Manpage to HTML5 converter.')
    parser.add_argument('filename', type=str, help='manpage file to parse')
    return parser.parse_args()

def initialize():
    ''' Initializes program - opens files. '''
    logger = getLogger('man2html5')
    st = State()
    st.file_manpage = open_man_file(initialize_get_args().filename)
    try:
        st.file_html = open('result.html', 'wt')
    except FileNotFoundError as err:
        logger.exception(err)
        exit(1)

    return st

def deinitialize(st):
    ''' Closes opened files. '''
    st.file_html.close()
    st.file_manpage.close()

