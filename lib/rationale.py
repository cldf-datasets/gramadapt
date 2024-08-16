"""

"""
import re
import functools
import itertools
import unicodedata

import attrs
from pybtex import database
from pycldf.sources import Source
from clld.lib.bibtex import unescape

CITES = 0


class Reference(Source):
    @property
    def author_year(self):
        author, year = self.refkey().split('(')
        return (author.strip().replace(' and ', ' & '), year.replace(')', '').strip())

    @classmethod
    def from_bibdata(cls, k, v):
        if 'date' in v.fields:
            v.fields['year'] = v.fields.pop('date')
        v = cls.from_entry(k, v)
        for f in ['author', 'editor', 'title', 'booktitle', 'publisher', 'shorttitle']:
            # Should we fix {{The Editors of Encyclopedia Britannica}} ?
            if f in v:
                v[f] = unescape(v[f]).replace(r'\aa', 'å').replace(r'\ae', 'æ')
        return v


@attrs.define
class Rationale:
    id = attrs.field()
    name = attrs.field()
    contributors = attrs.field(validator=attrs.validators.instance_of(list))
    references = attrs.field(validator=attrs.validators.instance_of(list))
    citations = attrs.field()
    lines = attrs.field()

    @contributors.validator
    def valid_contributor(self, attribute, value):
        if not value:
            raise ValueError(value)
        if any(c not in ['EK', 'FDG', 'OR', 'KS', 'RNDS', 'AH', 'KK'] for c in value):
            raise ValueError()

    @classmethod
    def from_path(cls, p):
        # Drop trailing empty lines:
        lines = list(reversed(list(itertools.dropwhile(
            lambda l: not l.strip(), reversed(p.read_text(encoding='utf-8').split('\n'))))))

        name = None
        rem = []
        for line in lines:
            if not name:
                if line.startswith('#'):
                    name = re.sub(r'^#+\s+', '', line)
                elif line.strip():
                    raise ValueError()
            else:
                rem.append(line)

        last_line, lines = rem[-1], rem[:-1]
        contribs = [m.group('contrib') for m in re.finditer(r'(?P<contrib>[A-Z]+)', last_line)]

        lines, refs = parse_refs(lines)
        # FIXME: replace References section with corresponding CLDF Markdown formatting
        cited = []
        if not refs:
            assert p.stem in [  # Known rationales without a References section:
                'DFK09', 'DFK29',
                'E1', 'E2', 'E4', 'E5',
                'OB1', 'OT1', 'OL2',
                'T1', 'T2', 'D10', 'I1', 'I2',
                'O1', 'P2', 'OV',
            ], p.name
        else:
            refs = [Reference.from_bibdata(k, v) for k, v in refs]
            rem = []
            rev = {r.author_year: r.id for r in refs}
            for line in lines:
                line = line.strip()
                line, c = parse_cite(line, rev)
                cited.extend(c)
                rem.append(line)
            rem.append('\n## References\n\n[References](Source?cited_only&with_link#cldf:__all__)')
            lines = rem

        rem = []
        for line in lines:
            line = fix_rationale_links(line)
            if line.startswith('**') and line.endswith('**'):
                rem.append('')
                rem.append('## {}'.format(norm_section(line[2:-2].strip())))
            else:
                rem.append(line)

            refids = {r.id for r in refs}
            #if refids - set(cited):
            #    print('{}\tUncited: {}\t{}'.format(p.stem, refids - set(cited), rev))

        return cls(
            id=p.stem,
            name=name,
            contributors=contribs,
            references=refs,
            lines=rem,
            citations=cited)

    @property
    def cldf_markdown(self):
        res = [
            '# [](ContributionTable?__template__=property.md&property=name#cldf:{})\n'.format(self.id),
            'Authors: [](ContributionTable'
            '?__template__=property.md&property=contributor#cldf:{})\n'.format(self.id),
        ]
        return '\n'.join(res + self.lines).replace('\n\n\n', '\n')


def norm_section(s):
    return {
        'Definition': 'Definitions', #  12
        'Theoretical and Empirical Support': 'Theoretical & Empirical Support', #  2
        'Theoretical&Empirical Support': 'Theoretical & Empirical Support', #  1
        'Theoretical & EmpiricalSupport': 'Theoretical & Empirical Support', #  1
        'Example': 'Examples', #  18
        'Theoretical support': 'Theoretical Support', #  5
        'Answer options': 'Answer Options', #  1
        'Definitions and examples': 'Definitions and Examples', #  1
    }.get(s, s)


def fix_rationale_links(line):
    """
    [T6](https://www.google.com/url?q=https%3A%2F%2Fsites.google.com%2Fview%2Frs210205edomains-questionnaire%2Fhome%23h.wrnznasw7ysz&sa=D&sntz=1&usg=AOvVaw0UooR21z09COoC0-Rchl6k)
    """
    from clldutils.markup import MarkdownLink

    def repl(ml):
        if ml.parsed_url.netloc == 'www.google.com':
            if re.fullmatch(r'[A-Z][A-Z0-9_]+', ml.label):
                return '[{}]({}.md)'.format(ml.label, ml.label)
            return ml.label

    return MarkdownLink.replace(line, repl)


def parse_refs(lines):
    bibtex, in_refs, in_ref = [], False, 0
    rem = []
    for line in lines:
        line = line.strip()
        if '*References*' in line:
            #
            # FIXME: append CLDF Markdown link to render cited refs!
            #
            in_refs = True
            continue
        if in_refs:
            if not line:
                continue
            if in_ref:
                bibtex.append(line)
                in_ref += line.count('{')
                in_ref -= line.count('}')
            else:
                if line.startswith('@'):
                    bibtex.append(line)
                    in_ref += line.count('{')
                    in_ref -= line.count('}')
                else:
                    in_refs = False
        if not in_refs:
            rem.append(line)
    if bibtex:
        return rem, list(database.parse_string('\n'.join(bibtex), 'bibtex').entries.items())
    return rem, []


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

    cited = []

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

    def link(ay, label):
        return '[{}](sources.bib?ref&with_internal_ref_link&keep_label#cldf:{})'.format(label, ays[ay])

    # in text citation like " Coupland & Bishop 2007 "
    def repl(m):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            cited.append(ays[ay])
            return ' {} {} '.format(link(ay, m.group('author')), link(ay, m.group('year')))
        return m.string[m.start():m.end()]

    p = re.compile(r'\s+' + author + r'\s+(?P<year>(\[[0-9]{4}]\s*)?[0-9]+([a-z])?)\s+')
    line = p.sub(repl, line)

    # "Friedkin 1988;|)"
    def repl(m):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            cited.append(ays[ay])
            return '{} {}{}{}'.format(
                link(ay, m.group('author')),
                link(ay, m.group('year')),
                ': {}'.format(m.group('pages')) if m.group('pages') else '',
                m.group('delim'))
        return m.string[m.start():m.end()]

    p = re.compile(author + r'\s+(?P<year>(\[[0-9]{4}]\s*)?[0-9][^,;):.]+)(:\s+(?P<pages>[^);,.]+))?(?P<delim>[,);.])')
    line = p.sub(repl, line)

    # Moore’s (2008: 66)
    def repl(m):
        ay = norm_ay(m.group('author'), m.group('year'))
        if ay in ays:
            cited.append(ays[ay])
            return '{} {}({}{}{}'.format(
                link(ay, m.group('author')),
                m.group('inner') + ' ' if m.group('inner') else '',
                link(ay, m.group('year')),
                ': {}'.format(m.group('pages')) if m.group('pages') else '',
                m.group('delim'))
        return m.string[m.start():m.end()]

    p = re.compile(author + r"(?P<inner>(’s\s+[a-z]+)|('s)|(’s))?\s+\((?P<year>[0-9][^:;)]+)(:\s*(?P<pages>[^)]+))?(?P<delim>[);])")
    line = p.sub(repl, line)

    # Trudgill (2004; 2010; 2011)
    def repl(i, m):
        nays = [norm_ay(m.group('author'), m.group('year{}'.format(j))) for j in range(1, i + 3)]
        if all(ay in ays for ay in nays):
            res = '{} {}'.format(m.group('author'), m.group('bracket') or '')
            for j, ay in enumerate(ays, start=1):
                cited.append(ays[ay])
                res += '{}{} '.format(
                    link(ay, m.group('year{}'.format(j))), m.group('delim{}'.format(j)))
            return res.strip()
        return m.string[m.start():m.end()]

    for i in range(4):  # Trudgill (2004; 2010; 2011)
        inner_years = ''
        for j in range(i + 1):
            inner_years += (r'\s+' + (r'(?P<bracket>\()?' if j == 0 else '') +
                            r'(?P<year{0}>[0-9][^;,\s]+)(?P<delim{0}>[;,])'.format(j + 1))
        p = re.compile(author + inner_years + r'\s*(?P<year{0}>[0-9][^\s)]+)(?P<delim{0}>\))'.format(i + 2))
        line = p.sub(functools.partial(repl, i), line)

    return line, cited
