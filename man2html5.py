#!/bin/env python3
import mimetypes
import gzip
import csv
import cgi
import argparse


def open_unzip_manpage(filename):
    ''' Opens file in text mode and unzips if necessary '''
    if mimetypes.guess_type(filename)[1] == 'gzip':
        return gzip.open(filename, mode='rt')
    else:
        return open(filename, mode='rt')

def parse_title(string):
    ''' Splits string into 5 parts while taking quotes into account '''
    title_line = string[3:].splitlines()
    return csv.reader(title_line, quotechar='"', delimiter=' ',
            quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

def section_name(section):
    ''' Returns name of manpage section number '''
    if section == '0':
        return 'POSIX headers'
    if section == '1':
        return 'Programs'
    elif section == '2':
        return 'System calls'
    elif section == '3':
        return 'Library calls'
    elif section == '4':
        return 'Special files'
    elif section == '5':
        return 'File formats'
    elif section == '6':
        return 'Games'
    elif section == '7':
        return 'Misc'
    elif section == '8':
        return 'System administration'
    elif section == '9':
        return 'Kernel routines'
    else:
        return 'UNKNOWN SECTION'


parser = argparse.ArgumentParser(description='Converts Linux manpages to HTML5.')
parser.add_argument('file', type=str, help='manpage file to parse')
args = parser.parse_args()


manpage = open_unzip_manpage(args.file)
html = open('result.html', 'wt')


in_par = False
print(in_par)

for line in manpage.read().splitlines():
    print('========================================================')

    # Empty line
    if line == '':
        print('Newline')
    # Comment
    elif line[:3] == r'.\"':
        continue
    # The title line
    elif line[:3] == r'.TH':
        title = parse_title(line)
        title[0] = title[0].lower()

        html.write('<!doctype HTML>\n')
        html.write('<html>\n')
        html.write('<head>\n')
        html.write('<meta charset=\'utf-8\'>\n')
        html.write('<title>' + title[0] + ' - ' + 
                section_name(title[1]) + ' - ' +
                'Man page</title>\n')
        html.write('<link rel=\'stylesheet\' type=\'text/css\' href=\'style.css\'>\n')
        html.write('</head>\n')
        html.write('<body>\n')
        html.write('<div id=\'content\'>\n')
        html.write('<h1>' + title[0] + '</h1>\n')
    # Section
    elif line[:3] == r'.SH':
        if in_par:
            html.write('</p>\n')
            in_par = False

        section_title = line[4:].capitalize()
        html.write('<h2>' + section_title + '</h2>\n')
        print('Sec     :', section_title)
    # Paragraph (sentence)
    elif line[:1] != r'.':
        line = ' ' + cgi.escape(line) + ' '
        if in_par:
            html.write(line)
        else:
            html.write('<p>')
            in_par = True
            html.write(line)

        print('Paragrph:', line)
    # Code
    elif line[:3] in (r'.B ', r'.I', r'.BI', r'.BR',
            r'.IB', r'.IR', r'.RB', r'.RI', r'.SB', r'.SM'):
        line = cgi.escape(line)
        line = line.replace('"', '')
        line = ' <code>' + line[3:].strip() + '</code> '

        if in_par:
            html.write(line)
        else:
            html.write('<p>')
            in_par = True
            html.write(line)

        print('Code    :', line)
    else:
        print('>>>>!!!!!!!!!!UNKNOWN:', line)

html.write('</div>\n')
html.write('</body>\n')
html.write('</html>\n')

manpage.close()
html.close()

