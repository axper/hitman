# Standard modules
import logging

# My modules
import log_handlers

log = logging.getLogger('htmlops')
log.addHandler(log_handlers.TO_CONSOLE)
log.addHandler(log_handlers.TO_FILE)
log.setLevel(logging.INFO)

class HtmlTags:
    ''' Single HTML tags formatted for opening or closing. '''
    paragraph = 'p'
    bold = 'b'
    italic = 'i'
    code = 'code'
    pre = 'pre'
    header_level_2 = 'h2'
    header_level_3 = 'h3'

    @staticmethod
    def opening(tag):
        return '<' + tag + '>'

    @staticmethod
    def closing(tag):
        return '</' + tag + '>'


class HtmlRequests:
    ''' Returns strings composed of one or more tags. '''
    @staticmethod
    def open_paragraph():
        result = HtmlTags.opening(HtmlTags.paragraph)
        log.debug(result)
        return result
    @staticmethod
    def close_paragraph():
        result = HtmlTags.closing(HtmlTags.paragraph)
        log.debug(result)
        return result

    @staticmethod
    def open_pre():
        result = HtmlTags.opening(HtmlTags.pre)
        log.debug(result)
        return result
    @staticmethod
    def close_pre():
        result = HtmlTags.closing(HtmlTags.pre)
        log.debug(result)
        return result

    @staticmethod
    def open_code():
        result = HtmlTags.opening(HtmlTags.code)
        log.debug(result)
        return result
    @staticmethod
    def close_code():
        result = HtmlTags.closing(HtmlTags.code)
        log.debug(result)
        return result

    @staticmethod
    def open_italic():
        result = HtmlTags.opening(HtmlTags.italic)
        log.debug(result)
        return result
    @staticmethod
    def close_italic():
        result = HtmlTags.closing(HtmlTags.italic)
        log.debug(result)
        return result

    @staticmethod
    def open_bold():
        result = HtmlTags.opening(HtmlTags.bold)
        log.debug(result)
        return result
    @staticmethod
    def close_bold():
        result = HtmlTags.closing(HtmlTags.bold)
        log.debug(result)
        return result

    @staticmethod
    def open_code_italic():
        result = HtmlRequests.open_code() + HtmlRequests.open_italic()
        log.debug(result)
        return result
    @staticmethod
    def close_italic_code():
        result = HtmlRequests.close_italic() + HtmlRequests.close_code()
        log.debug(result)
        return result

    @staticmethod
    def open_code_bold():
        result = HtmlRequests.open_code() + HtmlRequests.open_bold()
        log.debug(result)
        return result
    @staticmethod
    def close_bold_code():
        result = HtmlRequests.close_bold() + HtmlRequests.close_code()
        log.debug(result)
        return result

    @staticmethod
    def section_title(title):
        result = HtmlTags.opening(HtmlTags.header_level_2) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_2) + \
                 '\n'
        log.debug(result)
        return result

    @staticmethod
    def subsection_title(title):
        result = HtmlTags.opening(HtmlTags.header_level_3) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_3) + \
                 '\n'
        log.debug(result)
        return result

    @staticmethod
    def document_header(name, man_section):
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
    @staticmethod
    def document_footer():
        footer = '</body>\n' \
                 '</html>\n'
        log.debug(footer)
        return footer

