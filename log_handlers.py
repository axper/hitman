''' Initializes file and console log handlers for the program.

    Each module initializes it's own logger object
    and configures it.
    This module just provides TO_FILE and TO_CONSOLE
    destinations for local loggers to attach to
    as handlers.
'''

# Standard modules
import logging

FILE_FS = '%(asctime)s %(filename)15s:%(funcName)-13s:%(lineno)-4d    %(levelname)7s:%(message)s'
CONSOLE_FS = '%(filename)15s:%(lineno)-4d    %(levelname)7s:%(message)s'

TO_FILE = logging.FileHandler('log')
TO_FILE.setLevel(logging.DEBUG)
TO_FILE.setFormatter(logging.Formatter(FILE_FS))

TO_CONSOLE = logging.StreamHandler()
TO_CONSOLE.setLevel(logging.INFO)
TO_CONSOLE.setFormatter(logging.Formatter(CONSOLE_FS))
