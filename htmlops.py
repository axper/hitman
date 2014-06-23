import log

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
        return HtmlTags.opening(HtmlTags.paragraph) + '\n'
    @staticmethod
    def close_paragraph():
        return HtmlTags.closing(HtmlTags.paragraph) + '\n'

    @staticmethod
    def open_code():
        return HtmlTags.opening(HtmlTags.code)
    @staticmethod
    def close_code():
        return HtmlTags.closing(HtmlTags.code)

    @staticmethod
    def open_italic():
        return HtmlTags.opening(HtmlTags.italic)
    @staticmethod
    def close_italic():
        return HtmlTags.closing(HtmlTags.italic)

    @staticmethod
    def open_bold():
        return HtmlTags.opening(HtmlTags.bold)
    @staticmethod
    def close_bold():
        return HtmlTags.closing(HtmlTags.bold)

    @staticmethod
    def open_code_italic():
        return HtmlRequests.open_code() + HtmlRequests.open_italic()
    @staticmethod
    def close_italic_code():
        return HtmlRequests.close_italic() + HtmlRequests.close_code()

    @staticmethod
    def open_code_bold():
        return HtmlRequests.open_code() + HtmlRequests.open_bold()
    @staticmethod
    def close_bold_code():
        return HtmlRequests.close_bold() + HtmlRequests.close_code()

    @staticmethod
    def section_title(title):
        result = HtmlTags.opening(HtmlTags.header_level_2) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_2) + \
                 '\n'
        return result

    @staticmethod
    def subsection_title(title):
        result = HtmlTags.opening(HtmlTags.header_level_3) + \
                 title + \
                 HtmlTags.closing(HtmlTags.header_level_3) + \
                 '\n'
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
        return header.format(name, man_section)
    @staticmethod
    def document_footer():
        footer = '</body>\n' \
                 '</html>\n'
        return footer

