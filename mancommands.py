man_commands_start = {
    #'' : ('empty line', ),
    '\\"' : ('comment', ),

    ## Man macro package
    # Usage
    'TH' : ('title line', ),
    'SH' : ('section title', ),
    'SS' : ('subsection title', ),
    'TP' : ('new paragraph hanging 1', ),
    'LP' : ('new paragraph 1', ),
    'PP' : ('new paragraph 2', ),
    'P' : ('new paragraph 3', ),
    'IP' : ('new paragraph hanging 2', ),
    'HP' : ('new paragraph hanging 3', ),
    'RS' : ('start indent', ),
    'RE' : ('end indent', ),

    # Font
    'SM' : ('font small', ),
    'SB' : ('font small alt bold', ),
    'BI' : ('font bold alt italic', ),
    'IB' : ('font italic alt bold', ),
    'RI' : ('font normal alt italic', ),
    'IR' : ('font italic alt normal', ),
    'BR' : ('font bold alt normal', ),
    'RB' : ('font normal alt bold', ),
    'B' : ('font bold', ),
    'I' : ('font italic', ),
    #('R' : ('font normal', ),

    # Misc
    'DT' : ('reset tabs to default', ),
    'PD' : ('set distance between paragraphs', ),
    'AT' : ('set at&t unix version (dont use)', ),
    'UC' : ('set bsd version (dont use)', ),

    # Optional extensions
    'PT' : ('print header string', ),
    'BT' : ('print footer string', ),
    'CT' : ('print ctrl key', ),
    'CW' : ('font monospace', ),
    'Ds' : ('begin nonfilled display', ),
    'De' : ('end nonfilled display', ),
    'G' : ('font helvetica', ),
    'GL' : ('font helvetica oblique', ),
    'HB' : ('font helvetica bold 1', ),
    'TB' : ('font helvetica bold 2', ),
    'MS' : ('manpage reference ultrix', ),
    'PN' : ('set path name 1', ),
    'Pn' : ('set path name 2', ),
    'RN' : ('print <RETURN>', ),
    'VS' : ('start change bar', ),
    'VE' : ('end change bar', ),

    # Other (not described in groff info page)
    # Example
    'EX' : ('start example', ),
    'EE' : ('end example', ),
    # URL
    'URL' : ('url groff', ),
    'UR' : ('start url', ),
    'UE' : ('end url', ),
    # Email
    'MT' : ('start email', ),
    'ME' : ('end email', ),
    # Synopsis
    'SY' : ('start indented synopsis', ),
    'YS' : ('end indented synopsis', ),
    'OP' : ('synopsis optional command', ),
    # Note
    'NT' : ('begin note', ),
    'NE' : ('end note', ),
    # Paragraph indent
    'TQ' : ('new paragraph hanging 4', ),


    ## Requests from gtroff info page
    # Registers
    # \nXXXXX - get register
    'nr' : ('set register', ),
    'rr' : ('remove register', ),
    'rnn' : ('rename register', ),
    'aln' : ('create alias for register', ),
    'af' : ('change register output format', ),

    # Filling and adjusting
    'br' : ('line break', ),
    'fi' : ('enable fill mode', ),
    'nf' : ('disable fill mode', ),
    'ad' : ('set adjusting mode', ),
    'na' : ('disable adjusting', ),
    'brp' : ('adjust current line and break', ),
    'ss' : ('change space size between words', ),
    'ce' : ('center text', ),
    'rj' : ('right justify text', ),

    # Hypenation (-)
    'hy' : ('enable hypenation', ),
    'nh' : ('disable hypenation', ),
    'hlm' : ('set max hypenated lines', ),
    'hw' : ('define hypenation for words', ),
    'hc' : ('change hypenation char', ),
    'hpf' : ('read hypenation patterns from file 1', ),
    'hpfa' : ('read hypenation patterns from file 1', ),
    'hpfcode' : ('read hypenation patterns from file 1', ),
    'hcode' : ('set hypenation code of char', ),
    'hym' : ('set right hypenation margin', ),
    'hys' : ('set hypenation space', ),
    'shc' : ('set soft hypen char', ),
    'hla' : ('set hypenation language', ),

    # Spacing
    'sp' : ('space downwards', ),
    'ls' : ('print blank lines', ),
    'ns' : ('disable line spacing', ),

    # Tabs and fields
    'ta' : ('change tab stop positions', ),
    'tc' : ('do not fill tab with space', ),
    'linetabs' : ('set relative tab distance computing mode', ),
    'lc' : ('declare leader repetition char', ),
    'fc' : ('define delimiting and padding char for fields', ),

    # Character translations
    'cc' : ('set control character (dot and singlequote)', ),
    'c2' : ('set no break character', ),
    'eo' : ('disable character esacaping', ),
    'ec' : ('set escape char', ),
    'ecs' : ('save current escape char', ),
    'ecr' : ('restore saved escape char', ),
    'tr' : ('translate char to glyph 1', ),
    'trin' : ('translate char to glyph 2', ),
    'trnt' : ('translate char to glyph 3', ),

    # Troff and Nroff modes
    'nroff' : ('enable tty output', ),
    'troff' : ('enable non-tty output', ),

    # Line layout
    'po' : ('set horizontal page offset', ),
    'in' : ('set indentation', ),
    'ti' : ('temporary indent', ),
    'll' : ('set line length', ),

    # Page layout
    'pl' : ('set page length', ),
    'tl' : ('print title line 1', ),
    'lt' : ('print title line 2', ),
    'pn' : ('set page number', ),
    'pc' : ('set page number character', ),

    # Page control
    'bp' : ('new page', ),
    'ne' : ('reserver vertical space 1', ),
    'sv' : ('reserver vertical space 2', ),
    'os' : ('reserver vertical space 3', ),

    # Font
    #change
    'ft' : ('set font', ),
    'ftr' : ('alias font', ),
    'fzoom' : ('set font zoom', ),
    #family
    'fam' : ('set font family', ),
    'sty' : ('set style for font position', ),
    #positions
    'fp' : ('mount font to position', ),
    'ft' : ('change font position', ),
    #symbols
    'composite' : ('map glyph name', ),
    'cflags' : ('set char properties', ),
    'char' : ('print string instead of char 1', ),
    'fchar' : ('print string instead of char 2', ),
    'fschar' : ('print string instead of char 3', ),
    'schar' : ('print string instead of char 4', ),
    'rchar' : ('remove char definition 1', ),
    'rfschar' : ('remove char definition 2', ),
    #char class
    'class' : ('define char class', ),
    #special font
    'special' : ('set special font 1', ),
    'fspecial' : ('set special font 2', ),
    #artificial font
    'ul' : ('underline font', ),
    'cu' : ('underline font and space', ),
    'uf' : ('set underline font', ),
    'bd' : ('create bold font by printing twice', ),
    'cs' : ('switch constant glyph space mode', ),
    #ligatures and kerning
    'lg' : ('switch ligature', ),
    'kern' : ('switch kerning', ),
    'tkf' : ('enable track kerning', ),

    # Font size
    'ps' : ('change font size', ),
    'sizes' : ('change allowed font sizes', ),
    'vs' : ('change vertical font size', ),
    'pvs' : ('change post vertical font size', ),

    # String variables
    'ds' : ('define string var 1', ),
    'ds1' : ('define string var 2', ),
    'as' : ('assign string var 1', ),
    'as1' : ('assign string var 2', ),
    'substring' : ('substitue strings', ),
    'length' : ('get string length', ),
    'rn' : ('rename something', ),
    'als' : ('create alias to something', ),
    'chop' : ('remove last character from string', ),

    # Loops
    'if' : ('if condition', ),
    'nop' : ('execute nothing', ),
    'ie' : ('else 1', ),
    'el' : ('else 2', ),
    'while' : ('while loop', ),
    'break' : ('break out of loop', ),
    'continue' : ('continue loop', ),

    # Macros
    'de' : ('define macro 1', ),
    'de1' : ('define macro 2', ),
    'dei' : ('define macro 3', ),
    'dei1' : ('define macro 4', ),
    'am' : ('define append macro 1', ),
    'am1' : ('define append macro 2', ),
    'ami' : ('define append macro 3', ),
    'ami1' : ('define append macro 4', ),
    'return' : ('return from macro', ),

    # Page motions
    'mk' : ('mark page location', ),
    'rt' : ('return marked page location', ),

    # Traps (macro calls)
    'vpt' : ('change vertical position traps', ),
    'wh' : ('set page location trap', ),
    'ch' : ('change trap location', ),
    'dt' : ('set trap in diversion', ),
    'it' : ('set input line trap 1', ),
    'itc' : ('set input line trap 2', ),
    'blm' : ('set blank line trap', ),
    'lsm' : ('set leading space trap', ),
    'em' : ('set end of input trap', ),

    # Diversions
    'di' : ('begin diversion 1', ),
    'da' : ('begin diversion 2', ),
    'box' : ('begin diversion 3', ),
    'boxa' : ('begin diversion 4', ),
    'output' : ('print string', ),
    'asciify' : ('unformat diversion', ),
    'unformat' : ('unformat spaces and tabs in diversion', ),

    # Environments
    'ev' : ('switch environment', ),
    'evc' : ('copy environment to current', ),

    # Colors
    'color' : ('switch colors', ),
    'defcolor' : ('define color', ),
    'gcolor' : ('set glyph color', ),
    'fcolor' : ('set background color', ),

    # Input output
    'so' : ('include file', ),
    'pso' : ('include command output', ),
    'mso' : ('include file search in macro dirs', ),
    'trf' : ('transparently print file contents 1', ),
    'cf' : ('transparently print file contents 2', ),
    'nx' : ('force processing the file', ),
    'rd' : ('read from standard output', ),
    'pi' : ('pipe output to shell commands', ),
    'sy' : ('execute shell script', ),
    'open' : ('open file for writing', ),
    'opena' : ('open file for writing and appending', ),
    'write' : ('write to file', ),
    'writec' : ('write to file without newlines', ),
    'writem' : ('write macro to file', ),
    'close' : ('close file', ),

    # Postprocessor
    'device' : ('embed string into output 1', ),
    'devicem' : ('embed string into output 2', ),

    # Misc
    'nm' : ('print line numbers', ),
    'nn' : ('disable line numbering', ),
    'mc' : ('print glyph with distance from right margin', ),
    'psbb' : ('read postscript image', ),

    # Debugging
    'lf' : ('change line number', ),
    'tm' : ('print debug message 1', ),
    'tm1' : ('print debug message 2', ),
    'tmc' : ('print debug message 3', ),
    'ab' : ('print debug message 4', ),
    'ex' : ('print debug message 5', ),
    'pev' : ('print current environment to stderr', ),
    'pm' : ('print symbol table to stderr', ),
    'pnr' : ('print all numbers to stderr', ),
    'ptr' : ('print traps to stderr', ),
    'fl' : ('flush output', ),
    'bactrace' : ('print backtrace of input stack', ),
    'warnscale' : ('set warning scale indicator', ),
    'spreadwarn' : ('enable warning about unnecessary spaces', ),
    'warn' : ('change warning levels', ),

    # Implementation differences
    'cp' : ('switch compatability mode 1', ),
    'do' : ('switch compatability mode 2', ),
}

man_sub_inline = {
    #('\\*' : ('change font size'),
    #('\\*(HF' : ('section header font'),

    # Copyrights
    '\\*R' : ('®'),
    '\\*(Tm' : ('™'),
    '\\*[R]' : ('®'),
    '\\*[Tm]' : ('™'),
    
    # Quotes
    '\\*(lq' : ('“'),
    '\\*(rq' : ('”'),
    '\\*[lq]' : ('“'),
    '\\*[rq]' : ('”'),
    '\\(lq' : ('“'),
    '\\(rq' : ('”'),

    # Hypenation
    '\\%' : (''),
    '\\:' : (''),

    # Current escape character (ususally backslash)
    '\\\\' : ('\\'),
    '\\e' : ('\\'),
    '\\E' : ('\\'),
    '\\.' : ('.'), # wrong if escape char is not backslash

    # Line control
    '\\\n' : (''), # continue current line
    '\\c' : (''), # continue current line
}

