''' htmlops.py - HTML operations.

    This only functions called from outside are in the HtmlRequests class.
    They return 
'''
# Standard modules
import logging

# My modules
import log_handlers

log = logging.getLogger('htmlops')
log.addHandler(log_handlers.TO_CONSOLE)
log.addHandler(log_handlers.TO_FILE)
log.setLevel(logging.INFO)

class HtmlTags:
    ''' Single HTML tags formatted for opening or closing.
    
        Data is accessed from HtmlRequests using the functions
        opening() or closing().
    '''
    paragraph = 'p'
    bold = 'b'
    italic = 'i'
    code = 'code'
    pre = 'pre'
    header_level_2 = 'h2'
    header_level_3 = 'h3'
    definition_list = 'dl'
    definition_name = 'dt'
    definition_data = 'dd'

    def opening(tag):
        ''' Returns a single opening tag. '''
        return '<' + tag + '>'

    def closing(tag):
        ''' Returns a single closing tag. '''
        return '</' + tag + '>'


class HtmlRequests:
    ''' Returns strings composed of a pair of opening and closing tags.
    
        Exceptions include the document header and footer which are
        rather complex.
    '''

    def open_italic():
        ''' Returns '<i>' '''
        result = HtmlTags.opening(HtmlTags.italic)
        log.debug(result)
        return result
    def close_italic():
        ''' Returns '</i>' '''
        result = HtmlTags.closing(HtmlTags.italic)
        log.debug(result)
        return result

    def open_bold():
        ''' Returns '<b>' '''
        result = HtmlTags.opening(HtmlTags.bold)
        log.debug(result)
        return result
    def close_bold():
        ''' Returns '</b>' '''
        result = HtmlTags.closing(HtmlTags.bold)
        log.debug(result)
        return result

    def open_code_italic():
        ''' Returns '<code><i>' '''
        result = HtmlRequests.open_code() + HtmlRequests.open_italic()
        log.debug(result)
        return result
    def close_italic_code():
        ''' Returns '</i></code>' '''
        result = HtmlRequests.close_italic() + HtmlRequests.close_code()
        log.debug(result)
        return result

    def open_code_bold():
        ''' Returns '<code><b>' '''
        result = HtmlRequests.open_code() + HtmlRequests.open_bold()
        log.debug(result)
        return result
    def close_bold_code():
        ''' Returns '</b></code>' '''
        result = HtmlRequests.close_bold() + HtmlRequests.close_code()
        log.debug(result)
        return result

    def open_paragraph():
        ''' Returns '<p>' '''
        result = HtmlTags.opening(HtmlTags.paragraph)
        log.debug(result)
        return result
    def close_paragraph():
        ''' Returns '</p>' '''
        result = HtmlTags.closing(HtmlTags.paragraph)
        log.debug(result)
        return result

    def open_pre():
        ''' Returns '<pre>' '''
        result = HtmlTags.opening(HtmlTags.pre)
        log.debug(result)
        return result
    def close_pre():
        ''' Returns '</pre>' '''
        result = HtmlTags.closing(HtmlTags.pre)
        log.debug(result)
        return result

    def open_code():
        ''' Returns '<code>' '''
        result = HtmlTags.opening(HtmlTags.code)
        log.debug(result)
        return result
    def close_code():
        ''' Returns '</code>' '''
        result = HtmlTags.closing(HtmlTags.code)
        log.debug(result)
        return result

    def section_title(title):
        ''' Returns '<h2>TITLE</h2>' '''
        result = HtmlTags.opening(HtmlTags.header_level_2) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_2)
        log.debug(result)
        return result

    def subsection_title(title):
        ''' Returns '<h3>TITLE</h3>' '''
        result = HtmlTags.opening(HtmlTags.header_level_3) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_3)
        log.debug(result)
        return result

    def open_definition_list():
        ''' Returns '<dl>' '''
        result = HtmlTags.opening(HtmlTags.definition_list)
        log.debug(result)
        return result
    def close_definition_list():
        ''' Returns '</dl>' '''
        result = HtmlTags.closing(HtmlTags.definition_list)
        log.debug(result)
        return result

    def open_definition_name():
        ''' Returns '<dt>' '''
        result = HtmlTags.opening(HtmlTags.definition_name)
        log.debug(result)
        return result
    def close_definition_name():
        ''' Returns '</dt>' '''
        result = HtmlTags.closing(HtmlTags.definition_name)
        log.debug(result)
        return result

    def open_definition_data():
        ''' Returns '<dd>' '''
        result = HtmlTags.opening(HtmlTags.definition_data)
        log.debug(result)
        return result
    def close_definition_data():
        ''' Returns '</dd>' '''
        result = HtmlTags.closing(HtmlTags.definition_data)
        log.debug(result)
        return result

    def document_header(name, man_section):
        ''' Returns the HTML header, which includes:
            
            1. The doctype declaration
            2. Stuff in <head> tag, including:
                a. Charset declaration
                b. Title, composed of manpage name and it's section name
                c. CSS stylesheet name
            3. The document title at the top enclosed in level 1 header tags
        '''
        header = '<!doctype HTML>\n' \
                 '<html>\n' \
                 '<head>\n' \
                 '<meta charset=\'utf-8\'>\n' \
                 '<title>{0} - {1} - Man page</title>\n' \
                 '<link rel=\'stylesheet\' type=\'text/css\' href=\'style.css\'>\n' \
                 '</head>\n' \
                 '<body>\n' \
                 '<h1>{0}</h1>\n'
        result = header.format(name, man_section)
        log.debug(result)
        return result
    def document_footer():
        ''' Returns the HTML footer, which closes what has been left open by
            document_header(): the closing 'body' and 'html' tags
        '''
        footer = '</body>\n' \
                 '</html>\n'
        log.debug(footer)
        return footer

