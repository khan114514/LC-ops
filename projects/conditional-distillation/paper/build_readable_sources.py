"""Regenerate the draft's inline bibliography and readable/ICML variants.
Uses only the bundled, source-fetched metadata. Does not run experiments.
"""
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'paper'

def field(entry, name):
    m = re.search(r'\b' + re.escape(name) + r'\s*=\s*\{', entry, re.I)
    if not m:
        return ''
    start, depth, i = m.end(), 1, m.end()
    while depth and i < len(entry):
        if entry[i] == '{': depth += 1
        elif entry[i] == '}': depth -= 1
        i += 1
    if depth:
        raise ValueError(f'Unclosed field: {name}')
    return entry[start:i-1].strip()

def validate_entries(text):
    entries = re.split(r'\n\s*(?=@\w+\{)', text.strip())
    keys = set()
    for entry in entries:
        match = re.match(r'@\w+\{([^,]+),', entry)
        if not match:
            raise ValueError('Missing BibTeX entry header')
        key = match.group(1)
        if key in keys:
            raise ValueError(f'Duplicate citation key: {key}')
        keys.add(key)
        depth = 0
        outer_end = None
        for i, char in enumerate(entry):
            if char == '{' and (i == 0 or entry[i-1] != '\\'): depth += 1
            elif char == '}' and (i == 0 or entry[i-1] != '\\'):
                depth -= 1
                if depth == 0:
                    outer_end = i
                    break
        if depth != 0 or outer_end is None or entry[outer_end+1:].strip():
            raise ValueError(f'Unbalanced or trailing BibTeX content: {key}')
        for name in ('author', 'title', 'year'):
            if not field(entry, name):
                raise ValueError(f'Missing required {name}: {key}')
        if not re.fullmatch(r'\d{4}', field(entry, 'year')):
            raise ValueError(f'Invalid year: {key}')
        if not (field(entry, 'booktitle') or field(entry, 'eprint') or field(entry, 'journal')):
            raise ValueError(f'Missing publication or eprint source: {key}')
    return entries

bib = (ROOT/'literature/verified_references.bib').read_text()
# Prefer the complete, programmatically fetched CVPR proceedings entry.
# Match any entry type so that a previous malformed replacement can be repaired.
cvf = ROOT/'literature/raw_bibtex/adaface_cvf2022.bib'
if cvf.exists():
    raw = cvf.read_text()
    validate_entries(raw)
    correct = re.sub(r'^(@\w+\{)[^,]+', lambda m: m.group(1)+'adaface', raw, count=1)
    bib, replacements = re.subn(r'@\w+\{adaface,.*?(?=\n\s*@|\Z)', lambda m: correct+'\n', bib, flags=re.S)
    if replacements != 1:
        raise ValueError('Expected exactly one AdaFace entry')
entries = validate_entries(bib)
if '--validate-only' in sys.argv:
    validate_entries((PAPER/'references.bib').read_text())
    print(f'Validated {len(entries)} complete BibTeX entries; no files changed.')
    raise SystemExit(0)
# All source metadata is validated before any output is mutated.
(ROOT/'literature/verified_references.bib').write_text(bib)
(PAPER/'references.bib').write_text(bib)
urls = {
 'consisid':'https://github.com/PKU-YuanGroup/ConsisID',
 'celebvhq':'https://github.com/CelebV-HQ/CelebV-HQ',
 'vbench':'https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html',
 'adaface':'https://openaccess.thecvf.com/content/CVPR2022/html/Kim_AdaFace_Quality_Adaptive_Margin_for_Face_Recognition_CVPR_2022_paper.html',
}
inline, mdrefs, metas = [], [], {}
for entry in entries:
    key = re.search(r'@\w+\{([^,]+)',entry).group(1)
    author, title, year = field(entry,'author'), field(entry,'title'), field(entry,'year')
    title = title.replace('{','').replace('}','')
    names = author.split(' and ')
    surname = names[0].split(',')[0] if ',' in names[0] else names[0].split()[-1]
    if names[0]=='Team Wan': surname='Team Wan'
    short = surname + (' et~al.' if len(names)>2 else (' and '+names[1].split()[-1] if len(names)==2 else ''))
    authors = ', '.join(names[:3]) + (', et al.' if len(names)>3 else '')
    url = field(entry,'url') or urls.get(key,'')
    where = field(entry,'booktitle') or ('arXiv:'+field(entry,'eprint'))
    item = f'\\bibitem[{short}({year})]{{{key}}}\n{authors}. \\emph{{{title}}}. {where}, {year}.'
    if url: item += '\\newline\\url{'+url+'}'
    inline.append(item)
    mdrefs.append(f'- **{key}**: {authors}. [{title}]({url}). {where}, {year}.')
    metas[key]={'title':title,'year':year,'url':url,'author':author}
bibliography='\\begin{thebibliography}{99}\n'+'\n\n'.join(inline)+'\n\\end{thebibliography}'
s=(PAPER/'main.tex').read_text()
s=re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}',lambda m:'% VERIFIED_BIBLIOGRAPHY_INSERTION_POINT',s,flags=re.S)
s=s.replace('% VERIFIED_BIBLIOGRAPHY_INSERTION_POINT',bibliography)
(PAPER/'main.tex').write_text(s)
# ICML 2026 is a layout reference only, not a submission declaration.
body=s[s.index('\\begin{abstract}'):]
preamble=r'''% DRAFT v0. NO EMPIRICAL RESULTS. ICML 2026 LAYOUT REFERENCE ONLY.
\documentclass{article}
\usepackage{microtype,graphicx,booktabs,hyperref}
\usepackage{icml2026_reference/icml2026}
\usepackage{amsmath,amssymb,array}
\newcommand{\sg}{\operatorname{sg}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\pending}{\textsf{PENDING}}
\newcommand{\cneed}[1]{\textbf{[CITATION NEEDED: #1]}}
\icmltitlerunning{Condition-Preserving Distillation: Research Plan}
\begin{document}
\twocolumn[
\icmltitle{Condition-Preserving Distillation from a Teacher without the Student's Reference Condition}
\begin{icmlauthorlist}
\icmlauthor{Anonymous Authors}{anon}
\end{icmlauthorlist}
\icmlaffiliation{anon}{Anonymous Institution}
\icmlkeywords{Diffusion distillation, conditional generation, research plan}
\vskip 0.3in
]
\printAffiliationsAndNotice{}
\noindent\textbf{DRAFT v0 --- no empirical results; ICML target year unconfirmed.}
'''
# Keep wide planned-control tables readable in two columns.
body=body.replace('\\begin{table}[t]','\\begin{table*}[t]').replace('\\end{table}','\\end{table*}')
(PAPER/'main_icml2026.tex').write_text(preamble+'\n'+body)
# Produce a reading copy. Protect LaTeX math from text transformations.
text=s[s.index('\\begin{abstract}'):]
text=re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', '', text, flags=re.S)
maths=[]
def hold(m):
    maths.append(m.group(0));return f'MATHPLACEHOLDER{len(maths)-1}END'
text=re.sub(r'\\begin\{(?:equation|align)\}.*?\\end\{(?:equation|align)\}|\$[^$]*\$', hold, text, flags=re.S)
def tabular_body(block):
    """Skip a balanced column specification, including nested p{...} widths."""
    opening = re.search(r'\\begin\{tabular\}(?:\[[^]]*\])?\s*\{', block)
    if not opening:
        raise ValueError('Table has no supported tabular environment')
    depth, cursor = 1, opening.end()
    while depth and cursor < len(block):
        char = block[cursor]
        if char == '\\':
            cursor += 2
            continue
        if char == '{': depth += 1
        elif char == '}': depth -= 1
        cursor += 1
    if depth:
        raise ValueError('Unbalanced tabular column specification')
    ending = block.find(r'\end{tabular}', cursor)
    if ending < 0:
        raise ValueError('Table has no closing tabular environment')
    return block[cursor:ending]

def table(m):
    block=m.group(0)
    cap=re.search(r'\\caption\{(.*?)\}\s*\\end\{table\}',block,re.S)
    raw=tabular_body(block)
    raw=re.sub(r'\\(?:toprule|midrule|bottomrule)','',raw)
    rows=[]
    for row in raw.split('\\\\'):
        row=row.strip()
        if row: rows.append('| '+' | '.join(x.strip() for x in row.split('&'))+' |')
    if rows:rows.insert(1,'| '+' | '.join(['---']*(rows[0].count('|')-1))+' |')
    return '\n\n'+'\n'.join(rows)+'\n\n'+(cap.group(1) if cap else '')+'\n\n'
text=re.sub(r'\\begin\{table\}.*?\\end\{table\}',table,text,flags=re.S)
text=text.replace('\\begin{abstract}','## Abstract').replace('\\end{abstract}','')
text=re.sub(r'\\section\*?\{([^}]+)\}',lambda m:'\n## '+m.group(1)+'\n',text)
text=re.sub(r'\\subsection\{([^}]+)\}',lambda m:'\n### '+m.group(1)+'\n',text)
text=re.sub(r'\\paragraph\{([^}]+)\}',lambda m:'\n**'+m.group(1)+'** ',text)
text=re.sub(r'\\cneed\{([^}]+)\}',lambda m:'**[CITATION NEEDED: '+m.group(1)+']**',text)
text=re.sub(r'\\(?:emph|textit)\{([^}]+)\}',lambda m:'*'+m.group(1)+'*',text)
text=re.sub(r'\\textbf\{([^}]+)\}',lambda m:'**'+m.group(1)+'**',text)
text=re.sub(r'\\cite\{([^}]+)\}',lambda m:'('+', '.join('['+k+']('+metas[k]['url']+')' for k in m.group(1).split(','))+')',text)
text=re.sub(r'\\url\{([^}]+)\}',lambda m:'[source]('+m.group(1)+')',text)
text=re.sub(r'\\ref\{([^}]+)\}',lambda m:'('+m.group(1)+')',text)
text=text.replace('\\begin{enumerate}','').replace('\\end{enumerate}','').replace('\\item ','\n1. ')
text=text.replace('\\appendix','\n## Appendices\n').replace('\\end{document}','').replace('\\pending','PENDING').replace('\\%','%').replace('~',' ')
text=text.replace('\\footnote{',' (Footnote: ').replace('manifest.}', 'manifest.)')
for i,math in enumerate(maths):
    if math.startswith('\\begin'):
        is_align=math.startswith('\\begin{align}')
        math=re.sub(r'\\(?:begin|end)\{(?:equation|align)\}','',math)
        math=re.sub(r'\\label\{[^}]+\}','',math).replace('\\nonumber','')
        math=math.strip()
        if is_align: math='\\begin{aligned}\n'+math+'\n\\end{aligned}'
        math='\n$$\n'+math+'\n$$\n'
    math=re.sub(r'\\sg\b',r'\\operatorname{sg}',math)
    math=re.sub(r'\\E\b',r'\\mathbb{E}',math)
    math=re.sub(r'\\R\b',r'\\mathbb{R}',math)
    text=text.replace(f'MATHPLACEHOLDER{i}END',math)
text=re.sub(r'\n{3,}','\n\n',text)
header='# Condition-Preserving Distillation from a Teacher without the Student\'s Reference Condition\n\n**DRAFT v0 — October 26, 2026. Research plan; no empirical results.**\n\nReading copy generated from `main.tex`; TeX is authoritative for equations and formatting. Target ICML year is unconfirmed.\n\n'
(PAPER/'draft.md').write_text(header+text+'\n\n## Verified References\n\n'+'\n\n'.join(mdrefs)+'\n')
print('Wrote main.tex, main_icml2026.tex, draft.md and 12 verified citations.')
