# Standard modules
import html
import logging

# My modules
import tables
import globstat
import log_handlers
import htmlops

log = logging.getLogger('esc')
log.addHandler(log_handlers.TO_CONSOLE)
log.addHandler(log_handlers.TO_FILE)
log.setLevel(logging.DEBUG)

class FontParser:
    normal_fonts = ['R', '1']
    italic_fonts = ['I', '2']
    bold_fonts = ['B', '3']
    bold_italic_fonts = ['4']
    previous_fonts = ['P']

    ret_length = 2

    def ret(result):
        ''' Couples result with ret_length in a tuple and returns it. '''
        return (result, FontParser.ret_length)

    def new_is_normal(new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            globstat.state.inline_font_stack.append(new_font)
            log.debug(globstat.state.inline_font_stack)

        if previous_font in FontParser.normal_fonts:
            return FontParser.ret('')
        elif previous_font in FontParser.bold_fonts:
            return FontParser.ret(htmlops.HtmlRequests.close_bold_code())
        elif previous_font in FontParser.italic_fonts:
            return FontParser.ret(htmlops.HtmlRequests.close_italic_code())
        else:
            log.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = False
            return FontParser.ret('')

    def new_is_bold(new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            globstat.state.inline_font_stack.append(new_font)
            log.debug(globstat.state.inline_font_stack)

        if previous_font in FontParser.bold_fonts:
            return FontParser.ret('')
        elif previous_font in FontParser.normal_fonts:
            return FontParser.ret(htmlops.HtmlRequests.open_code_bold())
        elif previous_font in FontParser.italic_fonts:
            return FontParser.ret(htmlops.HtmlRequests.close_italic() +
                                  htmlops.HtmlRequests.open_bold())
        else:
            log.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = True
            return FontParser.ret('')

    def new_is_italic(new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            globstat.state.inline_font_stack.append(new_font)
            log.debug(globstat.state.inline_font_stack)

        if previous_font in FontParser.italic_fonts:
            return FontParser.ret('')
        elif previous_font in FontParser.bold_fonts:
            return FontParser.ret(htmlops.HtmlRequests.close_bold() +
                                  htmlops.HtmlRequests.open_italic())
        elif previous_font in FontParser.normal_fonts:
            return FontParser.ret(htmlops.HtmlRequests.open_code_italic())
        else:
            log.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = True
            return FontParser.ret('')

    def new_is_previous(new_font, previous_font):
        try:
            globstat.state.inline_font_stack.pop()
            new_font = globstat.state.inline_font_stack[-1]
            log.debug(globstat.state.inline_font_stack)
        except IndexError:
            log.warn('font stack empty 2, taking roman')
            new_font = 'R'

        if new_font in FontParser.normal_fonts:
            return FontParser.new_is_normal(new_font, previous_font, push_to_stack=False)
        elif new_font in FontParser.bold_fonts:
            return FontParser.new_is_bold(new_font, previous_font, push_to_stack=False)
        elif new_font in FontParser.italic_fonts:
            return FontParser.new_is_italic(new_font, previous_font, push_to_stack=False)
        else:
            log.info('new font unknown:%s', new_font)
            return FontParser.ret('')

    def get_result(text):
        ''' Returns a tuple consisting of text and length of escape. '''
        new_font = text[0]

        try:
            previous_font = globstat.state.inline_font_stack[-1]
        except IndexError:
            log.warn('font stack empty, taking roman')
            previous_font = 'R'

        if new_font in FontParser.normal_fonts:
            return FontParser.new_is_normal(new_font, previous_font)
        elif new_font in FontParser.bold_fonts:
            return FontParser.new_is_bold(new_font, previous_font)
        elif new_font in FontParser.italic_fonts:
            return FontParser.new_is_italic(new_font, previous_font)
        elif new_font in FontParser.previous_fonts:
            return FontParser.new_is_previous(new_font, previous_font)
        else:
            log.info('font unknown:%s', new_font)
            return FontParser.ret('')


def replace_2_len_chars(text_line):
    result = ''

    i = 0
    while i < len(text_line):
        if text_line[i] == globstat.state.escape_char:
            try:
                escape_code = text_line[i + 1]
            except IndexError:
                log.info('escape char is last char on line')
                result += text_line[i]
                break

            if escape_code == '(':
                try:
                    table_index = text_line[i + 2 : i + 4]
                except KeyError:
                    log.info('end of line reached when fetching code')
                    i += 3
                    continue

                log.info('table index:%s', table_index)

                try:
                    result += tables.chars[table_index]
                except KeyError:
                    log.info('not found in table:%s', table_index)
                    result += globstat.state.escape_char
                    i += 1
                    continue

                i += 3
            
            else:
                result += globstat.state.escape_char

        else:
            result += text_line[i]

        i += 1

    return result
    
def escape_text(text):
    ''' Escapes groff escape codes.

        1. First handle ampersands(&) after escape
           must be done before HTML escaping
        2. Then escape HTML
        3. Then replace 2 code chars which contain < or >
        4. Finally escape groff codes
    '''
    log_escape_text = logging.getLogger('esc.escape_text')
    log_escape_text.setLevel(logging.DEBUG)

    text = text.replace('\\&', '')
    text = html.escape(text, quote=False)
    text = replace_2_len_chars(text)
    log_escape_text.debug(text)

    globstat.state.inline_font_stack = ['R']

    log_escape_text.debug('inline_code=False')
    globstat.state.inline_code = False

    result = ''
    i = 0
    while i < len(text):
        if text[i] == globstat.state.escape_char:
            try:
                escape_code = text[i + 1]
            except IndexError:
                log_escape_text.debug('continue_line=True')
                globstat.state.continue_line = True
                break

            try:
                escape_info = escapes[escape_code]
            except KeyError:
                log_escape_text.info('stub: unknown escape code: %s', escape_code)
                i += 1
                continue

            log_escape_text.debug('escape code: %s (%s)', escape_code, escape_info[0])

            rest_of_line = text[i + 2:]

            try:
                replacement_and_length = escape_info[1](rest_of_line)
            except IndexError:
                log_escape_text.info('stub: escape code doesnt have handler: %s (%s)', escape_code, escape_info[0])
                i += 1
                continue

            result += replacement_and_length[0]
            i += replacement_and_length[1]

        else:
            result += text[i]

        i += 1

    log_escape_text.debug(result)
    return result


class HandleEscape:
    ''' Returns tuple consisting of replacement string and the length of
        the original escape, not counting the escape character (the backslash).
    '''
    def minus_sign(l):
        return ('-', 1)

    def hypenation_char(l):
        return ('', 1)

    def insert_char_with_2(l):
        two_chars = l[:2]

        try:
            replacement = tables.chars[two_chars]
        except KeyError:
            log.info('index not found in table:%s', two_chars)
            return (globstat.state.escape_char + '(' + two_chars, 3)

        return (replacement, 3)

    def space_char(l):
        return (' ', 1)

    def current_escape_char(l):
        return (globstat.state.escape_char, 1)

    def change_font(l):
        return FontParser.get_result(l)

    def equal_sign(l):
        return ('=', 1)

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
    '%' : ('insert hypenation char (dash)', HandleEscape.hypenation_char),
    ':' : ('break word but dont pring hypenation char', ),

    # 9. Manipulating spacing
    'x' : ('extra vertical line space', ),

    # 10. Tabs and fields
    't' : ('tab char (ignored)', ),

    # 11. Character translations
    '\\' : ('if escape char is backslash, print it', HandleEscape.current_escape_char),
    'e' : ('print current escape char', HandleEscape.current_escape_char),
    'E' : ('print current escape char but not in copy mode', ),
    '.' : ('dot char', ),

    # 14. Line control
    'c' : ('ignore everything on current line after this nobreak current', ),

    # 17. Fonts and symbols
    'f' : ('set font or font position', HandleEscape.change_font),
    'F' : ('set font family', ),
    '(' : ('insert char with 2 char name', HandleEscape.insert_char_with_2),
    '[' : ('insert char with name of any lenght 1', ),
    'C' : ('insert char with name of any lenght 2', ),
    'N' : ('insert char specified with its code', ),
    '\'' : ('quote (apostrophe) character', ),
    '`' : ('grave character', ),
    '-' : ('minus sign', HandleEscape.minus_sign),
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
    ' ' : ('unpaddable space char nobreak', HandleEscape.space_char),
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

    # added from aspell(1):
    '=' : ('equal sign', HandleEscape.equal_sign),
}
