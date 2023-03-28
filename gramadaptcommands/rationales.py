"""

"""
import io
import re
import pathlib

import requests
from lxml.etree import parse, HTMLParser

from cldfbench_gramadapt import Dataset


def run(args):
    """
    https://sites.google.com/view/rs210205edomains-questionnaire/d-set
    https://sites.google.com/view/rs210205edomains-questionnaire/overview-rationales
    """
    outdir = Dataset().dir / 'rationale'
    for doc in ['d-set', 'overview-rationales', 'home']:
        url = 'https://sites.google.com/view/rs210205edomains-questionnaire/' + doc

        doc = parse(io.StringIO(requests.get(url).text), HTMLParser())
        lines, fname = [], None
        for e in doc.getiterator():
            if e.tag == 'h2':
                if fname:
                    print('{}.md'.format(fname))
                    outdir.joinpath(fname + '.md').write_text('\n'.join(lines))
                t = ws(''.join(e.itertext()))
                assert ':' in t
                lines, fname = [], t.split(':')[0].strip()
                m = re.search('\(([A-Z0-9,\s]+)\)', t)
                if m:
                    fname += '_{}'.format(m.groups()[0].replace(',', '').replace(' ', '_'))
                lines.append('\n## ' + t + '\n')
            elif e.tag == 'p' and not child_of(e, 'ul'):
                lines.append(text(e).strip() + '\n')
            elif e.tag == 'small' and not child_of(e, 'ul'):
                t = text(e).strip()
                if t:
                    m = re.match(r'\(([0-9]+)\)\s*', t)
                    n = m.groups()[0] if m else '1'
                    t = t[m.end():] if m else t
                    lines.append('[^{}] {}'.format(n, t))
                #
                # FIXME: replace footnote refs in text above!
                #
            elif e.tag == 'ul' and not child_of(e, 'ul'):
                res = ''
                for li in e.findall('li'):
                    for i, line in enumerate(text(li).strip().split('\n')):
                        if line.strip():
                            res += ('- ' if i == 0 else '  ') + line.strip() + '\n'
                res += '\n'
                lines.append(res)
        if fname:
            print('{}.md'.format(fname))
            outdir.joinpath(fname + '.md').write_text('\n'.join(lines))


def tt(html):
    return text(parse(io.StringIO(html), HTMLParser()).getroot())


def child_of(e, tag):
    p = e.getparent()
    while p:
        if p.tag == tag:
            return True
        p = p.getparent()
    return False


def ws(s):
    return re.sub(r'\s+', ' ', s.strip())


def text(e, inner=False):
    res = e.text or ''
    if inner:
        res += e.tail if e.tail else ''
    if inner:
        return res
    for ee in e.getiterator():
        if ee.tag == 'em':
            pref = '*'
            if res.endswith('*') and not res.endswith('**'):
                res = res[:-1]
                pref = ''
            res += '{}{}*'.format(pref, ws(''.join(ee.itertext())))
            if ee.tail:
                res += ee.tail
        elif ee.tag == 'strong':
            pref = '**'
            if res.endswith('**'):
                res = res[:-2]
                pref = ''
            t = ws(''.join(ee.itertext()))
            if t:
                res += '{}{}**'.format(pref, t)
            if ee.tail:
                res += ee.tail
        elif ee.tag == 'br':
            res += '\n'
            if ee.tail:
                res += ee.tail
        elif ee.tag == 'a':
            res += '[{}]({})'.format(''.join(ee.itertext()), ee.attrib.get('href'))
            if ee.tail:
                res += ee.tail
        elif not any(child_of(ee, t) for t in {'a', 'em', 'strong', 'br'}):
            res += text(ee, inner=True)
    return res
