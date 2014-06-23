# Standard modules
import html

# My modules
import tables
import globstat
import log
import htmlops

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
            globstat.state.inline_font_stack.append(new_font)
            log.logger.debug(globstat.state.inline_font_stack)

        if previous_font in self.normal_fonts:
            return self.ret('')
        elif previous_font in self.bold_fonts:
            return self.ret(htmlops.HtmlRequests.close_bold_code())
        elif previous_font in self.italic_fonts:
            return self.ret(htmlops.HtmlRequests.close_italic_code())
        else:
            log.logger.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = False
            return self.ret('')

    def new_is_bold(self, new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            globstat.state.inline_font_stack.append(new_font)
            log.logger.debug(globstat.state.inline_font_stack)

        if previous_font in self.bold_fonts:
            return self.ret('')
        elif previous_font in self.normal_fonts:
            return self.ret(htmlops.HtmlRequests.open_code_bold())
        elif previous_font in self.italic_fonts:
            return self.ret('</i><b>')
        else:
            log.logger.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = True
            return self.ret('')

    def new_is_italic(self, new_font, previous_font, push_to_stack=True):
        if push_to_stack:
            globstat.state.inline_font_stack.append(new_font)
            log.logger.debug(globstat.state.inline_font_stack)

        if previous_font in self.italic_fonts:
            return self.ret('')
        elif previous_font in self.bold_fonts:
            return self.ret('</b><i>')
        elif previous_font in self.normal_fonts:
            return self.ret(htmlops.HtmlRequests.open_code_italic())
        else:
            log.logger.info('previous font unknown:%s', previous_font)
            globstat.state.inline_code = True
            return self.ret('')

    def new_is_previous(self, new_font, previous_font):
        try:
            globstat.state.inline_font_stack.pop()
            new_font = globstat.state.inline_font_stack[-1]
            log.logger.debug(globstat.state.inline_font_stack)
        except IndexError:
            log.logger.warn('font stack empty 2, taking roman')
            new_font = 'R'

        if new_font in self.normal_fonts:
            return self.new_is_normal(new_font, previous_font, push_to_stack=False)
        elif new_font in self.bold_fonts:
            return self.new_is_bold(new_font, previous_font, push_to_stack=False)
        elif new_font in self.italic_fonts:
            return self.new_is_italic(new_font, previous_font, push_to_stack=False)
        else:
            log.logger.info('new font unknown:%s', new_font)
            return self.ret('')

    def get_result(self, text):
        ''' Returns a tuple consisting of text and length of escape. '''
        new_font = text[0]

        try:
            previous_font = globstat.state.inline_font_stack[-1]
        except IndexError:
            log.logger.warn('font stack empty, taking roman')
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
            log.logger.info('font unknown:%s', new_font)
            return self.ret('')


def replace_dangerous_chars(text_line, char_table):
    result = ''

    i = 0
    while i < len(text_line):
        if text_line[i] == globstat.state.escape_char:
            try:
                escape_code = text_line[i + 1]
            except IndexError:
                log.logger.info('escape char is last char on line')
                result += text_line[i]
                break

            if escape_code == '(':
                try:
                    result += char_table[text_line[i + 2 : i + 4]]
                except KeyError:
                    pass
            
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
    text = text.replace('\\&', '')

    text = html.escape(text, quote=False)
    log.logger.debug('&HT:>>>%s<<<', text)

    text = replace_dangerous_chars(text, tables.chars_html_dangerous)
    log.logger.debug('2CC:>>>%s<<<', text)

    globstat.state.inline_font_stack = ['R']
    globstat.state.inline_code = False

    result = ''
    i = 0
    while i < len(text):
        if text[i] == globstat.state.escape_char:
            try:
                escape_code = text[i + 1]
            except IndexError:
                log.logger.info('stub:escape char is last char on line')
                globstat.state.continue_line = True
                break

            if escape_code not in escapes:
                log.logger.info('stub:unknown escape code:' + escape_code)
                i += 1
                continue

            escape_info = escapes[escape_code]

            log.logger.debug('escape code: %s (%s)', escape_code, escape_info[0])

            if len(escape_info) >= 2:
                rest_of_line = text[i + 2:]
                got = escapes[escape_code][1](rest_of_line)
                result += got[0]
                i += got[1]
            else:
                log.logger.info('stub escape code: %s (%s)', escape_code, escape_info[0])

        else:
            result += text[i]

        i += 1

    return result


class GetEscapeTuple:
    ''' Returns tuple consisting of replacement string and the length of
        the original escape, not counting the escape character (the backslash).
    '''
    def minus_sign(l):
        return ('-', 1)

    def hypenation_char(l):
        return ('', 1)

    def insert_char_with_2(l):
        return (chars[l[:2]], 3)

    def space_char(l):
        return (' ', 1)

    def current_escape_char(l):
        return (globstat.state.escape_char, 1)

    def change_font(l):
        font_parser = FontParser()
        return font_parser.get_result(l)

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
    '%' : ('insert hypenation char (dash)', GetEscapeTuple.hypenation_char),
    ':' : ('break word but dont pring hypenation char', ),

    # 9. Manipulating spacing
    'x' : ('extra vertical line space', ),

    # 10. Tabs and fields
    't' : ('tab char (ignored)', ),

    # 11. Character translations
    '\\' : ('if escape char is backslash, print it', GetEscapeTuple.current_escape_char),
    'e' : ('print current escape char', GetEscapeTuple.current_escape_char),
    'E' : ('print current escape char but not in copy mode', ),
    '.' : ('dot char', ),

    # 14. Line control
    'c' : ('ignore everything on current line after this nobreak current', ),

    # 17. Fonts and symbols
    'f' : ('set font or font position', GetEscapeTuple.change_font),
    'F' : ('set font family', ),
    '(' : ('insert char with 2 char name', GetEscapeTuple.insert_char_with_2),
    '[' : ('insert char with name of any lenght 1', ),
    'C' : ('insert char with name of any lenght 2', ),
    'N' : ('insert char specified with its code', ),
    '\'' : ('quote (apostrophe) character', ),
    '`' : ('grave character', ),
    '-' : ('minus sign', GetEscapeTuple.minus_sign),
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
    ' ' : ('unpaddable space char nobreak', GetEscapeTuple.space_char),
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
    '=' : ('equal sign', GetEscapeTuple.equal_sign),
}
