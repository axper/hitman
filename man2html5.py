#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-

# This program convets Linux manpages to HTML5 format.

# groff(7), groff_me(7)
# groff_man(7), man(7) - groff linux man package (an.tmac macro package)
# groff_mdoc(7), mdoc(7), mdoc.samples(7) - groff bsd man pages


import mimetypes
import gzip
import csv
import cgi
import argparse
import logging
import re


def open_unzip_manpage(filename):
    ''' Opens file in text mode and unzips if necessary '''
    if mimetypes.guess_type(filename)[1] == 'gzip':
        return gzip.open(filename, mode='rt')
    else:
        return open(filename, mode='rt')

def parse_title(string):
    ''' Splits string into 5 parts while taking quotes into account '''
    title_line = string[3:].splitlines()
    return csv.reader(title_line, quotechar='"', delimiter=' ',
            quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

def section_name(section):
    ''' Returns name of manpage section number '''
    if section == '0':
        return 'POSIX headers'
    if section == '1':
        return 'Programs'
    elif section == '2':
        return 'System calls'
    elif section == '3':
        return 'Library calls'
    elif section == '4':
        return 'Special files'
    elif section == '5':
        return 'File formats'
    elif section == '6':
        return 'Games'
    elif section == '7':
        return 'Misc'
    elif section == '8':
        return 'System administration'
    elif section == '9':
        return 'Kernel routines'
    else:
        return 'UNKNOWN SECTION'

def matches_command(line, command):
    ''' Returns True if line starts with command. '''
    logger_matches.debug('Comparing %s and %s', line, command)
    if len(line) - 1 < len(command):
        logger_matches.debug('Comp returns False (length)')
        return False

    for i in range(len(command)):
        logger_matches.debug('Comp<%s><%s>', line[1 + i], command[i])
        if line[1 + i] != command[i]:
            break
    else:
        logger_matches.debug('Comp returns True')
        return True
    logger_matches.debug('Comp returns False')
    return False

def escape_paragraph(paragraph):
    ''' Escapes HTML and man commands. '''
    paragraph = cgi.escape(paragraph)

    paragraph = re.sub(r'\\-', '-', paragraph)

    return paragraph



logging.basicConfig(filename='log', level=logging.DEBUG)
logger_matches = logging.getLogger("matches_command")
logger_matches.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Converts Linux manpages to HTML5.')
parser.add_argument('file', type=str, help='manpage file to parse')
args = parser.parse_args()


manpage = open_unzip_manpage(args.file)
html = open('result.html', 'wt')


in_par = False

for line in manpage.read().splitlines():
    logging.debug('-' * 79)
    logging.debug(line)

    # Empty line
    if line == '':
        logging.debug('An empty line')
    # Command
    elif line[0] in ['\'', '.']:

        if matches_command(line, '\\"'):
            logging.debug('A comment')

        elif matches_command(line, 'TH'):
            logging.debug('A title line')

            title = parse_title(line)
            title[0] = title[0].lower()

            html.write('<!doctype HTML>\n')
            html.write('<html>\n')
            html.write('<head>\n')
            html.write('<meta charset=\'utf-8\'>\n')
            html.write('<title>' + title[0] + ' - ' + 
                    section_name(title[1]) + ' - ' +
                    'Man page</title>\n')
            html.write('<link rel=\'stylesheet\' type=\'text/css\' href=\'style.css\'>\n')
            html.write('</head>\n')
            html.write('<body>\n')
            html.write('<div id=\'content\'>\n')
            html.write('<h1>' + title[0] + '</h1>\n')

            logging.debug(title)

        elif matches_command(line, 'SH'):
            logging.debug('A section title')

            if in_par:
                html.write('</p>\n')
                in_par = False

            section_title = line[4:].capitalize()
            html.write('<h2>' + section_title + '</h2>\n')

            logging.debug(section_title)

        elif matches_command(line, 'BI'):
            logging.debug('Code (bold - italic)')

        elif matches_command(line, 'IB'):
            logging.debug('Code (italic - bold)')

        elif matches_command(line, 'BR'):
            logging.debug('Code (bold roman)')

        elif matches_command(line, 'RB'):
            logging.debug('Code (roman bold)')

        elif matches_command(line, 'IR'):
            logging.debug('Code (italic roman)')

        elif matches_command(line, 'RI'):
            logging.debug('Code (italic roman)')

        elif matches_command(line, 'SM'):
            logging.debug('Code (small)')

        elif matches_command(line, 'SB'):
            logging.debug('Code (small bold)')

        elif matches_command(line, 'I'):
            logging.debug('Code (italic)')

        elif matches_command(line, 'B'):
            logging.debug('Code (bold)')

            line = cgi.escape(line)
            line = line.replace('"', '')
            line = ' <code>' + line[3:].strip() + '</code> '

            if in_par:
                html.write(line)
            else:
                html.write('<p>')
                in_par = True
                html.write(line)

        else:
            logging.info('Unknown command: %s', line)

    else:
        logging.debug('A paragraph')

        linenew = escape_paragraph(line)
        if in_par:
            html.write(linenew)
        else:
            html.write('<p>')
            in_par = True
            html.write(linenew)

        logging.debug(linenew)


html.write('</div>\n')
html.write('</body>\n')
html.write('</html>\n')

manpage.close()
html.close()

