''' Initializes logging library for the program.

    The result is the handle "LOGGER" shared between modules,
    it is used for general messages.
'''

# Standard modules
import logging

LOGGER = logging.getLogger('man2html5')
LOGGER.setLevel(logging.DEBUG)

LOG_TO_FILE = logging.FileHandler('log')
LOG_TO_FILE.setLevel(logging.DEBUG)
LOG_TO_FILE.setFormatter(logging.Formatter('%(asctime)s '
                                           '%(filename)s:'
                                           '%(lineno)4d '
                                           '%(levelname)s:'
                                           '%(message)s'
                                          ))
LOGGER.addHandler(LOG_TO_FILE)

LOG_TO_CONSOLE = logging.StreamHandler()
LOG_TO_CONSOLE.setLevel(logging.INFO)
LOG_TO_CONSOLE.setFormatter(logging.Formatter('%(filename)s:'
                                              '%(lineno)4d '
                                              '%(levelname)s:'
                                              '%(message)s'
                                             ))
LOGGER.addHandler(LOG_TO_CONSOLE)

