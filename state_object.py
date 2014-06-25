class State:
    ''' The global state variables.
        
        file_manpage - The manpage file from which text is read.
        file_html - The manpage file to which the result is written to.

        par - Is the program inside paragraph mode? (<pre> tag?)
        pre_mode - Is the program inside pre mode (<pre> tag?)
    '''
    # Files
    file_manpage = None
    file_html = None

    # Control and escape chars
    control_char = '.'
    control_char_nobreak = '\''
    escape_char = '\\'

    # Global state
    par = False
    pre_mode = False
    dl_mode = False
    cat_data = False
    fetch_tag = False

    # Inline state, resets on newline
    inline_font_stack = ['R']
    inline_code = False

    def write(self, text):
        ''' Writes text into HTML file. '''
        self.file_html.write(text)
