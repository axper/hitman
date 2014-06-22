#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
''' This program converts Manpages to HTML5. '''

# This program convets Linux manpages to HTML5 format.
# Used man file specifications:
# groff(7), groff_me(7), groff_man(7), man(7), info groff

# List of similar projects:
# man2html
#     text output with everything in black monospace font
# man2web
#     same as man2html
# roffit
#     can't handle more complex pages with groff commands
# man -H
#     can't properly format gcc(1)


import mimetypes
import gzip
import csv
import argparse
import logging
import re
import html



NORMAL = 0
BOLD = 1
ITALIC = 2


def open_man_file(filename):
    ''' Opens file in text mode and unzips if necessary. '''
    logging.debug('OPENING:' + filename)
    if mimetypes.guess_type(filename)[1] == 'gzip':
        try:
            return gzip.open(filename, mode='rt')
        except FileNotFoundError as err:
            print(err)
            exit(1)
    else:
        try:
            return open(filename)
        except FileNotFoundError as err:
            print(err)
            exit(1)

def split_with_quotes(string):
    ''' Splits string into words and takes quotes into account. '''
    return csv.reader(string.splitlines(), quotechar='"', delimiter=' ',
                      quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

def escape_text_line2(text_line):
    # First handle ampersands(&) after escape
    # It must be done before HTML escaping
    text_line = text_line.replace('\\&', '&amp;')
    logging.debug('after&:' + text_line)

    # Now escape HTML
    text_line = html.escape(text_line)
    logging.debug('afterH:' + text_line)

    # Now groff escape codes
    index = 0
    for index in range(len(text_line)):
        if text_line[index] == st.escape_char:
            if index == len(text_line) - 1:
                logging.info('stub: escape char is the last letter')
                continue

            escape_code = text_line[index + 1]

            if escape_code not in escapes:
                d('stub:unknown escape code:' + escape_code)
                continue

            logging.debug('escape:' + escape_code + '  means: ' + escapes[escape_code][0])

def escape_text_line(paragraph):
    ''' Escapes HTML and man commands. '''
    # Escape HTML chars
    paragraph = html.escape(paragraph)

    bold_start = '<code><b>'
    bold_end = '</b></code>'

    italic_start = '<code><i>'
    italic_end = '</i></code>'

    italic = False
    bold = False

    i = 0
    while i < len(paragraph) - 2:
        logger_font.debug(paragraph[i:i+3])
        if paragraph[i:i+3] == r'\fI':
            logger_font.debug('starting italic!!!')

            if not italic:
                italic = True
                paragraph = paragraph[:i] + italic_start + paragraph[i+3:]
                logger_font.debug(paragraph)
                i += len(italic_start) - 1
            else:
                logger_font.warning('already italic')

        elif paragraph[i:i+3] == r'\fB':
            logger_font.debug('starting bold!!!')

            if not bold:
                bold = True
                paragraph = paragraph[:i] + bold_start + paragraph[i+3:]
                logger_font.debug(paragraph)
                i += len(bold_start) - 1
            else:
                logger_font.warning('already bold')

        elif paragraph[i:i+3] in [r'\fR', r'\fP', r'\f1']:

            if italic:
                italic = False
                logger_font.debug('ending italic')
                paragraph = paragraph[:i] + italic_end + paragraph[i+3:]
                logger_font.debug(paragraph)
                i += len(italic_end) - 1
            elif bold:
                bold = False
                logger_font.debug('ending bold')
                paragraph = paragraph[:i] + bold_end + paragraph[i+3:]
                logger_font.debug(paragraph)
                i += len(bold_end) - 1
            else:
                logger_font.info('deleting non started font command')
                paragraph = paragraph[:i] + paragraph[i+3:]
                logger_font.debug(paragraph)

        i += 1

    if italic:
        logger_font.debug('ending italic (at the end)')
        paragraph += italic_end
        logger_font.debug(paragraph)
    elif bold:
        logger_font.debug('ending bold (at the end)')
        paragraph += bold_end
        logger_font.debug(paragraph)

    return paragraph

def alternating(st, line, first, second):
    ''' Writes HTML line alternating between first and second styles. '''

    bold_start = '<code><b>'
    bold_end = '</b></code>'

    italic_start = '<code><i>'
    italic_end = '</i></code>'

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

    words = split_with_quotes(escape_text_line(line))
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
    d(final)
    html_writer.write_string(final)

def initialize_logging():
    ''' Initializes logging library for the program. '''
    global logger_matches
    global logger_font

    logging.basicConfig(filename='log', level=logging.DEBUG)
    logger_font = logging.getLogger("sub_inline_font")
    logger_font.setLevel(logging.INFO)

def initialize_get_args():
    ''' Returns command line arguments. '''
    parser = argparse.ArgumentParser(description='Manpage to HTML5 converter.')
    parser.add_argument('file', type=str, help='manpage file to parse')
    return parser.parse_args()

def initialize(st):
    ''' Initializes program: sets up logging and opens files. '''
    initialize_logging()

    st.file_manpage = open_man_file(initialize_get_args().file)
    try:
        st.file_html = open('result.html', 'wt')
    except FileNotFoundError as err:
        print(err)
        exit(1)

def deinitialize(st):
    ''' Closes opened files. '''
    st.file_html.close()
    st.file_manpage.close()


class State:
    ''' The global state variables. '''
    file_manpage = None
    file_html = None
    par = False
    control_char = '.'
    control_char_nobreak = '\''
    escape_char = '\\'
    no_break = False
    ignore_until_doubledot = False

class HtmlWriter:
    paragraph_start = '<p>\n'
    paragraph_end = '</p>\n'

    bold_start = '<code><b>'
    bold_end = '</b></code>'

    italic_start = '<code><i>'
    italic_end = '</i></code>'

    # title[0]
    # title[1]
    # title[0]
    header = '<!doctype HTML>\n' \
            '<html>\n' \
            '<head>\n' \
            '<meta charset=\'utf-8\'>\n' \
            '<title>{0} - {1} - Man page</title>\n' \
            '<link rel=\'stylesheet\' type=\'text/css\' href=\'style.css\'>\n' \
            '</head>\n' \
            '<body>\n' \
            '<h1>{0}</h1>\n'
    footer = '</body>\n' \
            '</html>\n'

    def __init__(self, html_file):
        self.html_file = html_file

    def write_string(self, s):
        self.html_file.write(s)

    def write_html_header(self, title):
        if title[1] not in section_name:
            d('stub:unknown section name:' + title[1])
            return
        self.html_file.write(self.header.format(title[0],
                                                section_name[title[1]]))

    def write_html_footer(self):
        self.html_file.write(self.footer)

    def start_paragraph(self):
        self.html_file.write(self.paragraph_start)

    def end_paragraph(self):
        self.html_file.write(self.paragraph_end)

    def start_bold(self):
        self.html_file.write(self.bold_start)

    def end_bold(self):
        self.html_file.write(self.bold_end)

    def start_italic(self):
        self.html_file.write(self.italic_start)

    def end_italic(self):
        self.html_file.write(self.italic_end)



class Request:
    ''' Functions to handle requests at beginning of lines. '''
    def empty_line(st):
        if st.par:
            html_writer.end_paragraph()

        st.par = False

    def text_line(st, line):
        escape_text_line2(line)
        '''
        linenew = ' '.join(split_with_quotes(escape_text_line(line)))
        linenew += '\n'

        if st.par:
            d('already in paragraph')
            st.file_html.write(linenew)
        else:
            d('starting paragraph')
            html_writer.start_paragraph()
            st.par = True
            st.file_html.write(linenew)

        d(linenew)
        '''

    def comment(st, line):
        pass

    def title(st, line):
        title = split_with_quotes(line)[1:]
        title[0] = title[0].lower()

        html_writer.write_html_header(title)

        d(title)

    def section_title(st, line):
        if st.par:
            html_writer.end_paragraph()
            st.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        st.file_html.write('<h2>' + section_title + '</h2>\n')

        d(section_title)

    def subsection_title(st, line):
        if st.par:
            html_writer.end_paragraph()
            st.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        st.file_html.write('<h3>' + section_title + '</h3>\n')

        d(section_title)

    def new_paragraph(st, line):
        if st.par:
            html_writer.end_paragraph()
            html_writer.start_paragraph()
        else:
            st.par = True
            html_writer.start_paragraph()

    def hanging_indented_paragraph(st, line):
        logging.info('hanging or indented paragraph (ignoring...)')

        if not st.par:
            html_writer.start_paragraph()
            st.par = True
        else:
            html_writer.end_paragraph()
            html_writer.start_paragraph()

    def alt_bold_italic(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, BOLD, ITALIC)

    def alt_italic_bold(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, ITALIC, BOLD)

    def alt_bold_normal(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, BOLD, NORMAL)

    def alt_normal_bold(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, NORMAL, BOLD)

    def alt_italic_normal(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, ITALIC, NORMAL)

    def alt_normal_italic(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        alternating(st, line, NORMAL, ITALIC)

    def font_italic(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        html_writer.start_italic()
        parsed = ' '.join(split_with_quotes(escape_text_line(line))[1:])
        st.file_html.write(parsed)
        html_writer.end_italic()
        st.file_html.write(' ')

    def font_bold(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        html_writer.start_bold()
        parsed = ' '.join(split_with_quotes(escape_text_line(line))[1:])
        st.file_html.write(parsed)
        html_writer.end_bold()
        st.file_html.write(' ')

    def line_break(st, line):
        if st.par:
            html_writer.end_paragraph()

        st.par = False

    def finalize(st):
        if st.par:
            html_writer.end_paragraph()
            st.par = False


section_name = {
    '0' : 'POSIX headers',
    '1' : 'Programs',
    '2' : 'System calls',
    '3' : 'Library calls',
    '4' : 'Special files',
    '5' : 'File formats',
    '6' : 'Games',
    '7' : 'Misc',
    '8' : 'System administration',
    '9' : 'Kernel routines',
}

# Just the control char by itself on the line is ignored
requests = {
    '.' : ('just a single dot', ),
    '\\"' : ('comment', Request.comment),

    ## Man macro package
    # 2. Usage
    'TH' : ('title line', Request.title),
    'SH' : ('section title', Request.section_title),
    'SS' : ('subsection title', Request.subsection_title),
    'LP' : ('new paragraph 1', Request.new_paragraph),
    'PP' : ('new paragraph 2', Request.new_paragraph),
    'P' : ('new paragraph 3', Request.new_paragraph),
    'TP' : ('new paragraph hanging 1', Request.hanging_indented_paragraph),
    'IP' : ('new paragraph hanging 2', Request.hanging_indented_paragraph),
    'HP' : ('new paragraph hanging 3', Request.hanging_indented_paragraph),
    'RS' : ('start indent', ),
    'RE' : ('end indent', ),

    # 3. Font
    'SM' : ('font small', ),
    'SB' : ('font small alt bold', ),
    'BI' : ('font bold alt italic', Request.alt_bold_italic),
    'IB' : ('font italic alt bold', Request.alt_italic_bold),
    'RI' : ('font normal alt italic', Request.alt_normal_italic),
    'IR' : ('font italic alt normal', Request.alt_italic_normal),
    'BR' : ('font bold alt normal', Request.alt_bold_normal),
    'RB' : ('font normal alt bold', Request.alt_normal_bold),
    'B' : ('font bold', Request.font_bold),
    'I' : ('font italic', Request.font_italic),
    #('R' : ('font normal', ),

    # 4. Misc
    'DT' : ('reset tabs to default', ),
    'PD' : ('set distance between paragraphs', ),
    'AT' : ('set at&t unix version (dont use)', ),
    'UC' : ('set bsd version (dont use)', ),

    # 7. Optional extensions
    'PT' : ('print header string', ),
    'BT' : ('print footer string', ),
    'CT' : ('print ctrl key', ),
    'CW' : ('font monospace', ),
    'Ds' : ('begin nonfilled display', ),
    'De' : ('end nonfilled display', ),
    'G' : ('font helvetica', ),
    'GL' : ('font helvetica oblique', ),
    'HB' : ('font helvetica bold 1', ),
    'TB' : ('font helvetica bold 2', ),
    'MS' : ('manpage reference ultrix', ),
    'PN' : ('set path name 1', ),
    'Pn' : ('set path name 2', ),
    'RN' : ('print <RETURN>', ),
    'VS' : ('start change bar', ),
    'VE' : ('end change bar', ),

    # Other (not described in groff info page for man)
    # Example
    'EX' : ('start example', ),
    'EE' : ('end example', ),
    # URL
    'URL' : ('url groff', ),
    'UR' : ('start url', ),
    'UE' : ('end url', ),
    # Email
    'MT' : ('start email', ),
    'ME' : ('end email', ),
    # Synopsis
    'SY' : ('start indented synopsis', ),
    'YS' : ('end indented synopsis', ),
    'OP' : ('synopsis optional command', ),
    # Note
    'NT' : ('begin note', ),
    'NE' : ('end note', ),
    # Paragraph indent
    'TQ' : ('new paragraph hanging 4', ),
    # Unknown
    'UN' : ('Unknown!!!', ),


    ## Requests from gtroff info page
    # 5. Comments
    'ig' : ('ignore until .. or macro encounters', ),

    # 6. Registers
    'nr' : ('define register', ),
    'rr' : ('remove register', ),
    'rnn' : ('rename register', ),
    'aln' : ('create alias name for register', ),
    'af' : ('set register output format', ),

    # 7. Manipulating filling and adjusting
    'br' : ('line break', Request.line_break),
    'fi' : ('enable output fill mode', ),
    'nf' : ('disable output fill mode', ),
    'ad' : ('set line adjusting mode', ),
    'na' : ('disable output line adjusting', ),
    'brp' : ('break and adjust (spread) current line', ),
    'ss' : ('change space size between words', ),
    'ce' : ('center next line', ),
    'rj' : ('right justify text', ),

    # 8. Manipulating hypenation
    'hy' : ('enable hypenation', ),
    'nh' : ('disable hypenation', ),
    'hlm' : ('set max hypenated lines', ),
    'hw' : ('define exceptional hypenation for words', ),
    'hc' : ('switch additional hypenation indicator char', ),
    'hpf' : ('read hypenation patterns from file', ),
    'hpfa' : ('append hypenation patterns from file', ),
    'hpfcode' : ('set input mapping for hpf', ),
    'hcode' : ('set hypenation code of char', ),
    'hym' : ('set right hypenation margin', ),
    'hys' : ('set hypenation space', ),
    'shc' : ('set soft hypen char', ),
    'hla' : ('set hypenation language', ),

    # 9. Manipulating spacing
    'sp' : ('skip lines up or down', Request.line_break),
    'ls' : ('print blank lines after each output', ),
    'ns' : ('disable line spacing mode', ),
    'rs' : ('enable line spacing mode', ),

    # 10. Tabs and fields
    'ta' : ('set tab stop positions', ),
    'tc' : ('set tab fill char (space)', ),
    'linetabs' : ('switch relative tab distance computing mode', ),
    'lc' : ('switch leader repetition char', ),
    'fc' : ('define delimiting and padding char for fields', ),

    # 11. Character translations
    'cc' : ('set control character (dot)', ),
    'c2' : ('set no break control character (singlequote)', ),
    'eo' : ('disable character esacaping', ),
    'ec' : ('set escape char (backslash)', ),
    'ecs' : ('save current escape char (backslash)', ),
    'ecr' : ('restore saved escape char (backslash)', ),
    'tr' : ('translate char to glyph 1', ),
    'trin' : ('translate char to glyph 2', ),
    'trnt' : ('translate char to glyph 3', ),

    # 12. Troff and Nroff modes
    'nroff' : ('enable condition n and disable condition t', ),
    'troff' : ('enable condition t and disable condition n', ),

    # 13. Line layout
    'po' : ('set horizontal page offset', ),
    'in' : ('set indentation', ),
    'ti' : ('temporary indent next line', ),
    'll' : ('set line length', ),

    # 15. Page layout
    'pl' : ('set page length', ),
    'tl' : ('print title line', ),
    'lt' : ('set length of title', ),
    'pn' : ('set page number', ),
    'pc' : ('set page number character', ),

    # 16. Page control
    'bp' : ('new page', ),
    'ne' : ('reserve vertical space 1', ),
    'sv' : ('reserve vertical space 2', ),
    'os' : ('reserve vertical space 3', ),

    # 17. Fonts and symbols
    # Changing fonts
    'ft' : ('set font or font position', ),
    'ftr' : ('alias font', ),
    'fzoom' : ('set font zoom', ),
    # Font Families
    'fam' : ('set font family', ),
    'sty' : ('set style for font position', ),
    # Font positions
    'fp' : ('mount font to position', ),
    # Using symbols
    'composite' : ('map glyph name', ),
    'cflags' : ('set char properties', ),
    'char' : ('print string instead of char 1', ),
    'fchar' : ('print string instead of char 2', ),
    'fschar' : ('print string instead of char 3', ),
    'schar' : ('print string instead of char 4', ),
    'rchar' : ('remove char definition', ),
    'rfschar' : ('remove char definition for font', ),
    # Characater classes
    'class' : ('define class of characters', ),
    # Special fonts
    'special' : ('set special font 1', ),
    'fspecial' : ('set special font 2', ),
    # Artificial fonts
    'ul' : ('underline next n input lines', ),
    'cu' : ('underline font and space', ),
    'uf' : ('set underline font', ),
    'bd' : ('create bold font by printing twice', ),
    'cs' : ('set constant glyph width mode for font', ),
    # Ligatures and kerning
    'lg' : ('switch ligature mode', ),
    'kern' : ('switch kerning', ),
    'tkf' : ('enable track kerning for font', ),

    # 18. Sizes
    'ps' : ('set font size', ),
    'sizes' : ('change allowed font sizes', ),
    'vs' : ('change vertical font size', ),
    'pvs' : ('change post vertical line spacing', ),

    # 19. Strings
    'ds' : ('define string var', ),
    'ds1' : ('define string var nocompat', ),
    'as' : ('append to string var', ),
    'as1' : ('append to string var nocompat', ),
    'substring' : ('substitue in string', ),
    'length' : ('get string length', ),
    'rn' : ('rename something', ),
    'rm' : ('remove something', ),
    'als' : ('create alias name for something', ),
    'chop' : ('remove last character from thing', ),

    # 20. Conditionals and loops
    'if' : ('if condition', ),
    'nop' : ('execute nothing', ),
    'ie' : ('else if', ),
    'el' : ('else', ),
    'while' : ('while loop', ),
    'break' : ('break out of loop', ),
    'continue' : ('continue loop', ),

    # 21. Writing macros
    'de' : ('define macro 1', ),
    'de1' : ('define macro nocompat', ),
    'dei' : ('define macro 2', ),
    'dei1' : ('define macro 2 nocompat', ),
    'am' : ('append to macro', ),
    'am1' : ('append to macro nocompat', ),
    'ami' : ('append to macro whose name is stored in', ),
    'ami1' : ('append to macro whose name is stored in nocompat', ),
    'return' : ('return from macro', ),
    'shift' : ('shift macro arguments', ),

    # 22. Page motions
    'mk' : ('put current line number into register', ),
    'rt' : ('return to marked line number', ),

    # 24. Traps (macro calls)
    'vpt' : ('switch vertical position traps', ),
    'wh' : ('set line number trap', ),
    'ch' : ('change trap location', ),
    'dt' : ('set trap in diversion', ),
    'it' : ('set input line trap 1', ),
    'itc' : ('set input line trap 2', ),
    'blm' : ('switch blank line trap', ),
    'lsm' : ('set leading space trap', ),
    'em' : ('set end of input trap (run macro after end of input)', ),

    # 25. Diversions
    'di' : ('begin diversion 1', ),
    'da' : ('begin diversion 2', ),
    'box' : ('begin diversion 3', ),
    'boxa' : ('begin diversion 4', ),
    'output' : ('print string', ),
    'asciify' : ('unformat diversion', ),
    'unformat' : ('unformat spaces and tabs in diversion', ),

    # 26. Environments
    'ev' : ('switch environment', ),
    'evc' : ('copy environment to current', ),

    # 28. Colors
    'color' : ('switch colors', ),
    'defcolor' : ('define color', ),
    'gcolor' : ('set glyph color', ),
    'fcolor' : ('set background color', ),

    # 29. I/O
    'so' : ('include file', ),
    #'pso' : ('include command output', ), # Unsafe
    'mso' : ('include file search in tmac macro dirs', ),
    'trf' : ('transparently print file contents 1', ),
    'cf' : ('transparently print file contents 2', ),
    'nx' : ('force processing the file', ),
    'rd' : ('read from standard output (input?)', ),
    #'pi' : ('pipe output to shell command', ), # Unsafe
    #'sy' : ('execute shell script', ), # Unsafe
    #'open' : ('open file for writing', ), # Unsafe
    #'opena' : ('open file for writing and appending', ), # Unsafe
    'write' : ('write to file', ),
    'writec' : ('write to file without newline', ),
    'writem' : ('write macro to file', ),
    'close' : ('close file', ),

    # 30. Postprocessor
    'device' : ('write control string into output device', ),
    'devicem' : ('write control string into output device uninterpreted', ),

    # 31. Misc
    'nm' : ('switch line number mode', ),
    'nn' : ('disable line numbering', ),
    'mc' : ('print glyph with distance from right margin', ),
    'psbb' : ('read postscript image', ),

    # 33. Debugging
    'lf' : ('set input line number and filename', ),
    'tm' : ('print debug message', ),
    'tm1' : ('print debug message with whitespace at front', ),
    'tmc' : ('print debug message with whitespace and no newline at end', ),
    'ab' : ('print debug message 4 and exit', ),
    'ex' : ('print debug message 5 (exit from roff processing)', ),
    'pev' : ('print current environment to stderr', ),
    'pm' : ('print macro names and sizes stderr', ),
    'pnr' : ('print registers to stderr', ),
    'ptr' : ('print traps to stderr', ),
    'fl' : ('flush output', ),
    'backtrace' : ('print backtrace of input stack', ),
    'warnscale' : ('set warning scale indicator', ),
    'spreadwarn' : ('switch warning about unnecessary spaces', ),
    'warn' : ('change warning levels', ),

    # 34. Implementation differences
    'cp' : ('switch compatability mode', ),
    'do' : ('switch compatability mode for some name', ),


    ## Preprocessor macros (see groff(7))
    'EQ' : ('start eqn preprocessor', ),
    'EN' : ('end eqn preprocessor', ),
    'G1' : ('start grap preprocessor', ),
    'G2' : ('end grap preprocessor', ),
    'GS' : ('start grn preprocessor', ),
    'GE' : ('end grn preprocessor', ),
    'PS' : ('start pic preprocessor', ),
    'PE' : ('end pic preprocessor', ),
    'R1' : ('start refer preprocessor', ),
    'R2' : ('end refer preprocessor', ),
    'TS' : ('start tbl preprocessor', ),
    'TS' : ('end tbl preprocessor', ),
}

# Escapes begin with slash
# Followed by:
#     [xyz] for vairables and escape
#     'xyz' for constants
# 1-character escape, except '[' and '(':
#     \x
# 2-character escape, usually special characters:
#     \(xy
# or
#     \*(xy
# Arguments are enclosed in single quotes
# Backslash (\) at the end - continue line
# Three single-quotes at beginning of line is a comment
# Escape followed by newline:
#     ignore the newline and continue current line
# This program will misbehave during HTML escaping
# if an escape code is < or > 

escapes = {
    # 4. Identifiers
    'A' : ('check if valid identifier', ),

    # 5.3.1 Comments
    '"' : ('start comment until end of line', ),
    '#' : ('start comment until end of line nobreak', ),

    # 6. Registers
    'R' : ('define register', ),
    'n' : ('get register value', ),
    'g' : ('get format stored in register', ),

    # 7. Filling and adjusting
    'p' : ('break and adjust (spread) current line', ),

    # 8. Manipulating hypenation
    '%' : ('insert hypenation char (dash)', ),
    ':' : ('break word but dont pring hypenation char', ),

    # 9. Manipulating spacing
    'x' : ('extra vertical line space', ),

    # 10. Tabs and fields
    't' : ('tab char (ignored)', ),

    # 11. Character translations
    '\\' : ('if escape char is backslash, print it', ),
    'e' : ('print current escape char', ),
    'E' : ('print current escape char but not in copy mode', ),
    '.' : ('dot char', ),

    # 14. Line control
    'c' : ('ignore everything on current line after this nobreak current', ),

    # 17. Fonts and symbols
    'f' : ('set font or font position', ),
    'F' : ('set font family', ),
    '(' : ('insert char with 2 char name', ),
    '[' : ('insert char with name of any lenght 1', ),
    'C' : ('insert char with name of any lenght 2', ),
    'N' : ('insert char specified with its code', ),
    '\'' : ('quote (apostrophe) character', ),
    '`' : ('grave character', ),
    '-' : ('minus sign', ),
    '_' : ('underline', ),
    'H' : ('set height of current font', ),
    'S' : ('slant current font', ),
    '/' : ('increasee width of previous glyph (italic correction)', ),
    ',' : ('increasee width of next glyph (italic correction)', ),
    '&' : ('insert zero-width char (ignored) 1', ),
    ')' : ('insert zero-width char (ignored) 2', ),

    # 18. Sizes
    's' : ('set font size', ),

    # 19. Strings
    '*' : ('get string value', ),

    # 20. Loops
    '{' : ('loop: begin block', ),
    '}' : ('loop: end block', ),

    # 21. Writing macros
    '$' : ('get macro argument by its number (like bash)', ),

    # 22. Page motions
    'v' : ('move up or down in page', ),
    'r' : ('move (reserve) up 1v', ),
    'u' : ('move (reserve) up 0.5v', ),
    'd' : ('move (reserve) down 0.5v', ),
    'h' : ('move left or right', ),
    ' ' : ('unpaddable space char nobreak', ),
    '~' : ('unbreakable stretching space char', ),
    '|' : ('small space (1/6)', ),
    '^' : ('small space (1/12)', ),
    '0' : ('space of size of a number', ),
    'w' : ('get width of string', ),
    'k' : ('store current column position in register', ),
    'o' : ('overstrike chars', ),
    'z' : ('print char with zero width (without spacing)', ),
    'Z' : ('print string and restore previous position', ),

    # 23. Drawing requests
    'l' : ('draw line to left or right from current position', ),
    'L' : ('draw line to top or down from current position', ),
    'D' : ('draw variety of stuff', ),
    'b' : ('bracket building by centering vertically', ),

    # 25. Diversions
    '!' : ('transparent line until end of line', ),
    '?' : ('transparently embed into diversion until next question mark', ),

    # 27. Suppressing output
    'O' : ('switch output', ),

    # 28. Colors
    'm' : ('set font color', ),
    'M' : ('set font background color', ),

    # 29. I/O
    'V' : ('get content of environment variable', ),

    # 30. Postprocessor access
    'X' : ('write control string into output device', ),
    'Y' : ('write control string into output device uninterpreted', ),
}

chars = {
    '-D' : 'Ð',
    'Sd' : 'ð',
    'TP' : 'Þ',
    'Tp' : 'þ',
    'ss' : 'ß',
    'ff' : 'ff',
    'fi' : 'fi',
    'fl' : 'fl',
    'Fi' : 'ffi',
    'Fl' : 'ffl',
    '/L' : 'Ł',
    '/l' : 'ł',
    '/O' : 'Ø',
    '/o' : 'ø',
    'AE' : 'Æ',
    'ae' : 'æ',
    'OE' : 'Œ',
    'oe' : 'œ',
    'IJ' : 'Ĳ',
    'ij' : 'ĳ',
    '.i' : 'ı',
    '.j' : 'ȷ',
    '\'A' : 'Á',
    '\'C' : 'Ć',
    '\'E' : 'É',
    '\'I' : 'Í',
    '\'O' : 'Ó',
    '\'U' : 'Ú',
    '\'Y' : 'Ý',
    '\'a' : 'á',
    '\'c' : 'ć',
    '\'e' : 'é',
    '\'i' : 'í',
    '\'o' : 'ó',
    '\'u' : 'ú',
    '\'y' : 'ý',
    ':A' : 'Ä',
    ':E' : 'Ë',
    ':I' : 'Ï',
    ':O' : 'Ö',
    ':U' : 'Ü',
    ':Y' : 'Ÿ',
    ':a' : 'ä',
    ':e' : 'ë',
    ':i' : 'ï',
    ':o' : 'ö',
    ':u' : 'ü',
    ':y' : 'ÿ',
    '^A' : 'Â',
    '^E' : 'Ê',
    '^I' : 'Î',
    '^O' : 'Ô',
    '^U' : 'Û',
    '^a' : 'â',
    '^e' : 'ê',
    '^i' : 'î',
    '^o' : 'ô',
    '^u' : 'û',
    '`A' : 'À',
    '`E' : 'È',
    '`I' : 'Ì',
    '`O' : 'Ò',
    '`U' : 'Ù',
    '`a' : 'à',
    '`e' : 'è',
    '`i' : 'ì',
    '`o' : 'ò',
    '`u' : 'ù',
    '~A' : 'Ã',
    '~N' : 'Ñ',
    '~O' : 'Õ',
    '~a' : 'ã',
    '~n' : 'ñ',
    '~o' : 'õ',
    'vS' : 'Š',
    'vs' : 'š',
    'vZ' : 'Ž',
    'vz' : 'ž',
    ',C' : 'Ç',
    ',c' : 'ç',
    'oA' : 'Å',
    'oa' : 'å',
    'a"' : '˝',
    'a-' : '¯',
    'a.' : '˙',
    'a^' : '^',
    'aa' : '\'',
    'ga' : '`',
    'ab' : '˘',
    'ac' : '¸',
    'ad' : '¨',
    'ah' : 'ˇ',
    'ao' : '˚',
    'a~' : '~',
    'ho' : '˛',
    'ha' : '^',
    'ti' : '~',
    'Bq' : '„',
    'bq' : '‚',
    'lq' : '“',
    'rq' : '”',
    'oq' : '‘',
    'cq' : '’',
    'aq' : '\'',
    'dq' : '"',
    'Fo' : '«',
    'Fc' : '»',
    'fo' : '‹',
    'fc' : '›',
    'r!' : '¡',
    'r?' : '¿',
    'em' : '—',
    'en' : '–',
    'hy' : '‐',
    'lB' : '[',
    'rB' : ']',
    'lC' : '{',
    'rC' : '}',
    'la' : '⟨',
    'ra' : '⟩',
    'bv' : '⎪',
    'braceex' : '⎪',
    'bracketlefttp' : '⎡',
    'bracketleftbt' : '⎣',
    'bracketleftex' : '⎢',
    'bracketrighttp' : '⎤',
    'bracketrightbt' : '⎦',
    'bracketrightex' : '⎥',
    'lt' : '╭',
    'bracelefttp' : '⎧',
    'lk' : '┥',
    'braceleftmid' : '⎨',
    'lb' : '╰',
    'braceleftbt' : '⎩',
    'braceleftex' : '⎪',
    'rt' : '╮',
    'bracerighttp' : '⎫',
    'rk' : '┝',
    'bracerightmid' : '⎬',
    'rb' : '╯',
    'bracerightbt' : '⎭',
    'bracerightex' : '⎪',
    'parenlefttp' : '⎛',
    'parenleftbt' : '⎝',
    'parenleftex' : '⎜',
    'parenrighttp' : '⎞',
    'parenrightbt' : '⎠',
    'parenrightex' : '⎟',
    '<-' : '←',
    '->' : '→',
    '<>' : '↔',
    'da' : '↓',
    'ua' : '↑',
    'va' : '↕',
    'lA' : '⇐',
    'rA' : '⇒',
    'hA' : '⇔',
    'dA' : '⇓',
    'uA' : '⇑',
    'vA' : '⇕',
    'an' : '⎯',
    'ba' : '|',
    'br' : '│',
    'ul' : '_',
    'rn' : '‾',
    'ru' : '_',
    'bb' : '¦',
    'sl' : '/',
    'rs' : '\\',
    'ci' : '○',
    'bu' : '·',
    'dd' : '‡',
    'dg' : '†',
    'lz' : '◊',
    'sq' : '□',
    'ps' : '¶',
    'sc' : '§',
    'lh' : '☜',
    'rh' : '☞',
    'at' : '@',
    'sh' : '#',
    'CR' : '↵',
    'OK' : '✓',
    'co' : '©',
    'rg' : '®',
    'tm' : '™',
    'bs' : 'ATT Bell Labs logo',
    'Do' : '$',
    'ct' : '¢',
    'eu' : '€',
    'Eu' : '€',
    'Ye' : '¥',
    'Po' : '£',
    'Cs' : '¤',
    'Fn' : 'ƒ',
    'de' : '°',
    '%0' : '‰',
    'fm' : '′',
    'sd' : '″',
    'mc' : 'µ',
    'Of' : 'ª',
    'Om' : 'º',
    'AN' : '∧',
    'OR' : '∨',
    'no' : '¬',
    'tno' : '¬',
    'te' : '∃',
    'fa' : '∀',
    'st' : '∋',
    '3d' : '∴',
    'tf' : '∴',
    'or' : '|',
    '12' : '½',
    '14' : '¼',
    '34' : '¾',
    '18' : '⅛',
    '38' : '⅜',
    '58' : '⅝',
    '78' : '⅞',
    'S1' : '¹',
    'S2' : '²',
    'S3' : '³',
    'pl' : '+',
    'mi' : '−',
    '-+' : '∓',
    '+-' : '±',
    't+-' : '±',
    'pc' : '·',
    'md' : '⋅',
    'mu' : '×',
    'tmu' : '×',
    'c*' : '⊗',
    'c+' : '⊕',
    'di' : '÷',
    'tdi' : '÷',
    'f/' : '⁄',
    '**' : '∗',
    '<=' : '≤',
    '>=' : '≥',
    '<<' : '≪',
    '>>' : '≫',
    'eq' : '=',
    '!=' : '≠',
    '==' : '≡',
    'ne' : '≢',
    '=~' : '≅',
    '|=' : '≃',
    'ap' : '∼',
    '~~' : '≈',
    '~=' : '≈',
    'pt' : '∝',
    'es' : '∅',
    'mo' : '∈',
    'nm' : '∉',
    'sb' : '⊂',
    'nb' : '⊄',
    'sp' : '⊃',
    'nc' : '⊅',
    'ib' : '⊆',
    'ip' : '⊇',
    'ca' : '∩',
    'cu' : '∪',
    '/_' : '∠',
    'pp' : '⊥',
    'is' : '∫',
    'integral' : '∫',
    'sum' : '∑',
    'product' : '∏',
    'coproduct' : '∐',
    'gr' : '∇',
    'sr' : '√',
    'sqrt' : '√',
    'radicalex' : 'square root continuation',
    'sqrtex' : 'square root continuation',
    'lc' : '⌈',
    'rc' : '⌉',
    'lf' : '⌊',
    'rf' : '⌋',
    'if' : '∞',
    'Ah' : 'ℵ',
    'Im' : 'ℑ',
    'Re' : 'ℜ',
    'wp' : '℘',
    'pd' : '∂',
    '-h' : 'ℏ',
    'hbar' : 'ℏ',
    '*A' : 'Α',
    '*B' : 'Β',
    '*G' : 'Γ',
    '*D' : 'Δ',
    '*E' : 'Ε',
    '*Z' : 'Ζ',
    '*Y' : 'Η',
    '*H' : 'Θ',
    '*I' : 'Ι',
    '*K' : 'Κ',
    '*L' : 'Λ',
    '*M' : 'Μ',
    '*N' : 'Ν',
    '*C' : 'Ξ',
    '*O' : 'Ο',
    '*P' : 'Π',
    '*R' : 'Ρ',
    '*S' : 'Σ',
    '*T' : 'Τ',
    '*U' : 'Υ',
    '*F' : 'Φ',
    '*X' : 'Χ',
    '*Q' : 'Ψ',
    '*W' : 'Ω',
    '*a' : 'α',
    '*b' : 'β',
    '*g' : 'γ',
    '*d' : 'δ',
    '*e' : 'ε',
    '*z' : 'ζ',
    '*y' : 'η',
    '*h' : 'θ',
    '*i' : 'ι',
    '*k' : 'κ',
    '*l' : 'λ',
    '*m' : 'μ',
    '*n' : 'ν',
    '*c' : 'ξ',
    '*o' : 'ο',
    '*p' : 'π',
    '*r' : 'ρ',
    'ts' : 'ς',
    '*s' : 'σ',
    '*t' : 'τ',
    '*u' : 'υ',
    '*f' : 'ϕ',
    '*x' : 'χ',
    '*q' : 'ψ',
    '*w' : 'ω',
    '+h' : 'ϑ',
    '+f' : 'φ',
    '+p' : 'ϖ',
    '+e' : 'ϵ',
    'CL' : '♣',
    'SP' : '♠',
    'HE' : '♥',
    'u2661' : '♡',
    'DI' : '♦',
    'u2662' : '♢',
}


st = State()
initialize(st)
html_writer = HtmlWriter(st.file_html)
d = logging.debug


for line in st.file_manpage.read().splitlines():
    d('-' * 79)
    d(line)

    if not line:
        d('Type: empty line')
        Request.empty_line(st)
        continue

    if line[0] == st.control_char_nobreak:
        st.no_break = True
    elif line[0] == st.control_char:
        st.no_break = False
    else:
        d('Type: text line')
        Request.text_line(st, line)
        continue

    if len(line) == 1:
        d('Type: single ctrl char, is ignored')
        continue

    request = line[1:].split()[0]

    if request not in requests:
        d('stub:unknown request:' + request)
        continue

    command_info = requests[request]
    d('Type: %s', command_info[0])

    if len(command_info) >= 2:
        command_info[1](st, line)
    else:
        logging.info('Stub: %s', command_info[0])

Request.finalize(st)

html_writer.write_html_footer()
deinitialize(st)
