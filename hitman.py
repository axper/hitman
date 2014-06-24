#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
''' This program converts Manpages to HTML5. '''

# Standard modules
import re
import logging

# My modules
import log_handlers
import globstat
import init_deinit
import htmlops
import req

log = logging.getLogger('hitman')
log.addHandler(log_handlers.TO_CONSOLE)
log.addHandler(log_handlers.TO_FILE)
log.setLevel(logging.DEBUG)

def main():
    line_number = 1

    for line in globstat.state.file_manpage:
        line = line.rstrip('\n')

        log.debug('-'*40 + str(line_number) + '-'*40)
        log.debug(line)
        line_number += 1

        try:
            first_char = line[0]
        except IndexError:
            log.debug('type: empty line')
            req.HandleRequest.empty_line()
            continue

        if first_char in [globstat.state.control_char, globstat.state.control_char_nobreak]:
            try:
                request_name = re.match(' *([a-zA-Z0-9]+)', line[1:]).group(1)
            except AttributeError:
                log.debug('type: comment, fetching next line')
                continue

            try:
                command_info = req.requests[request_name]
            except KeyError:
                log.warning('unknown request: %s, fetching next line', request_name)
                continue

            log.debug('type: request: %s (%s)', request_name, command_info[0])

            try:
                request_handler_function = command_info[1]
            except IndexError:
                log.info('stub: request doesnt have handler: %s (%s), fetching next line', request_name, command_info[0])
                continue

            request_handler_function(line)

        else:
            log.debug('type: text')
            req.HandleRequest.text_line(line)


    req.HandleRequest.finalize()

    globstat.state.write(htmlops.HtmlRequests.document_footer())
    init_deinit.deinitialize(globstat.state)

if __name__ == '__main__':
    main()
