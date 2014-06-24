class State:
    ''' The global state variables. '''
    # Files
    file_manpage = None
    file_html = None

    # Control and escape chars
    control_char = '.'
    control_char_nobreak = '\''
    escape_char = '\\'

    # Global state
    par = False
    ignore_until_doubledot = False
    continue_line = False
    hanging = False
    cat_tag = False
    pre_mode = False

    # Inline state, resets on newline
    inline_font_stack = ['R']
    inline_code = False

    def write(self, text):
        ''' Writes text into HTML file. '''
        self.file_html.write(text)
