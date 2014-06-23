#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
''' This program converts Manpages to HTML5. '''

# Standard modules
import re

# My modules
import log
import globstat
import init_deinit
import htmlops
import req

line_number = 1

for line in globstat.state.file_manpage:
    line = line.rstrip('\n')

    log.logger.debug('-'*40 + str(line_number) + '-'*40)
    line_number += 1
    log.logger.debug(line)

    try:
        first_char = line[0]
    except IndexError:
        log.logger.debug('empty line')
        continue

    if first_char in [globstat.state.control_char, globstat.state.control_char_nobreak]:
        try:
            current_request = re.match(' *([a-zA-Z0-9]+)', line[1:]).group(1)
        except AttributeError:
            log.logger.debug('comment')
            continue

        try:
            command_info = req.requests[current_request]
        except KeyError:
            log.logger.info('unknown request:%s', current_request)
            continue
        log.logger.debug('request:%s', command_info)

        if len(command_info) >= 2:
            command_info[1](line)
        else:
            log.logger.info('stub: %s', command_info[0])

    else:
        log.logger.debug('Type: text line')
        req.HandleRequest.text_line(line)


req.HandleRequest.finalize()

globstat.state.write(htmlops.HtmlRequests.document_footer())
init_deinit.deinitialize(globstat.state)
