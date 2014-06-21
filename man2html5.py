#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
''' This program converts Manpages to HTML5. '''

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



NORMAL = 0
BOLD = 1
ITALIC = 2


def open_man_file(filename):
    ''' Opens file in text mode and unzips if necessary. '''
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
    title_line = string.splitlines()
    return csv.reader(title_line, quotechar='"', delimiter=' ',
                      quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

def sub_inline_font(par):
    ''' Parses man inline font escapes and replaces with HTML. '''

    bold_start = '<code><b>'
    bold_end = '</b></code>'

    italic_start = '<code><i>'
    italic_end = '</i></code>'

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
        linenew = escape_paragraph(line)
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
        parsed = ' '.join(split_with_quotes(escape_paragraph(line))[1:])
        st.file_html.write(parsed)
        html_writer.end_italic()
        st.file_html.write(' ')

    def font_bold(st, line):
        if not st.par:
            html_writer.start_paragraph()
            st.par = True

        html_writer.start_bold()
        parsed = ' '.join(split_with_quotes(escape_paragraph(line))[1:])
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

requests = {
    #'' : ('empty line', ),
    '.' : ('just a single dot', ),
    '\\"' : ('comment', Request.comment),

    ## Man macro package
    # Usage
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

    # Font
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

    # Misc
    'DT' : ('reset tabs to default', ),
    'PD' : ('set distance between paragraphs', ),
    'AT' : ('set at&t unix version (dont use)', ),
    'UC' : ('set bsd version (dont use)', ),

    # Optional extensions
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

    # Other (not described in groff info page)
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
    # Comments
    'ig' : ('ignore until .. or macro encounters', ),

    # Registers
    'nr' : ('define register', ),
    'rr' : ('remove register', ),
    'rnn' : ('rename register', ),
    'aln' : ('create alias name for register', ),
    'af' : ('set register output format', ),

    # Filling and adjusting
    'br' : ('line break', Request.line_break),
    'fi' : ('enable output fill mode', ),
    'nf' : ('disable output fill mode', ),
    'ad' : ('set line adjusting mode', ),
    'na' : ('disable output line adjusting', ),
    'brp' : ('break and adjust (spread) current line', ),
    'ss' : ('change space size between words', ),
    'ce' : ('center next line', ),
    'rj' : ('right justify text', ),

    # Hypenation (-)
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

    # Spacing
    'sp' : ('skip lines up or down', Request.line_break),
    'ls' : ('print blank lines after each output', ),
    'ns' : ('disable line spacing mode', ),
    'rs' : ('enable line spacing mode', ),

    # Tabs and fields
    'ta' : ('set tab stop positions', ),
    'tc' : ('set tab fill char (space)', ),
    'linetabs' : ('switch relative tab distance computing mode', ),
    'lc' : ('switch leader repetition char', ),
    'fc' : ('define delimiting and padding char for fields', ),

    # Character translations
    'cc' : ('set control character (dot)', ),
    'c2' : ('set no break control character (singlequote)', ),
    'eo' : ('disable character esacaping', ),
    'ec' : ('set escape char (backslash)', ),
    'ecs' : ('save current escape char (backslash)', ),
    'ecr' : ('restore saved escape char (backslash)', ),
    'tr' : ('translate char to glyph 1', ),
    'trin' : ('translate char to glyph 2', ),
    'trnt' : ('translate char to glyph 3', ),

    # Troff and Nroff modes
    'nroff' : ('enable condition n and disable condition t', ),
    'troff' : ('enable condition t and disable condition n', ),

    # Line layout
    'po' : ('set horizontal page offset', ),
    'in' : ('set indentation', ),
    'ti' : ('temporary indent next line', ),
    'll' : ('set line length', ),

    # Page layout
    'pl' : ('set page length', ),
    'tl' : ('print title line', ),
    'lt' : ('set length of title', ),
    'pn' : ('set page number', ),
    'pc' : ('set page number character', ),

    # Page control
    'bp' : ('new page', ),
    'ne' : ('reserve vertical space 1', ),
    'sv' : ('reserve vertical space 2', ),
    'os' : ('reserve vertical space 3', ),

    # Font
    #change
    'ft' : ('set font', ),
    'ftr' : ('alias font', ),
    'fzoom' : ('set font zoom', ),
    #family
    'fam' : ('set font family', ),
    'sty' : ('set style for font position', ),
    #positions
    'fp' : ('mount font to position', ),
    #'ft' : ('change font position', ), # only when argument is a number
    #symbols
    'composite' : ('map glyph name', ),
    'cflags' : ('set char properties', ),
    'char' : ('print string instead of char 1', ),
    'fchar' : ('print string instead of char 2', ),
    'fschar' : ('print string instead of char 3', ),
    'schar' : ('print string instead of char 4', ),
    'rchar' : ('remove char definition', ),
    'rfschar' : ('remove char definition for font', ),
    #char class
    'class' : ('define class of characters', ),
    #special font
    'special' : ('set special font 1', ),
    'fspecial' : ('set special font 2', ),
    #artificial font
    'ul' : ('underline next n input lines', ),
    'cu' : ('underline font and space', ),
    'uf' : ('set underline font', ),
    'bd' : ('create bold font by printing twice', ),
    'cs' : ('set constant glyph width mode for font', ),
    #ligatures and kerning
    'lg' : ('switch ligature mode', ),
    'kern' : ('switch kerning', ),
    'tkf' : ('enable track kerning for font', ),

    # Font size
    'ps' : ('set font size', ),
    'sizes' : ('change allowed font sizes', ),
    'vs' : ('change vertical font size', ),
    'pvs' : ('change post vertical line spacing', ),

    # String variables
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

    # Loops
    'if' : ('if condition', ),
    'nop' : ('execute nothing', ),
    'ie' : ('else if', ),
    'el' : ('else', ),
    'while' : ('while loop', ),
    'break' : ('break out of loop', ),
    'continue' : ('continue loop', ),

    # Macros
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

    # Page motions
    'mk' : ('put current line number into register', ),
    'rt' : ('return to marked line number', ),

    # Traps (macro calls)
    'vpt' : ('switch vertical position traps', ),
    'wh' : ('set line number trap', ),
    'ch' : ('change trap location', ),
    'dt' : ('set trap in diversion', ),
    'it' : ('set input line trap 1', ),
    'itc' : ('set input line trap 2', ),
    'blm' : ('switch blank line trap', ),
    'lsm' : ('set leading space trap', ),
    'em' : ('set end of input trap (run macro after end of input)', ),

    # Diversions
    'di' : ('begin diversion 1', ),
    'da' : ('begin diversion 2', ),
    'box' : ('begin diversion 3', ),
    'boxa' : ('begin diversion 4', ),
    'output' : ('print string', ),
    'asciify' : ('unformat diversion', ),
    'unformat' : ('unformat spaces and tabs in diversion', ),

    # Environments
    'ev' : ('switch environment', ),
    'evc' : ('copy environment to current', ),

    # Colors
    'color' : ('switch colors', ),
    'defcolor' : ('define color', ),
    'gcolor' : ('set glyph color', ),
    'fcolor' : ('set background color', ),

    # Input output
    'so' : ('include file', ),
    'pso' : ('include command output', ),
    'mso' : ('include file search in tmac macro dirs', ),
    'trf' : ('transparently print file contents 1', ),
    'cf' : ('transparently print file contents 2', ),
    'nx' : ('force processing the file', ),
    'rd' : ('read from standard output (input?)', ),
    'pi' : ('pipe output to shell command', ),
    'sy' : ('execute shell script', ),
    'open' : ('open file for writing', ),
    'opena' : ('open file for writing and appending', ),
    'write' : ('write to file', ),
    'writec' : ('write to file without newline', ),
    'writem' : ('write macro to file', ),
    'close' : ('close file', ),

    # Postprocessor
    'device' : ('write control string into output device', ),
    'devicem' : ('write control string into output device uninterpreted', ),

    # Misc
    'nm' : ('switch line number mode', ),
    'nn' : ('disable line numbering', ),
    'mc' : ('print glyph with distance from right margin', ),
    'psbb' : ('read postscript image', ),

    # Debugging
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

    # Implementation differences
    'cp' : ('switch compatability mode', ),
    'do' : ('switch compatability mode for some name', ),
}

# \* - retrive string var
# \n - retrive number var
# \f - set font
# \*(HF - section header font
# \* - interpolate string (change font size???)

# \(XX - escape sequence name of exactly 2 characters
# \[X] - long escape sequence name

# dq - "
# cq - '
# rs - \
#   - <space 1>
# | - <space 2>
# ^ - <space 3>
# h - <space 4>

# backslash (\) at the end - continue line

escape_sequences = {
    # Copyrights
    '\\*R' : ('®'),
    '\\*(Tm' : ('™'),
    '\\*[R]' : ('®'),
    '\\*[Tm]' : ('™'),

    # Quotes
    '\\*(lq' : ('“'),
    '\\*(rq' : ('”'),
    '\\*[lq]' : ('“'),
    '\\*[rq]' : ('”'),
    '\\(lq' : ('“'),
    '\\(rq' : ('”'),

    # Hypenation
    '\\%' : (''),
    '\\:' : (''),

    # Current escape character (ususally backslash)
    '\\\\' : ('\\'),
    '\\e' : ('\\'), # Current escape character
    '\\E' : ('\\'),
    '\\.' : ('.'), # wrong if escape char is not backslash

    # Line control
    '\\\n' : (''), # continue current line
    '\\c' : (''), # continue current line
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

    command_info = requests[request]
    d('Type: %s', command_info[0])

    if len(command_info) >= 2:
        command_info[1](st, line)
    else:
        logging.info('Stub: %s', command_info[0])

Request.finalize(st)

html_writer.write_html_footer()
deinitialize(st)
