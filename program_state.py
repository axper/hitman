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

