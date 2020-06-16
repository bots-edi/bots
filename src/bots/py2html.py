# -*- coding: utf-8 -*-

## {{{ http://code.activestate.com/recipes/578178/ (r20)
'''Add syntax highlighting to Python source code'''
__author__ = 'Raymond Hettinger'

# Mike Griffin 3/05/2013
# This is a cut-down version for Bots, only creates html <pre> </pre> block
# css is required in django html template for colours!

# Mike Griffin 10/05/2013 added line numbering
# It doesn't work quite right for triple quoted strings across multiple lines.
# The whole string is one token so the line numbers on those lines get the string
# highlight colour. No simple way to fix this, but it's not really an issue.
import sys
if sys.version_info[0] > 2:
    import builtins
else:
    import builtins as builtins
import keyword
import tokenize
import cgi
import functools

#### Analyze Python Source #################################


def is_builtin(s):
    'Return True if s is the name of a builtin'
    return hasattr(builtins, s)


def combine_range(lines, start, end):
    'Join content from a range of lines between start and end'
    (srow, scol), (erow, ecol) = start, end
    if srow == erow:
        return lines[srow - 1][scol:ecol], end
    rows = [lines[srow - 1][scol:]] + lines[srow: erow - 1] + [lines[erow - 1][:ecol]]
    return ''.join(rows), end


def analyze_python(source):
    '''Generate and classify chunks of Python for syntax highlighting.
       Yields tuples in the form: (category, categorized_text).
    '''
    lines = source.splitlines(True)
    lines.append('')
    for i in range(0, len(lines) - 1):
        lines[i] = '%04d  %s' % (i + 1, lines[i])  # add line numbers
    readline = functools.partial(next, iter(lines), '')
    kind = tok_str = ''
    tok_type = tokenize.COMMENT
    written = (1, 0)
    for tok in tokenize.generate_tokens(readline):
        prev_tok_type, prev_tok_str = tok_type, tok_str
        tok_type, tok_str, (srow, scol), (erow, ecol), logical_lineno = tok
        kind = ''
        if ecol < 5:
            kind = 'linenum'
        elif tok_type == tokenize.COMMENT:
            kind = 'comment'
        elif tok_type == tokenize.OP and tok_str[:1] not in '{}[](),.:;@':
            kind = 'operator'
        elif tok_type == tokenize.STRING:
            kind = 'string'
            if prev_tok_type == tokenize.INDENT or scol == 0:
                kind = 'docstring'
        elif tok_type == tokenize.NAME:
            if tok_str in ('def', 'class', 'import', 'from'):
                kind = 'definition'
            elif prev_tok_str in ('def', 'class'):
                kind = 'defname'
            elif keyword.iskeyword(tok_str):
                kind = 'keyword'
            elif is_builtin(tok_str) and prev_tok_str != '.':
                kind = 'builtin'
        if kind:
            if written != (srow, scol):
                text, written = combine_range(lines, written, (srow, scol))
                yield '', text
            text, written = tok_str, (erow, ecol)
            yield kind, text
    line_upto_token, written = combine_range(lines, written, (erow, ecol))
    yield '', line_upto_token

#### HTML Output ###########################################


def html_highlight(classified_text):
    'Convert classified text to an HTML fragment'
    result = []
    for kind, text in classified_text:
        if kind:
            result.append('<span class="%s">' % kind)
        result.append(cgi.escape(text))
        if kind:
            result.append('</span>')
    return ''.join(result)
