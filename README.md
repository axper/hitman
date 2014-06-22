man2html5 - a manpage to HTML5 convertor
==============

Used groff file specifications
-------------
- groff(7)
- groff\_me(7)
- groff\_man(7)
- man(7)
- groff info

List of similar projects
--------------
- man2html: text output with everything in black monospace font
- man2web: same as man2html
- roffit: can't handle more complex pages with groff commands
- man -H: can't properly format gcc(1)

Escapes
--------------
- Escapes begin with slash
- Followed by:
    [xyz] for vairables and escape
    'xyz' for constants
- 1-character escape, except '[' and '(':
    \x
- 2-character escape, usually special characters:
    \(xy
or
    \*(xy
- Arguments are enclosed in single quotes
- Backslash (\\) at the end - continue line
- Three single-quotes at beginning of line is a comment
- Escape followed by newline means ignore the newline and continue current line
- This program will misbehave during HTML escaping if an escape code is < or > 

Requests
--------------
- Just the control char by itself on the line is ignored