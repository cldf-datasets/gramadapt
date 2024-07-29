"""

"""
import re
import collections
import unicodedata

from pybtex import database
from pycldf.sources import Source
from clld.lib.bibtex import unescape

from cldfbench_gramadapt import Dataset

CITES = 0


def valid_bibtex(lines):
    try:
        database.parse_string('\n'.join(lines), 'bibtex')
        return True
    except:
        return False


def parse_refs(p, ays=None):
    bibtex, in_refs, in_ref, with_refs = [], False, 0, False
    rem = []
    rev = {} if ays is None else {v: k for k, v in ays.items()}
    cited = set()
    #if ays:
    #    print(rev)
    for line in p.read_text(encoding='utf8').split('\n'):
        line = line.strip()
        if in_refs:
            if not line:
                continue
            if in_ref:
                bibtex.append(line)
                in_ref += line.count('{')
                in_ref -= line.count('}')
            else:
                if line.strip().startswith('@'):
                    bibtex.append(line)
                    in_ref += line.count('{')
                    in_ref -= line.count('}')
                else:
                    in_refs = False
        elif '*References*' in line:
            #
            # FIXME: append CLDF Markdown link to render cited refs!
            #
            with_refs = True
            in_refs = True
        else:
            if ays:
                # Replace citations!
                #line = parse_cite(line, rev)
                cited |= parse_cite(line, rev)
                pass
            rem.append(line)
    if ays:
        #for k, v in ays.items():
        #    if k not in cited:
        #        print(p.stem, k, v)
        return '\n'.join(rem)
    if with_refs:
        assert bibtex or p.stem in [
            'D12', 'D1_DTR02', 'DFK09', 'DFK29', 'E1', 'OB1', 'OT1', 'T1', 'D10', 'I1', 'I2',
            'O1',
        ], p.name
        assert valid_bibtex(bibtex), '\n'.join(bibtex)
        return '\n'.join(bibtex)


def run(args):
    known = ['EK', 'FDG', 'OR', 'KS', 'RNDS', 'AH', 'KK']
    ds = Dataset()
    bib = {}
    refs = collections.defaultdict(dict)
    for p in sorted(ds.dir.joinpath('rationale').glob('*.md'), key=lambda pp: pp.name):

        lines = p.read_text(encoding='utf-8').split('\n')
        last_line = [l for l in lines if l.strip()][-1]
        contribs = [m.group('contrib') for m in re.finditer(r'(?P<contrib>[A-Z]+)', last_line)]
        if any(c not in known for c in contribs):
            print('---', p.stem)
            print(last_line)
            print(contribs)
        if not contribs:
            print('---', p.stem)
            print(last_line)
        #
        #if p.stem != 'BA':
        #    continue
        r = parse_refs(p)
        if r:
            for k, v in database.parse_string(r, 'bibtex').entries.items():
                if 'date' in v.fields:
                    v.fields['year'] = v.fields.pop('date')
                v = Source.from_entry(k, v)
                for f in ['author', 'editor', 'title', 'booktitle']:
                    if f in v:
                        v[f] = unescape(v[f]).replace(r'\aa', 'å').replace(r'\ae', 'æ')
                if k not in bib:
                    bib[k] = v
                key = v.refkey()
                author, year = key.split('(')
                author = author.strip().replace(' and ', ' & ')
                year = year.replace(')', '').strip()
                #print(p.name, author, year)
                refs[p.name][k] = (author, year)
    for p in sorted(ds.dir.joinpath('rationale').glob('*.md'), key=lambda pp: pp.name):
        if p.name in refs:
            #if p.stem != 'OI0':
            #    continue
            #    print(list(refs[p.name].values()))

            r = parse_refs(p, ays=refs[p.name])
    #for _, v in sorted(bib.items(), key=lambda i: i[0]):
    #    print(v.bibtex())
    global CITES
    print(len(bib))
    print(CITES)


def parse_cite(line, ays):
    """
    (Giles 1978; Giles & Byrne 1982)
    (Kirby et al. 2016; 2018a; see [https://d-place.org/parameters/B009#1/29/169](https://www.google.com/url?q=https%3A%2F%2Fd-place.org%2Fparameters%2FB009%231%2F29%2F169&sa=D&sntz=1&usg=AOvVaw1EAEgU3zT2lpmzI73NlP0Q))
    """
    line = unicodedata.normalize('NFC', line)

    # 1. compute list of (author, year) pairs from References section
    # 2. plug into patterns (Author Year(: pages)?(; Author Year(: pages)?)*), Author (Year(: pages)?)
    # 3. replace matches by markdown links [Author](bibkey), [Year](bibkey).

    #
    # FIXME: google.com URLs
    #
    global CITES

    cited = set()

    a = []
    for aa, yy in ays:
        a.append(aa)
        if ' & ' in aa:
            a.append(aa.replace(' & ', ' and '))
    author = r'(?P<author>{})'.format('|'.join(re.escape(v) for v in a))

    def norm_ay(a, y):
        a = a.strip().replace(' and ', ' & ')
        y = y.strip()
        if (a, y) not in ays and y[-1] in 'abcde':
            y = y[:-1]
        if (a, y) not in ays and '–' in y:
            y = y.replace('–', '/')
        return (a, y)

    # in text citation like " Coupland & Bishop 2007 "
    p = re.compile(r'\s+' + author + r'\s+(?P<year>[0-9]+([a-z])?)\s+')
    for m in p.finditer(line):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            CITES += 1
            cited.add(ays[ay])


    # "Friedkin 1988;|)"
    p = re.compile(author + r'\s+(?P<year>[0-9][^,;):.]+)(:\s+(?P<pages>[^);,.]+))?(?P<delim>[,);.])')
    for m in p.finditer(line):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            CITES += 1
            cited.add(ays[ay])

    # Moore (2008: 66)
    p = re.compile(author + r"(?P<inner>(’s\s+[a-z]+)|('s)|(’s))?\s+\((?P<year>[0-9][^:;)]+)(:\s*(?P<pages>[^)]+))?(?P<delim>[);])")
    for m in p.finditer(line):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            CITES += 1
            cited.add(ays[ay])

    ## (Collar 2007: 153)
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author>{})\s+(?P<year>[^:)]+)(:\s*(?P<pages>[^)]+))?\)'.format('|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    ay = (m.group('author').strip(), m.group('year').strip())
    #    if ay in ays:
    #        cited.add(ays[ay])
    #        CITES += 1
    #        #print('-{}-{}-{}-'.format(m.group('author'), m.group('year'), m.group('pages')))
    # (Giles 1978; Giles & Byrne 1982)
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author1>{0})\s+(?P<year1>[^;:]+)(:\s*(?P<pages>[^;]+))?;\s+(?P<author2>{0})\s+(?P<year2>[^):]+)(:\s*(?P<pages2>[^)]+))?\)'.format(
    #    '|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    for i in ['1', '2']:
    #        ay = (m.group('author' + i).strip(), m.group('year' + i).strip())
    #        if ay in ays:
    #            cited.add(ays[ay])
    #            CITES += 1
    #            #print('-{}-{}-{}-'.format(m.group('author'), m.group('year'), m.group('pages')))
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author1>{0})\s+(?P<year1>[^;]+);\s+(?P<author2>{0})\s+(?P<year2>[^;]+);\s+(?P<author3>{0})\s+(?P<year3>[^)]+)\)'.format(
    #    '|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    for i in ['1', '2', '3']:
    #        ay = (m.group('author' + i).strip(), m.group('year' + i).strip())
    #        if ay in ays:
    #            cited.add(ays[ay])
    #            CITES += 1
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author1>{0})\s+(?P<year1>[^;]+);\s+(?P<author2>{0})\s+(?P<year2>[^;]+);\s+(?P<author3>{0})\s+(?P<year3>[^;]+);\s+(?P<author4>{0})\s+(?P<year4>[^)]+)\)'.format(
    #    '|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    for i in ['1', '2', '3', '4']:
    #        ay = (m.group('author' + i).strip(), m.group('year' + i).strip())
    #        if ay in ays:
    #            cited.add(ays[ay])
    #            CITES += 1
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author1>{0})\s+(?P<year1>[^;]+);\s+(?P<author2>{0})\s+(?P<year2>[^;]+);\s+(?P<author3>{0})\s+(?P<year3>[^;]+);\s+(?P<author4>{0})\s+(?P<year4>[^;]+);\s+(?P<author5>{0})\s+(?P<year5>[^)]+)\)'.format(
    #    '|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    for i in ['1', '2', '3', '4', '5']:
    #        ay = (m.group('author' + i).strip(), m.group('year' + i).strip())
    #        if ay in ays:
    #            cited.add(ays[ay])
    #            CITES += 1
    #p2 = re.compile(r'\(((see|e\.g\.)\s+)?(?P<author1>{0})\s+(?P<year1>[^;]+);\s+(?P<author2>{0})\s+(?P<year2>[^;]+);\s+(?P<author3>{0})\s+(?P<year3>[^;]+);\s+(?P<author4>{0})\s+(?P<year4>[^;]+);\s+(?P<author5>{0})\s+(?P<year5>[^;]+);\s+(?P<author6>{0})\s+(?P<year6>[^)]+)\)'.format(
    #    '|'.join(re.escape(v[0]) for v in ays.keys())))
    #for m in p2.finditer(line):
    #    for i in ['1', '2', '3', '4', '5', '6']:
    #        ay = (m.group('author' + i).strip(), m.group('year' + i).strip())
    #        if ay in ays:
    #            cited.add(ays[ay])
    #            CITES += 1
    # (Kirby et al. 2016; 2018a;

    for i in range(4):
        inner_years = ''
        for j in range(i + 1):
            inner_years += r'\s+(?P<year{0}>[0-9][^;,\s]+)(?P<delim{0}>[;,])'.format(j + 1)

        p = re.compile(author + inner_years + r'\s*(?P<year{0}>[0-9][^\s)]+)(?P<delim{0}>\))'.format(i + 2))
        for m in p.finditer(line):
            for j in range(i + 2):
                ay = norm_ay(m.group('author'), m.group('year{}'.format(j + 1)))
                if ay in ays:
                    #print(ay)
                    cited.add(ays[ay])
                    CITES += 1
                    #print('-{}-{}-{}-'.format(m.group('author'), m.group('year'), m.group('pages')))
    return cited
    return line
