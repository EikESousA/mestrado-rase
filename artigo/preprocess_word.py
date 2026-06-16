#!/usr/bin/env python3
"""Make a pandoc-friendly copy of main.tex so all tables convert to real Word
tables. Flattens \\multicolumn, drops \\cline/\\hspace, and removes color macros."""
import re

src = open('main.tex', encoding='utf-8').read()

# 1) color highlight macros -> ASCII sentinels (pandoc drops \textcolor in docx,
#    so fix_docx.py turns these markers into real green/red runs afterwards).
#    \textbf is left untouched -> threshold values stay bold, exactly as the PDF.
src = src.replace(r'\newcommand{\melhor}[1]{\textcolor{green!55!black}{#1}}',
                  r'\newcommand{\melhor}[1]{ZZGZZ#1ZZgZZ}')
src = src.replace(r'\newcommand{\pior}[1]{\textcolor{red!80!black}{#1}}',
                  r'\newcommand{\pior}[1]{ZZRZZ#1ZZrZZ}')


def find_balanced(s, i):
    """Given s[i] == '{', return index just past the matching '}'."""
    depth = 0
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def flatten_multicolumn(s):
    """Replace \\multicolumn{n}{align}{content} with content + (n-1) empty cells."""
    out, i = [], 0
    tok = r'\multicolumn'
    while True:
        j = s.find(tok, i)
        if j == -1:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k = j + len(tok)
        # arg1 {n}
        a1 = find_balanced(s, k)
        n = int(s[k + 1:a1 - 1])
        # arg2 {align}
        a2 = find_balanced(s, a1)
        # arg3 {content}
        a3 = find_balanced(s, a2)
        content = s[a2 + 1:a3 - 1]
        out.append(content + ' &' * (n - 1))
        i = a3
    return ''.join(out)


src = flatten_multicolumn(src)
src = re.sub(r'\\cline\{[^}]*\}', '', src)   # drop \cline rules
src = re.sub(r'\\hspace\{[^}]*\}', '', src)  # drop \hspace indents

open('main_word.tex', 'w', encoding='utf-8').write(src)
print('wrote main_word.tex; multicolumn left:', src.count(r'\multicolumn'),
      '| cline left:', src.count(r'\cline'))
