#!/usr/bin/env python3
"""Post-process pandoc's main.docx: add affiliation + emails + fix keywords."""
import re
import shutil
import zipfile
from xml.sax.saxutils import escape

SRC = 'main.docx'
DOC = 'word/document.xml'

AFFIL = ('Universidade Federal de Sergipe, Cidade Universitaria Prof. Jose Aloisio '
         'de Campos, Sao Cristovao, 49100-000, Sergipe, Brazil')
EMAILS = ('Corresponding author: eike.sousa@hotmail.com; '
          'andre@dcomp.ufs.br; marco.sampaio@ufs.br')


def p(text, style=None, italic=False):
    ppr = '<w:pPr>' + (f'<w:pStyle w:val="{style}"/>' if style else '') + '</w:pPr>'
    rpr = '<w:rPr>' + ('<w:i/>' if italic else '') + '</w:rPr>'
    return (f'<w:p>{ppr}<w:r>{rpr}'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
    data = {n: z.read(n) for n in names}

xml = data[DOC].decode('utf-8')

# 1) insert affiliation + emails right after the LAST Author-styled paragraph
author_paras = list(re.finditer(r'<w:p\b(?:(?!</w:p>).)*?pStyle w:val="Author".*?</w:p>',
                                 xml, re.S))
if author_paras:
    last = author_paras[-1]
    insertion = p(AFFIL, style='AuthorAddress', italic=True) + p(EMAILS, italic=True)
    xml = xml[:last.end()] + insertion + xml[last.end():]
    print('inserted affiliation/emails after', len(author_paras), 'authors')
else:
    print('WARNING: no Author paragraphs found')

# 2) fix keywords paragraph: add label, fix " ," spacing
kw_old = 'Machine Learning ,Natural Language Processing ,LLM ,Prompt Engineering ,BIM ,RASE'
kw_new = 'Keywords: Machine Learning, Natural Language Processing, LLM, Prompt Engineering, BIM, RASE'
if kw_old in xml:
    xml = xml.replace(kw_old, kw_new)
    print('fixed keywords line')
else:
    print('keywords line not found verbatim (skipped)')

# 3) turn ZZ.ZZ sentinels into real colored runs: melhor=green, pior=red
#    (\textbf bold is preserved -> threshold values stay bold, as in the PDF)
GREEN, RED = '008C00', 'CC0000'
state = {'c': None}


def inject_color(run, color):
    tag = f'<w:color w:val="{color}"/>'
    if '<w:rPr>' in run:
        return run.replace('<w:rPr>', '<w:rPr>' + tag, 1)
    return re.sub(r'(<w:r\b[^>]*>)', r'\1' + f'<w:rPr>{tag}</w:rPr>', run, count=1)


def color_run(m):
    run = m.group(0)
    tm = re.search(r'(<w:t[^>]*>)(.*?)(</w:t>)', run, re.S)
    if not tm:
        return run
    text = tm.group(2)
    if 'ZZGZZ' in text:
        state['c'] = GREEN
    if 'ZZRZZ' in text:
        state['c'] = RED
    closing = ('ZZgZZ' in text) or ('ZZrZZ' in text)
    clean = (text.replace('ZZGZZ', '').replace('ZZgZZ', '')
                 .replace('ZZRZZ', '').replace('ZZrZZ', ''))
    run = run[:tm.start(2)] + clean + run[tm.end(2):]
    if state['c'] and clean.strip():
        run = inject_color(run, state['c'])
    if closing:
        state['c'] = None
    return run


before = xml.count('ZZ')
xml = re.sub(r'<w:r\b.*?</w:r>', color_run, xml, flags=re.S)
print(f'colored highlights (markers found: {before}); leftover ZZ markers:',
      xml.count('ZZGZZ') + xml.count('ZZgZZ') + xml.count('ZZRZZ') + xml.count('ZZrZZ'))

data[DOC] = xml.encode('utf-8')

with zipfile.ZipFile(SRC, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, data[n])
print('rewrote', SRC)
