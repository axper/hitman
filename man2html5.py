#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-

# This program convets Linux manpages to HTML5 format.
# Used man file specifications:
# groff(7), groff_me(7), groff_man(7), man(7), info groff


import mimetypes
import gzip
import csv
import cgi
import argparse
import logging
import re

import mancommands


bold_start = '<code>'
bold_end = '</code>'
italic_start = '<code><i>'
italic_end = '</i></code>'


NORMAL = 0
BOLD = 1
ITALIC = 2


def open_man_file(filename):
    ''' Opens file in text mode and unzips if necessary. '''
    if mimetypes.guess_type(filename)[1] == 'gzip':
        return gzip.open(filename, mode='rt')
    else:
        return open(filename, mode='rt')

def split_with_quotes(string):
    ''' Splits string into words and takes quotes into account. '''
    title_line = string.splitlines()
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
        logging.warning('Unknown manpage section number: %s', section)
        return 'UNKNOWN SECTION'

def matches(line, command):
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

def sub_inline_font(par):
    ''' Parses man inline font escapes and replaces with HTML. '''
    italic = False
    bold = False

    i = 0
    while i < len(par) - 2:
        logger_font.debug(par[i:i+3])
        if par[i:i+3] == r'\fI':
            logger_font.debug('starting italic!!!')

            if not italic:
                italic = True
                par = par[:i] + italic_start + par[i+3:]
                logger_font.debug(par)
                i += len(italic_start) - 1
            else:
                logger_font.warning('already italic')

        elif par[i:i+3] == r'\fB':
            logger_font.debug('starting bold!!!')

            if not bold:
                bold = True
                par = par[:i] + bold_start + par[i+3:]
                logger_font.debug(par)
                i += len(bold_start) - 1
            else:
                logger_font.warning('already bold')

        elif par[i:i+3] in [r'\fR', r'\fP', r'\f1']:

            if italic:
                italic = False
                logger_font.debug('ending italic')
                par = par[:i] + italic_end + par[i+3:]
                logger_font.debug(par)
                i += len(italic_end) - 1
            elif bold:
                bold = False
                logger_font.debug('ending bold')
                par = par[:i] + bold_end + par[i+3:]
                logger_font.debug(par)
                i += len(bold_end) - 1
            else:
                logger_font.info('deleting non started font command')
                par = par[:i] + par[i+3:]
                logger_font.debug(par)

        i += 1

    if italic:
        logger_font.debug('ending italic (at the end)')
        par += italic_end
        logger_font.debug(par)
    elif bold:
        logger_font.debug('ending bold (at the end)')
        par += bold_end
        logger_font.debug(par)

    return par

def escape_paragraph(paragraph):
    ''' Escapes HTML and man commands. '''
    # Escape HTML chars
    paragraph = cgi.escape(paragraph)
    # Replace \-
    paragraph = re.sub(r'\\-', '-', paragraph)
    # Replace inline fonts
    paragraph = sub_inline_font(paragraph)

    return paragraph

def start_paragraph(file_html):
    ''' Writes <p> to html file. '''
    file_html.write('<p>')

def end_paragraph(file_html):
    ''' Writes </p> and newline to html file. '''
    file_html.write('</p>\n')

def alternating(st, line, first, second):
    ''' Writes HTML line alternating between first and second styles. '''
    if first == BOLD:
        even_start = bold_start
        even_end = bold_end
    elif first == ITALIC:
        even_start = italic_start
        even_end = italic_end
    elif first == NORMAL:
        even_start = ''
        even_end = ''
    else:
        logging.error("Incorrect first argument: %s", first)

    if second == BOLD:
        odd_start = bold_start
        odd_end = bold_end
    elif second == ITALIC:
        odd_start = italic_start
        odd_end = italic_end
    elif second == NORMAL:
        odd_start = ''
        odd_end = ''
    else:
        logging.error("Incorrect second argument: %s", second)

    words = split_with_quotes(escape_paragraph(line))
    final = ''

    even = True
    for i in words[1:]:
        if even:
            final += even_start + i + even_end
            even = False
        else:
            final += odd_start + i + odd_end
            even = True

    final += ' '
    logging.debug(final)
    st.file_html.write(final)

def initialize_logging():
    ''' Initializes logging library for the program. '''
    global logger_matches
    global logger_font

    logging.basicConfig(filename='log', level=logging.DEBUG)
    logger_matches = logging.getLogger("matches")
    logger_matches.setLevel(logging.INFO)
    logger_font = logging.getLogger("sub_inline_font")
    logger_font.setLevel(logging.INFO)

def initialize_get_args():
    ''' Returns command line arguments. '''
    parser = argparse.ArgumentParser(description='Converts Linux manpages to HTML5.')
    parser.add_argument('file', type=str, help='manpage file to parse')
    return parser.parse_args()

def initialize(st):
    ''' Initializes program: sets up logging and opens files. '''
    initialize_logging()

    st.file_manpage = open_man_file(initialize_get_args().file)
    st.file_html = open('result.html', 'wt')

class CommandHandlers:
    ''' Functions to handle requests at beginning of lines. '''
    def empty_line(st, line):
        logging.debug('empty line')

        if st.par:
            end_paragraph(st.file_html)

        st.par = False

    def sentence(st, line):
        logging.debug('sentence')

        linenew = escape_paragraph(line)
        linenew += '\n'

        if st.par:
            logging.debug('already in paragraph')
            st.file_html.write(linenew)
        else:
            logging.debug('starting paragraph')
            start_paragraph(st.file_html)
            st.par = True
            st.file_html.write(linenew)

        logging.debug(linenew)

class State:
    ''' The global state variables. '''
    file_manpage = None
    file_html = None
    par = False
    control_char = '.'
    control_char_nobreak = '\''
    escape_char = '\\'
    no_break = False

st = State()

initialize(st)


for line in st.file_manpage.read().splitlines():
    logging.debug('-' * 79)
    logging.debug(line)

    if line == '':
        CommandHandlers.empty_line(st, line)
        continue

    if line[0] == st.control_char_nobreak:
        st.no_break = True
    elif line[0] == st.control_char:
        st.no_break = False
    else:
        CommandHandlers.sentence(st, line)

    # Definitely a command now
    if matches(line, '\\"'):
        logging.debug('A comment')

    elif matches(line, 'TH'):
        logging.debug('A title line')

        title = split_with_quotes(line)[1:]
        title[0] = title[0].lower()

        st.file_html.write('<!doctype HTML>\n')
        st.file_html.write('<html>\n')
        st.file_html.write('<head>\n')
        st.file_html.write('<meta charset=\'utf-8\'>\n')
        st.file_html.write('<title>' + title[0] + ' - ' + 
                section_name(title[1]) + ' - ' +
                'Man page</title>\n')
        st.file_html.write('<link rel=\'stylesheet\' type=\'text/css\''
                ' href=\'style.css\'>\n')
        st.file_html.write('</head>\n')
        st.file_html.write('<body>\n')
        st.file_html.write('<h1>' + title[0] + '</h1>\n')

        logging.debug(title)

    elif matches(line, 'SH'):
        logging.debug('A section title')

        if st.par:
            end_paragraph(st.file_html)
            st.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        st.file_html.write('<h2>' + section_title + '</h2>\n')

        logging.debug(section_title)
    
    elif matches(line, 'SS'):
        logging.debug('A subsection title')

        if st.par:
            end_paragraph(st.file_html)
            st.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        st.file_html.write('<h3>' + section_title + '</h3>\n')

        logging.debug(section_title)

    elif matches(line, 'PP') or matches(line, 'P ') or matches(line, 'LP'):
        logging.debug('Begin new state paragraph')

        if st.par:
            end_paragraph(st.file_html)
            start_paragraph(st.file_html)
        else:
            st.par = True
            start_paragraph(st.file_html)

    elif matches(line, 'HP') or matches(line, 'IP') or matches(line, 'TP'):
        logging.info('Begin hanging or indented paragraph (ignoring...)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True
        else:
            end_paragraph(st.file_html)
            start_paragraph(st.file_html)

    elif matches(line, 'BI'):
        logging.debug('Code (bold - italic)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, BOLD, ITALIC)

    elif matches(line, 'IB'):
        logging.debug('Code (italic - bold)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, ITALIC, BOLD)

    elif matches(line, 'BR'):
        logging.debug('Code (bold - normal)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, BOLD, NORMAL)

    elif matches(line, 'RB'):
        logging.debug('Code (normal - bold)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, NORMAL, BOLD)

    elif matches(line, 'IR'):
        logging.debug('Code (italic - normal)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, ITALIC, NORMAL)

    elif matches(line, 'RI'):
        logging.debug('Code (italic - normal)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        alternating(st, line, NORMAL, ITALIC)

    elif matches(line, 'SM'):
        logging.debug('Code (small)')
        logging.info('STUB')

    elif matches(line, 'SB'):
        logging.debug('Code (small bold)')
        logging.info('STUB')

    elif matches(line, 'I '):
        logging.debug('Code (italic)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        final = ''
        final += italic_start
        final += ' '.join(split_with_quotes(escape_paragraph(line))[1:])
        final += italic_end
        final += ' '

        logging.debug(final)
        st.file_html.write(final)

    elif matches(line, 'B '):
        logging.debug('Code (bold)')

        if not st.par:
            start_paragraph(st.file_html)
            st.par = True

        final = ''
        final += bold_start
        final += ' '.join(split_with_quotes(escape_paragraph(line))[1:])
        final += bold_end
        final += ' '

        logging.debug(final)
        st.file_html.write(final)

    elif matches(line, 'UR'):
        logging.debug('Start URL')

    elif matches(line, 'br') or matches(line, 'sp'):
        logging.debug('Line break')

        if st.par:
            end_paragraph(st.file_html)

        st.par = False

    else:
        logging.info('Unknown command: %s', line)


if st.par:
    end_paragraph(st.file_html)
    st.par = False



st.file_html.write('</body>\n')
st.file_html.write('</html>\n')

st.file_manpage.close()
st.file_html.close()

