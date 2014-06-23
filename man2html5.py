#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
''' This program converts Manpages to HTML5. '''

import csv
import re
import html
from logger import logger
from logger import logger_escape_text_line
from tables import chars, section_name
from program_state import State
from init_deinit import initialize, deinitialize


NORMAL = 0
BOLD = 1
ITALIC = 2


def split_with_quotes(string):
    ''' Splits string into words and takes quotes into account. '''
    return csv.reader(string.splitlines(), quotechar='"', delimiter=' ',
                      quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

def escape_text_line2(text_line):
    # First handle ampersands(&) after escape
    # It must be done before HTML escaping
    text_line = text_line.replace('\\&', '')

    # Now escape HTML
    text_line = html.escape(text_line, quote=False)

    logger.debug('after:' + text_line)

    state.inline_font_stack = ['R']
    state.inline_code = False

    # Now groff escape codes
    result = ''
    index = 0
    while index < len(text_line):
        if text_line[index] == state.escape_char:
            if index == len(text_line) - 2:
                logger.info('stub: escape char is the last letter')
                index += 1
                continue

            escape_code = text_line[index + 1]

            if escape_code not in escapes:
                logger.info('stub:unknown escape code:' + escape_code)
                index += 1
                continue

            escape_info = escapes[escape_code]

            logger.debug('escape code: %s (%s)', escape_code, escape_info[0])

            if len(escape_info) >= 2:
                rest_of_line = text_line[index + 2:]
                got = escapes[escape_code][1](rest_of_line)
                result += got[0]
                index += got[1]
            else:
                logger.info('stub escape code: %s (%s)', escape_code, escape_info[0])

        else:
            result += text_line[index]

        index += 1

    logger.debug('result:%s', result)

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
        logger_escape_text_line.debug(paragraph[i:i+3])
        if paragraph[i:i+3] == r'\fI':
            logger_escape_text_line.debug('starting italic!!!')

            if not italic:
                italic = True
                paragraph = paragraph[:i] + italic_start + paragraph[i+3:]
                logger_escape_text_line.debug(paragraph)
                i += len(italic_start) - 1
            else:
                logger_escape_text_line.warning('already italic')

        elif paragraph[i:i+3] == r'\fB':
            logger_escape_text_line.debug('starting bold!!!')

            if not bold:
                bold = True
                paragraph = paragraph[:i] + bold_start + paragraph[i+3:]
                logger_escape_text_line.debug(paragraph)
                i += len(bold_start) - 1
            else:
                logger_escape_text_line.warning('already bold')

        elif paragraph[i:i+3] in [r'\fR', r'\fP', r'\f1']:

            if italic:
                italic = False
                logger_escape_text_line.debug('ending italic')
                paragraph = paragraph[:i] + italic_end + paragraph[i+3:]
                logger_escape_text_line.debug(paragraph)
                i += len(italic_end) - 1
            elif bold:
                bold = False
                logger_escape_text_line.debug('ending bold')
                paragraph = paragraph[:i] + bold_end + paragraph[i+3:]
                logger_escape_text_line.debug(paragraph)
                i += len(bold_end) - 1
            else:
                logger_escape_text_line.info('deleting non started font command')
                paragraph = paragraph[:i] + paragraph[i+3:]
                logger_escape_text_line.debug(paragraph)

        i += 1

    if italic:
        logger_escape_text_line.debug('ending italic (at the end)')
        paragraph += italic_end
        logger_escape_text_line.debug(paragraph)
    elif bold:
        logger_escape_text_line.debug('ending bold (at the end)')
        paragraph += bold_end
        logger_escape_text_line.debug(paragraph)

    return paragraph

def alternating(line, first, second):
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
        logger.error("Incorrect first argument: %s", first)

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
        logger.error("Incorrect second argument: %s", second)

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
    logger.debug(final)
    html_writer.write_string(final)


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
            logger.info('stub:unknown section name:' + title[1])
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
    def empty_line():
        if state.par:
            html_writer.end_paragraph()

        state.par = False

    def text_line(line):
        escape_text_line2(line)
        '''
        linenew = ' '.join(split_with_quotes(escape_text_line(line)))
        linenew += '\n'

        if state.par:
            logger.debug('already in paragraph')
            state.file_html.write(linenew)
        else:
            logger.debug('starting paragraph')
            html_writer.start_paragraph()
            state.par = True
            state.file_html.write(linenew)

        logger.debug(linenew)
        '''

    def comment(line):
        pass

    def title(line):
        title = split_with_quotes(line)[1:]
        title[0] = title[0].lower()

        html_writer.write_html_header(title)

        logger.debug(title)

    def section_title(line):
        if state.par:
            html_writer.end_paragraph()
            state.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        state.file_html.write('<h2>' + section_title + '</h2>\n')

        logger.debug(section_title)

    def subsection_title(line):
        if state.par:
            html_writer.end_paragraph()
            state.par = False

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()
        state.file_html.write('<h3>' + section_title + '</h3>\n')

        logger.debug(section_title)

    def new_paragraph(line):
        if state.par:
            html_writer.end_paragraph()
            html_writer.start_paragraph()
        else:
            state.par = True
            html_writer.start_paragraph()

    def hanging_indented_paragraph(line):
        logger.info('stub: hanging or indented paragraph (ignoring...)')

        if not state.par:
            html_writer.start_paragraph()
            state.par = True
        else:
            html_writer.end_paragraph()
            html_writer.start_paragraph()

    def alt_bold_italic(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, BOLD, ITALIC)

    def alt_italic_bold(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, ITALIC, BOLD)

    def alt_bold_normal(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, BOLD, NORMAL)

    def alt_normal_bold(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, NORMAL, BOLD)

    def alt_italic_normal(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, ITALIC, NORMAL)

    def alt_normal_italic(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        alternating(line, NORMAL, ITALIC)

    def font_italic(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        html_writer.start_italic()
        parsed = ' '.join(split_with_quotes(escape_text_line(line))[1:])
        state.file_html.write(parsed)
        html_writer.end_italic()
        state.file_html.write(' ')

    def font_bold(line):
        if not state.par:
            html_writer.start_paragraph()
            state.par = True

        html_writer.start_bold()
        parsed = ' '.join(split_with_quotes(escape_text_line(line))[1:])
        state.file_html.write(parsed)
        html_writer.end_bold()
        state.file_html.write(' ')

    def line_break(line):
        if state.par:
            html_writer.end_paragraph()

        state.par = False

    def finalize():
        if state.par:
            html_writer.end_paragraph()
            state.par = False


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

class FontParser:
    normal_fonts = ['R', '1']
    italic_fonts = ['I', '2']
    bold_fonts = ['B', '3']
    bold_italic_fonts = ['4']
    previous_fonts = ['P']

    ret_length = 2

    def ret(self, result):
        ''' Couples result with ret_length in a tuple and returns it. '''
        return (result, self.ret_length)

    def new_is_normal(self, new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            state.inline_font_stack.append(new_font)
            logger.debug(state.inline_font_stack)

        if previous_font in self.normal_fonts:
            return self.ret('')
        elif previous_font in self.bold_fonts:
            return self.ret(HtmlWriter.bold_end)
        elif previous_font in self.italic_fonts:
            return self.ret(HtmlWriter.italic_end)
        else:
            logger.info('previous font unknown:%s', previous_font)
            state.inline_code = False
            return self.ret('')

    def new_is_bold(self, new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            state.inline_font_stack.append(new_font)
            logger.debug(state.inline_font_stack)

        if previous_font in self.bold_fonts:
            return self.ret('')
        elif previous_font in self.normal_fonts:
            return self.ret(HtmlWriter.bold_start)
        elif previous_font in self.italic_fonts:
            return self.ret('</i><b>')
        else:
            logger.info('previous font unknown:%s', previous_font)
            state.inline_code = True
            return self.ret('')

    def new_is_italic(self, new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            state.inline_font_stack.append(new_font)
            logger.debug(state.inline_font_stack)

        if previous_font in self.italic_fonts:
            return self.ret('')
        elif previous_font in self.bold_fonts:
            return self.ret('</b><i>')
        elif previous_font in self.normal_fonts:
            return self.ret(HtmlWriter.italic_start)
        else:
            logger.info('previous font unknown:%s', previous_font)
            state.inline_code = True
            return self.ret('')

    def new_is_previous(self, new_font, previous_font):
        try:
            state.inline_font_stack.pop()
            new_font = state.inline_font_stack[-1]
            logger.debug(state.inline_font_stack)
        except IndexError:
            logger.warn('font stack empty 2, taking roman')
            new_font = 'R'

        if new_font in self.normal_fonts:
            return self.new_is_normal(new_font, previous_font, push_to_stack=False)
        elif new_font in self.bold_fonts:
            return self.new_is_bold(new_font, previous_font, push_to_stack=False)
        elif new_font in self.italic_fonts:
            return self.new_is_italic(new_font, previous_font, push_to_stack=False)
        else:
            logger.info('new font unknown:%s', new_font)
            return self.ret('')

    def get_result(self, text):
        ''' Returns a tuple consisting of text and length of escape. '''
        new_font = text[0]

        try:
            previous_font = state.inline_font_stack[-1]
        except IndexError:
            logger.warn('font stack empty, taking roman')
            previous_font = 'R'

        if new_font in self.normal_fonts:
            return self.new_is_normal(new_font, previous_font)
        elif new_font in self.bold_fonts:
            return self.new_is_bold(new_font, previous_font)
        elif new_font in self.italic_fonts:
            return self.new_is_italic(new_font, previous_font)
        elif new_font in self.previous_fonts:
            return self.new_is_previous(new_font, previous_font)
        else:
            logger.info('font unknown:%s', new_font)
            return self.ret('')

class Escape:
    def minus_sign(l):
        return ('-', 1)

    def hypenation_char(l):
        return ('', 1)

    def insert_char_with_2(l):
        return (chars[l[:2]], 3)

    def space_char(l):
        return (' ', 1)

    def current_escape_char(l):
        return (state.escape_char, 1)

    def change_font(l):
        fp = FontParser()
        return fp.get_result(l)

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
    '%' : ('insert hypenation char (dash)', Escape.hypenation_char),
    ':' : ('break word but dont pring hypenation char', ),

    # 9. Manipulating spacing
    'x' : ('extra vertical line space', ),

    # 10. Tabs and fields
    't' : ('tab char (ignored)', ),

    # 11. Character translations
    '\\' : ('if escape char is backslash, print it', Escape.current_escape_char),
    'e' : ('print current escape char', Escape.current_escape_char),
    'E' : ('print current escape char but not in copy mode', ),
    '.' : ('dot char', ),

    # 14. Line control
    'c' : ('ignore everything on current line after this nobreak current', ),

    # 17. Fonts and symbols
    'f' : ('set font or font position', Escape.change_font),
    'F' : ('set font family', ),
    '(' : ('insert char with 2 char name', Escape.insert_char_with_2),
    '[' : ('insert char with name of any lenght 1', ),
    'C' : ('insert char with name of any lenght 2', ),
    'N' : ('insert char specified with its code', ),
    '\'' : ('quote (apostrophe) character', ),
    '`' : ('grave character', ),
    '-' : ('minus sign', Escape.minus_sign),
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
    ' ' : ('unpaddable space char nobreak', Escape.space_char),
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


state = initialize()
html_writer = HtmlWriter(state.file_html)

logger.debug('file:===============' + state.file_manpage.name + '=================')

for line in state.file_manpage:
    logger.debug('-' * 79)
    logger.debug(line[:-1])

    if line == '\n':
        logger.debug('Type: completely empty line')
        Request.empty_line()
        continue

    if line[0] == state.control_char_nobreak:
        state.no_break = True
    elif line[0] == state.control_char:
        state.no_break = False
    else:
        logger.debug('Type: text line')
        Request.text_line(line)
        continue

    except_first_char = line[1:].split()
    
    if not except_first_char:
        logger.info('Type: escape char, maybe whitespace after')
        Request.empty_line()
        continue

    request = except_first_char[0]

    if request not in requests:
        logger.debug('stub:unknown request:' + request)
        continue

    command_info = requests[request]
    logger.debug('Type: %s', command_info[0])

    if len(command_info) >= 2:
        command_info[1](line)
    else:
        logger.info('stub: %s', command_info[0])

Request.finalize()

html_writer.write_html_footer()
deinitialize(state)
