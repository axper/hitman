# Standard modules
import csv
import logging

# My modules
import log_handlers
import esc
import htmlops
import globstat
import tables

log = logging.getLogger('req')
log.addHandler(log_handlers.TO_CONSOLE)
log.addHandler(log_handlers.TO_FILE)
log.setLevel(logging.DEBUG)

def split_with_quotes(string):
    ''' Splits string into words and takes quotes into account. '''
    return csv.reader(string.splitlines(), quotechar='"', delimiter=' ',
                      quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

NORMAL = 0
BOLD = 1
ITALIC = 2

def alternating(line, style1, style2):
    ''' Alternates text between 2 styles.

        Also changes par state if needed.
    '''
    open_par_if_closed()

    if style1 == BOLD:
        even_start = htmlops.HtmlRequests.open_bold()
        even_end = htmlops.HtmlRequests.close_bold()
    elif style1 == ITALIC:
        even_start = htmlops.HtmlRequests.open_italic()
        even_end = htmlops.HtmlRequests.close_italic()
    elif style1 == NORMAL:
        even_start = ''
        even_end = ''
    else:
        log.error("Incorrect style1 argument: %s", style1)

    if style2 == BOLD:
        odd_start = htmlops.HtmlRequests.open_bold()
        odd_end = htmlops.HtmlRequests.close_bold()
    elif style2 == ITALIC:
        odd_start = htmlops.HtmlRequests.open_italic()
        odd_end = htmlops.HtmlRequests.close_italic()
    elif style2 == NORMAL:
        odd_start = ''
        odd_end = ''
    else:
        log.error("Incorrect style2 argument: %s", style2)

    words = split_with_quotes(esc.escape_text(line))
    words2 = words[1:]

    if words2:
        result = ''
        result += htmlops.HtmlRequests.open_code()

        even = True
        for i in words2:
            if even:
                result += even_start + i + even_end
                even = False
            else:
                result += odd_start + i + odd_end
                even = True

        result += htmlops.HtmlRequests.close_code()
        result += '\n'

        log.debug(result)
        return result

    else:
        log.warning('alternating style has no content')
        return ''

def open_par():
    result_open_par = htmlops.HtmlRequests.open_paragraph()
    log.debug(result_open_par)
    globstat.state.write(result_open_par)

    log.debug('par=True')
    globstat.state.par = True

def close_par():
    result_close_par = htmlops.HtmlRequests.close_paragraph() + '\n'
    log.debug(result_close_par)
    globstat.state.write(result_close_par)

    log.debug('par=False')
    globstat.state.par = False

def open_par_if_closed(line=''):
    if not globstat.state.par:
        open_par()

def close_par_if_open(line=''):
    if globstat.state.par:
        close_par()


def close_data():
    result_close_data = htmlops.HtmlRequests.close_definition_data() + '\n'
    log.debug(result_close_data)
    globstat.state.write(result_close_data)

    log.debug('cat_data=False')
    globstat.state.cat_data = False

def close_data_if_open():
    if globstat.state.cat_data:
        close_data()

def close_deflist():
    result_close_deflist = htmlops.HtmlRequests.close_definition_list() + '\n'
    log.debug(result_close_deflist)
    globstat.state.write(result_close_deflist)

    log.debug('dl_mode=False')
    globstat.state.dl_mode = False

def close_deflist_if_open():
    if globstat.state.dl_mode:
        close_deflist()


class HandleRequest:
    ''' Functions to handle requests.
        
        Requests are the lines which start with dot or single quote.
    '''
    def empty_line():
        close_par_if_open()

    def text_line(line):
        result = esc.escape_text(line)

        if globstat.state.continue_line:
            log.debug(result)
            globstat.state.write(result)

            log.debug('continue_line=False')
            globstat.state.continue_line = False

            return

        result += '\n'

        if not globstat.state.pre_mode and not globstat.state.cat_data:
            open_par_if_closed()

        log.debug(result)
        globstat.state.write(result)

    def comment(line):
        pass

    def title(line):
        title = split_with_quotes(line)[1:]
        title[0] = title[0].lower()

        man_section_number = title[1]

        try:
            section = tables.section_name[man_section_number]
        except KeyError:
            log.warning('Unknown section title: %s', man_section_number)
            section = 'UNKNOWN SECTION'

        result = htmlops.HtmlRequests.document_header(title[0], section)
        log.debug(result)
        globstat.state.write(result)

    def section_title(line):
        close_par_if_open()
        close_data_if_open()
        close_deflist_if_open()

        section_title = ' '.join(split_with_quotes(line)[1:]).capitalize()

        result = htmlops.HtmlRequests.section_title(section_title)
        log.debug(result)
        globstat.state.write(result)

    def subsection_title(line):
        close_par_if_open()

        subsection_title = ' '.join(split_with_quotes(line)[1:]).capitalize()

        result = htmlops.HtmlRequests.subsection_title(subsection_title)
        log.debug(result)
        globstat.state.write(result)

    def new_paragraph(line):
        close_par_if_open()

        result_open_par = htmlops.HtmlRequests.open_paragraph()
        log.debug(result_open_par)
        globstat.state.write(result_open_par)

        log.debug('par=True')
        globstat.state.par = True

    def hanging_indented_paragraph(line):
        log.info('stub: hanging_indented_paragraph')

        close_par_if_open()
        open_par()

    def hanging_tp(line):
        close_par_if_open()

        log.debug('hanging=True')
        globstat.state.hanging = True
        log.debug('cat_tag=True')
        globstat.state.cat_tag = True

    def hanging_ip(line):
        close_par_if_open()

        if globstat.state.cat_data:
            close_data = htmlops.HtmlRequests.close_definition_data() + '\n'
            log.debug(close_data)
            globstat.state.write(close_data)

            log.debug('cat_data=False')
            globstat.state.cat_data = False

        if not globstat.state.dl_mode:
            result_open_dl = htmlops.HtmlRequests.open_definition_list() + '\n'
            log.debug(result_open_dl)
            globstat.state.write(result_open_dl)

            log.debug('dl_mode=True')
            globstat.state.dl_mode = True

        escaped = esc.escape_text(line)
        tag = split_with_quotes(escaped)[1]

        result = htmlops.HtmlRequests.open_definition_name() + \
                 tag + \
                 htmlops.HtmlRequests.close_definition_name() + \
                 '\n'

        log.debug(result)
        globstat.state.write(result)

        if not globstat.state.cat_data:
            open_data = htmlops.HtmlRequests.open_definition_data()
            log.debug(open_data)
            globstat.state.write(open_data)

            log.debug('cat_data=True')
            globstat.state.cat_data = True

    def alt_bold_italic(line):
        result = alternating(line, BOLD, ITALIC)
        log.debug(result)
        globstat.state.write(result)

    def alt_italic_bold(line):
        result = alternating(line, ITALIC, BOLD)
        log.debug(result)
        globstat.state.write(result)

    def alt_bold_normal(line):
        result = alternating(line, BOLD, NORMAL)
        log.debug(result)
        globstat.state.write(result)

    def alt_normal_bold(line):
        result = alternating(line, NORMAL, BOLD)
        log.debug(result)
        globstat.state.write(result)

    def alt_italic_normal(line):
        result = alternating(line, ITALIC, NORMAL)
        log.debug(result)
        globstat.state.write(result)

    def alt_normal_italic(line):
        result = alternating(line, NORMAL, ITALIC)
        log.debug(result)
        globstat.state.write(result)

    def font_italic(line):
        open_par_if_closed()

        line = ' '.join(split_with_quotes(esc.escape_text(line))[1:])

        result = htmlops.HtmlRequests.open_code_italic() + \
                 line + \
                 htmlops.HtmlRequests.close_italic_code()
        log.debug(result)
        globstat.state.write(result)

    def font_bold(line):
        open_par_if_closed()

        line = ' '.join(split_with_quotes(esc.escape_text(line))[1:])

        result = htmlops.HtmlRequests.open_code_bold() + \
                 line + \
                 htmlops.HtmlRequests.close_bold_code()
        log.debug(result)
        globstat.state.write(result)

    def start_indent(line):
        close_par_if_open()

        log.debug('pre_mode=True')
        globstat.state.pre_mode = True

        result = htmlops.HtmlRequests.open_pre() + '\n'
        log.debug(result)
        globstat.state.write(result)

    def end_indent(line):
        log.debug('pre_mode=False')
        globstat.state.pre_mode = False

        result = htmlops.HtmlRequests.close_pre() + '\n'
        log.debug(result)
        globstat.state.write(result)

    def finalize():
        close_par_if_open()


requests = {
    '.' : ('just a single dot', ),
    '\\"' : ('comment', HandleRequest.comment),

    ## Man macro package
    # 2. Usage
    'TH' : ('title line', HandleRequest.title),
    'SH' : ('section title', HandleRequest.section_title),
    'SS' : ('subsection title', HandleRequest.subsection_title),
    'LP' : ('new paragraph 1', HandleRequest.new_paragraph),
    'PP' : ('new paragraph 2', HandleRequest.new_paragraph),
    'P' : ('new paragraph 3', HandleRequest.new_paragraph),
    'TP' : ('new paragraph hanging 1', HandleRequest.hanging_tp),
    'IP' : ('new paragraph hanging 2', HandleRequest.hanging_ip),
    'HP' : ('new paragraph hanging 3', ),
    'RS' : ('start indent', HandleRequest.start_indent),
    'RE' : ('end indent', HandleRequest.end_indent),

    # 3. Font
    'SM' : ('font small', ),
    'SB' : ('font small alt bold', ),
    'BI' : ('font bold alt italic', HandleRequest.alt_bold_italic),
    'IB' : ('font italic alt bold', HandleRequest.alt_italic_bold),
    'RI' : ('font normal alt italic', HandleRequest.alt_normal_italic),
    'IR' : ('font italic alt normal', HandleRequest.alt_italic_normal),
    'BR' : ('font bold alt normal', HandleRequest.alt_bold_normal),
    'RB' : ('font normal alt bold', HandleRequest.alt_normal_bold),
    'B' : ('font bold', HandleRequest.font_bold),
    'I' : ('font italic', HandleRequest.font_italic),
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
    'br' : ('line break', close_par_if_open),
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
    'sp' : ('skip lines up or down', close_par_if_open),
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
    #'pi' : ('pipe output to shell command', ), # Unsafe*a
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

