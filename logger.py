''' Initializes logging library for the program. '''
import logging

logger = logging.getLogger('man2html5')
logger.setLevel(logging.DEBUG)

log_to_file = logging.FileHandler('log')
log_to_file.setLevel(logging.DEBUG)
log_to_file.setFormatter(logging.Formatter('%(asctime)s '
                                           '%(filename)s '
                                           '%(lineno)4d '
                                           '%(levelname)s:'
                                           '%(message)s  '
                                           ))
logger.addHandler(log_to_file)

log_to_console = logging.StreamHandler()
log_to_console.setLevel(logging.INFO)
log_to_console.setFormatter(logging.Formatter('%(filename)s '
                                              '%(lineno)4d '
                                              '%(levelname)s:'
                                              '%(message)s  '
                                              ))
logger.addHandler(log_to_console)


# For escape_text_line()
logger_escape_text_line = logging.getLogger("man2html5.escape_text_line")
logger_escape_text_line.setLevel(logging.INFO)
