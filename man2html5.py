#!/bin/env python3
from mimetypes import guess_type
import csv


filename = './brctl.8.gz'

if guess_type(filename)[1] == 'gzip':
    from gzip import open
    manpage = open(filename, mode='rt')
else:
    manpage = open(filename, mode='rt')


for line in manpage.read().splitlines():
    print(line)
    
    if line[:3] == r'.\"':
        print('>>>>comment')
    elif line[:3] == r'.TH':
        title_line = line[3:].splitlines()
        title = csv.reader(title_line, quotechar='"', delimiter=' ', quoting=csv.QUOTE_ALL, skipinitialspace=True).__next__()

        title_name = title[0]
        title_section = title[1]
        title_date = title[2]
        title_source = title[3]
        title_manual = title[4]

        print('>>', title_name, title_section, title_date, title_source, title_manual, sep='|')
    elif line[:3] == r'.SH':
        print('>>>>section title')


manpage.close()
