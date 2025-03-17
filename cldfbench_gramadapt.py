import re
import pathlib
import itertools
import contextlib
import collections

from clldutils.misc import slug
from clldutils.markup import add_markdown_text
from cldfbench import Dataset as BaseDataset, CLDFSpec
from cldfbench.metadata import get_creators_and_contributors
from nameparser import HumanName
from matplotlib import pyplot as plt

from lib.rationale import Rationale

NOTES = """
This dataset provides the data of the earlier released "raw" data (see above) formatted as 
[CLDF StructureDataset](https://cldf.clld.org). It also includes the
[rationales for the questionnaire construction](cldf/rationale/), as a set of short documents
formatted in Markdown. The relevant rationales for each group of questions are listed in the
column *Rationale* in [cldf/questions.csv](cldf/questions.csv).


## Contact pairs

![](map.svg)


## Data model

![](erd.svg)

For detailed descriptions of the tables and columns refer to [cldf/README.md](cldf/README.md).


## Notes

### Respondent comments vs Reviewer comments

Comments are directly written by the authors of the respective set. For multiauthor sets, the specific
respondent can be identified by the name associated with the particular answer by looking at the
`Respondent` column in the `ValueTable`.

Any comments in [square brackets] are those included by the editorial team for clarification.


### About the timeframe

Each contact set is unique in terms of the timeframe they respond for. We urge researchers who use
this dataset to read the `Value` and `Comment` columns in `ValueTable` for answers to questions
marked as timeframe comments (via the `Is_Timeframe_Comment` in `ParameterTable`) carefully for each
set, to get a sense of the heterogeneity of timeframes represented in each set, as well as the whole
dataset.

The timeframes given are broad and coarse approximations, often negotiated between the respondent
and reviewer. These timeframes are to be used with caution. Always read the associated comments.

An end date of 2020 (or later) indicates that social contact is ongoing at the time of data
collection in 2021. 


### Idiosyncratic contact sets

Set26 "Garifuna - Galibi" only contains responses for the Overview.
Set10 "FLNA - NLNA" and set22 "Muak Sa-aak - Tai Lue" have restricted public access to the data;
see "Data Sensitivity" section below.


### Data Sensitivity

The respondents of sets 10 and 22 have requested access restrictions to their respective datasets. 

The respondent of set10 has requested to have community identifying names anonymised. The
respondent name for set 10 has also been anonymised. If you wish to access the community
identifying names for set10, please contact Kaius Sinnemäki at the University of Helsinki, and he
will get in contact with the author of set10. 

The respondent for set22 has requested to make certain comments publicly invisible, due to their
potentially sensitive nature. If you wish to access the invisible comments of set 22, please
contact the author directly.

"""
TAGS = {
    # Domains Questionnaire
    "P": "Preamble",
    "D": "Domain characterisation",
    "S": "Social network",
    "B": "Behaviour affecting biases",  # BA|BH|BI
    "O": "Linguistic output of Focus group people",
    "I": "Linguistic input of Focus group people, i.e. the output of Neighbour group people",
    "T": "Language transmission to children",
    "E": "Ending questions about data source and confidence",
    # Overview Questionnaire
    "OD": "Demographics",
    "OG": "Language geography",
    "OI": "Language and identity",
    "OL": "Literacy",
    "OS": "Social structure",
    "OH": "History",
    "OE": "Respondent fieldwork experience",
    "OC": "Response confidence",
    "OB": "Behaviour affecting biases",
    "OT": "Time frame",  # OT1, OT2
}
MULTICAUSAL_FACTORS = {
    "Use Equivalence":
        "Questions pertaining to whether language use is equivalent or language contact dynamics "
        "between Focus and Neighbour Groups as used in equivalent ways or not. The tag relates to "
        "questions of language uses in social domains, and discrepancies in fluency between Focus "
        "and Neighbour group people when speaking.",
    "Socio-Political Power":
        "Questions on whether there are differences in socio-political power between the Focus and "
        "Neighbour groups.",
    "Language Loyalty":
        "For the purpose of this dataset language loyalty is defined as a tendency to be loyal to "
        "one’s language, typically by expressing a desire to retain an identity that is expressed "
        "through the use of that language. This multicausal factor thus significantly overlaps "
        "with \"Use Equivalence\".",
    "Attitudes and Ideologies":
        "Concernts the two groups’ attitudes towards each other in general.",
}


def get_tag(cid):
    if cid == 'O10':  # Fix typo.
        cid = 'OI0'
    for k in sorted(TAGS, key=lambda x: (-len(x), x)):
        if cid.startswith(k):
            return k
    raise ValueError(cid)


def norm_datatype(pid, datatype):
    if pid == 'DEM13':
        return 'Scalar'
    if pid in {'OD1', 'OD3', 'OG1', 'OS7'}:
        return 'TypesSequential'
    return datatype


def norm_answer(s, opts=None, dt=''):
    if s.strip() == 'NA':
        return None
    if opts:  # A fixed set of options is given for valid answers. We try to pick one.
        if dt.endswith('Multiple'):
            # If multiple answers are allowed, we have to match repeatedly.
            res = []
            for opt in opts:
                if opt in s:
                    res.append(opt)
                    s = s.replace(opt, '').strip()
            assert not s, 'Unmatched stuff in answer: {}'.format(s)
            return res

        for opt in opts:
            if s == opt:
                return opt
            if slug(s) == slug(opt):  # Match fuzzily.
                return opt
    return s


def parse_time_range(s):
    if s in {'NA', 'XXXX-XXXX', '0000-0000'}:
        return
    if s == '-1050-450':
        return (-1050, -450)
    p = re.compile(r'(?P<start>-?[0-9]+)[-–](?P<end>[0-9]+)')
    m = p.fullmatch(s)
    assert m
    assert len(m.group('end')) >= len(m.group('start').replace('-', ''))
    start, end = int(m.group('start')), int(m.group('end'))
    assert end > start, s
    return (start, end)


def repl_placeholder(s):
    return s.replace("[q2o1answer]", "Focus Group").replace("[q2o2answer]", "Neighbour Group")


def norm_question(d):
    qs = [
	    "List any comments or notes that you feel are relevant to this section of the questionnaire.",
	    "Typically, what language do Focus Group children from four/five year of age prefer to speak with Neighbour Group adults?",
	    "Typically, how well does a Focus Group person understand the Neighbour Group in-law’s language?",
    ]
    # Chop off legacy numbering, replace markers.
    res = repl_placeholder(
        re.sub(r'^[0-9]+([ab])?\.\s*', '', d['Wording'] if isinstance(d, dict) else d))
    if res in qs:
        # We need to disambiguate.
        res = '{} [{}]'.format(res, d['Dom'])
    return res


def norm(rows, col):
    """
    Normalize content in the dicts in rows by setting the value for col to the most frequent value
    in rows.
    """
    counts = collections.Counter([row[col] for row in rows])
    selected = counts.most_common(1)[0][0]
    for row in rows:
        if row[col] != selected:
            row[col] = selected


def norm_comment(c):
    return None if c == 'NA' else (c or None)


def contributor_id(n):
    return slug(HumanName(n).last)


def get_rationale(rationales, cid, qid):
    """
    No rationales:
    - E6 is a comment box question so no need for a rationale
    - E1, 2, 3: No rationales.
    - C1 - 6: No rationales.

    P2, P2N and P3, P3N: I'm guessing P2 is P2Begin and P2N is P2End.
    These questions should be linked to a P2 rationale.
    """
    if cid in {'OE1', 'OE2', 'OE3', 'E6', 'OC1', 'OC2', 'OC3', 'OC4', 'OC5', 'OC6'}:
        return None, None
    if cid == 'O10':  # Fix typo.
        cid = 'OI0'
    if qid == 'DFKXX':
        qid = 'DFK29'
    # We must lookup more specific rationale first!
    for key, p in rationales.items():
        ccid, _, spec = key.partition('_')
        if ccid == cid and qid in spec:
            return key, p
    if qid in rationales:
        return qid, rationales[qid]
    if cid in rationales:
        return cid, rationales[cid]
    if cid.endswith('N') and cid[:-1] in rationales:
        return cid[:-1], rationales[cid[:-1]]
    res = rationales.get('{}_{}'.format(cid, qid))
    if res:
        return '{}_{}'.format(cid, qid), res
    raise ValueError('missing rationale: {} {}'.format(cid, qid))


def value(pid, d, **kw):
    res = dict(
        ID='{}-{}'.format(d['Set'], pid),
        Contactset_ID=d['Set'],
        Parameter_ID=pid,
        Language_ID='{}-F'.format(d['Set']),
        Comment=norm_comment(d['Comment']),
        Respondent=d['Respondent'],
    )
    res.update(kw)
    return res


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gramadapt"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):  # called from "cldfbench download"
        return

    def cmd_readme(self, args):
        """
        Create rendered rationales, i.e. expand dataset object references.
        """
        from cldfviz.text import render
        cldf = self.cldf_reader()
        for contrib in cldf.objects('ContributionTable'):
            if contrib.cldf.description:
                res = render(contrib.cldf.description, cldf, template_dir=self.etc_dir)
                self.cldf_dir.joinpath(
                    'rationale', '{}.md'.format(contrib.id)).write_text(res, encoding='utf8')
        return add_markdown_text(BaseDataset.cmd_readme(self, args), NOTES, section='Description')

    def cmd_makecldf(self, args):  # called from "cldfbench makecldf"
        self.schema(args.writer.cldf)
        glangs = {l.id: l for l in args.glottolog.api.languoids()}

        # We add two "synthetic" parameters which can later be used to plot contact pairs on a map.
        args.writer.objects['ParameterTable'].append(dict(
            ID='F',
            Name='Focus language',
            **{k.replace(' ', '_'): False for k in MULTICAUSAL_FACTORS},
        ))
        for code in ['Yes', 'No']:
            args.writer.objects['CodeTable'].append(dict(
                ID='F-{}'.format(code.lower()),
                Parameter_ID='F',
                Name=code,
            ))
        # We add the contact pair ID as value of a parameter.
        args.writer.objects['ParameterTable'].append(dict(
            ID='S',
            Name='Contact pair',
            **{k.replace(' ', '_'): False for k in MULTICAUSAL_FACTORS},
        ))

        authors, contributors = get_creators_and_contributors(
            self.dir.joinpath('CONTRIBUTORS.md').read_text(encoding='utf8'))
        editors = collections.OrderedDict((c['id'], c['name']) for c in authors if c['id'])
        respondents = {c['name']: False for c in authors + contributors}
        assert len(respondents) == len({slug(HumanName(n).last) for n in respondents})

        def citation(author, title):
            return "{}. {}. In {} (eds.). GramAdapt Crosslinguistic Social Contact Dataset.".format(
                author,
                title,
                ' and '.join(ed for ed in editors.values() if ed != 'Robert Forkel')).replace(
                '?.', '?')

        for p in sorted(self.dir.joinpath('rationale').glob('*.md'), key=lambda pp: pp.stem):
            r = Rationale.from_path(p)
            args.writer.cldf.add_sources(*r.references)
            args.writer.objects['ContributionTable'].append(dict(
                ID=r.id,
                Name=r.name,
                Description=r.cldf_markdown,
                Contributor=' and '.join(editors[cid] for cid in r.contributors),
                Author_IDs=[contributor_id(editors[cid]) for cid in r.contributors],
                Source=[s.id for s in r.references],
                Type='rationale',
                Document=r.id,
                Citation=citation(
                    ' and '.join(editors[cid] for cid in r.contributors),
                    'Rationale {}'.format(r.name)),
            ))
            p = self.cldf_dir / 'rationale' / '{}.md'.format(r.id)
            p.write_text(r.cldf_markdown, encoding='utf8')
            args.writer.objects['MediaTable'].append(dict(
                ID=p.stem,
                Name=p.name,
                Download_URL=str(p.relative_to(self.cldf_dir)),
                Media_Type='text/markdown',
            ))

        # Add language metadata: GA_V1.0.0_Metadata.csv
        for d in self.raw_dir.joinpath('On Zenodo copy').read_csv('GA_V1.0.0_Metadata.csv', dicts=True):
            args.writer.objects['CodeTable'].append(dict(
                ID='S-{}'.format(d['SetID']),
                Parameter_ID='S',
                Name=d['SetID'],
            ))
            for ltype in ['F', 'N']:  # We add both, focus and neighbouring languages to the table.
                glang = glangs.get(d['{}_Glottocode'.format(ltype)])
                latlon = {
                    'nort2964': (52.63985, -127.93325),
                    'wich1261': (-23.123400000000004, -62.5615),
                    'yuul1239': (-12.584506111111109, 135.12851972222222),
                }.get(d['{}_Glottocode'.format(ltype)])
                if not latlon:
                    geolang = glang
                    if geolang and not geolang.latitude:
                        for _, gc, _ in reversed(glang.lineage):
                            if glangs[gc].latitude:
                                geolang = glangs[gc]
                                break
                    if geolang:
                        latlon = (geolang.latitude, geolang.longitude)

                assert (not d['{}_Glottocode'.format(ltype)]) or latlon

                args.writer.objects['LanguageTable'].append(dict(
                    ID='{}-{}'.format(d['SetID'], ltype),
                    Name=d[ltype + '_Lang'],
                    Glottocode=glang.id if glang else None,
                    Latitude=latlon[0] if glang else None,
                    Longitude=latlon[1] if glang else None,
                    Macroarea=glang.macroareas[0].name if glang and glang.macroareas else None,
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='F-{}-{}'.format(d['SetID'], ltype),
                    Language_ID='{}-{}'.format(d['SetID'], ltype),
                    Parameter_ID='F',
                    Contactset_ID=d['SetID'],
                    Code_ID='F-yes' if ltype == 'F' else 'F-no',
                    Value='Yes' if ltype == 'F' else 'No',
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='S-{}-{}'.format(d['SetID'], ltype),
                    Language_ID='{}-{}'.format(d['SetID'], ltype),
                    Parameter_ID='S',
                    Contactset_ID=d['SetID'],
                    Code_ID='S-{}'.format(d['SetID']),
                    Value=d['SetID'],
                ))
            contribs = []
            for n in d['Respondents'].split(' & '):
                if n not in {'Anonymous'}:
                    assert n in respondents, n
                    contribs.append(contributor_id(n))
                    respondents[n] = True
            args.writer.objects['ContributionTable'].append(dict(
                ID=d['SetID'],
                Name=d['ContactPair'],
                Type='contactset',
                Contributor=d['Respondents'],
                Focus_Language_ID='{}-F'.format(d['SetID']),
                Neighbour_Language_ID='{}-N'.format(d['SetID']),
                Author_IDs=contribs,
                Reviewer_IDs=[
                    contributor_id(editors[eid.strip()]) for eid in d['Reviewer(s)'].split(',')],
                Area=d['AArea'],
                Citation=citation(d['Respondents'], '{}: {} and {}'.format(
                    d['SetID'], d['F_Lang'], d['N_Lang'])),
            ))

        rationales = {p.stem: p for p in self.dir.joinpath('rationale').glob('*.md')}
        rationales_linked = {k: False for k in rationales}

        mcfactors = {r['QID']: {k: v.strip().lower() for k, v in r.items()}
                     for r in self.raw_dir.read_csv('QN_2025_Tagging.csv', dicts=True)
                     if any(r[mcf].strip().lower() == 'yes' for mcf in MULTICAUSAL_FACTORS)}
        mcfactors['DFKXX'] = mcfactors['DFK29']
        qids = {r['QID'] for r in self.raw_dir.read_csv('V1_0_1.csv', dicts=True)}
        assert all(qid in qids for qid in mcfactors), {qid for qid in mcfactors if qid not in qids}

        domains = collections.defaultdict(dict)
        qids = set()
        vals = collections.defaultdict(lambda: collections.Counter())
        for (qid, subid), rows in itertools.groupby(
            sorted(
                self.raw_dir.read_csv('V1_0_1.csv', dicts=True),
                key=lambda r: (r['QID'], r['Sub.ID'], r['Set'])
            ),
            lambda r: (r['QID'], r['Sub.ID']),
        ):
            if qid == 'DFK29':  #  The responses to DFKXX are the “correct” one.
                args.log.info('Skipping DFK29')
                continue
            if subid in {'DEME29-3', 'DEME29-4'}:
                # These two sub-questions are logically dependent on another sub-question which had
                # only "No" responses for all sets.
                args.log.info('Skipping {}'.format(subid))
                continue

            mcf = {k.replace(' ', '_'):
                       mcfactors.get(qid, {}).get(k, '') == 'yes'
                   for k in MULTICAUSAL_FACTORS}
            # Add Name for questions.csv:
            pid = '{}_{}'.format(qid, subid) if subid else qid
            qnames = {
                "DEM30": "Child rearing obligations",
                "DEM37": "What type of marriage payments and transfers are expected when [q2o1answer] and [q2o2answer] marry?",
                "DFK02": "Co-residential units",
                "DFK38": "Are any of the following features characteristic when speaking to one’s [q2o2answer] in-laws?",
                "OI1": "Is [q2o1answer] stated as an expression of identity?",
                "OT1": "How long have [q2o1answer] and [q2o2answer] people been in contact overall?",
                "OT2": "What is the overall time frame when the largest number of people had the most opportunities for interaction?",
                "DEM0a": "How long have [q2o1answer] and [q2o2answer] people practised exchange for?",
                "DEM0b": "What is the time frame when the largest number of people had the most opportunities for interaction in exchange?",
                "DFK0a": "How long have [q2o1answer] and [q2o2answer] peoples been forming families with each other for?",
                "DFK0b": "What’s the time frame of densest contact between [q2o1answer] and [q2o2answer] as far as family formation is concerned?",
                "DKN0a": "How long have [q2o1answer] and [q2o2answer] people been involved in the knowledge domain together for?",
                "DKN0b": "What is the time frame when the largest number of people had the most opportunities for interaction in the knowledge domain?",
                "DLB0a": "How long have [q2o1answer] people and [q2o2answer] people worked together for?",
                "DLB0b": "What is the time frame when the largest number of people had the most opportunities for interaction in the labour domain?",
                "DLC0a": "How long have [q2o1answer] and [q2o2answer] people been in contact in the local community?",
                "DLC0b": "What is the time frame when the largest number of people had the most opportunities for interaction in the local community?",
                "DTR0a": "How long have [q2o1answer] and [q2o2answer] people traded for?",
                "DTR0b": "What is the time frame when the largest number of people had the most opportunities for interaction in trade?",
            }
            qnames = {k: norm_question(v) for k, v in qnames.items()}
            time_range = False
            if qid.endswith('N'):
                time_range = True
                qid = qid[:-1]  # Group the sub-question for a time range with the actual question.
                assert qid in qnames and pid.endswith('N')
            rows = list(rows)
            assert len({r['Dom'] for r in rows}) == 1
            assert len({r['CID'].replace('=', '') for r in rows}) == 1, {r['CID'] for r in rows}
            tag = get_tag(rows[0]['CID'])
            for col in ['Wording'] + ['Answer{}'.format(i + 1) for i in range(8)]:
                norm(rows, col)

            vals[pid].update([r['Response'] for r in rows])
            d = rows[0]

            if qid not in qids:
                rkey, cid = get_rationale(rationales, d['CID'], qid)
                if cid:
                    rationales_linked[rkey] = True
                rationales_linked[d['Dom']] = True
                args.writer.objects['questions.csv'].append(dict(
                    ID=qid, Rationale=[d['Dom']] + ([cid.stem] if cid else [])))
                qids.add(qid)
            if time_range:
                assert d['DataType'] == 'Value'
                assert d['Wording'] == 'Coarse time range, numerical'
                args.writer.objects['ParameterTable'].append(dict(
                    ID=pid + '0',
                    Name='Coarse time range, start [{}]'.format(pid),
                    Question_ID=qid,
                    datatype=d['DataType'],
                    Domain=d['Dom'],
                    Tag=tag,
                    ColumnSpec=dict(datatype=dict(base='integer', maximum=2020, minimum=-2000)),
                    **mcf,
                ))
                args.writer.objects['ParameterTable'].append(dict(
                    ID=pid + '1',
                    Name='Coarse time range, end [{}]'.format(pid),
                    Question_ID=qid,
                    datatype=d['DataType'],
                    Domain=d['Dom'],
                    Tag=tag,
                    ColumnSpec=dict(datatype=dict(base='integer', maximum=2020, minimum=-2000)),
                    **mcf,
                ))
            else:
                args.writer.objects['ParameterTable'].append(dict(
                    ID=pid,
                    Name=norm_question(d),
                    Question_ID=qid,
                    datatype=norm_datatype(pid, d['DataType']),
                    Domain=d['Dom'],
                    Tag=tag,
                    **mcf,
                ))
            for qid, qs in itertools.groupby(
                sorted(args.writer.objects['ParameterTable'], key=lambda r: r.get('Question_ID') or 'x'),
                lambda r: r.get('Question_ID'),
            ):
                if qid and qid not in qnames:
                    qs = list(qs)
                    if len(qs) == 1:
                        qnames[qid] = qs[0]['Name']
                    else:
                        assert all('.' in q['Name'] or ':' in q['Name'] for q in qs), qid
                        if '.' in qs[0]['Name']:
                            qname = {q['Name'].partition('.')[0].strip() for q in qs}
                            assert len(qname) == 1, str(qname)
                        else:
                            qname = {q['Name'].partition(':')[0].strip() for q in qs}
                            assert len(qname) == 1, str(qname)
                        qnames[qid] = qname.pop()

            for q in args.writer.objects['questions.csv']:
                q['Name'] = qnames[q['ID']]

            if d['DataType'] in ['Scalar', 'Types', 'TypesMultiple', 'TypesSequential']:
                codes = [norm_answer(d['Answer{}'.format(i)]) for i in range(1, 9)]
                codes = [c for c in codes if c is not None]
                if d['DataType'] == 'Scalar':
                    assert len(codes) == 5, pid
                for i, res in enumerate(codes, start=1):
                    args.writer.objects['CodeTable'].append(dict(
                        ID='{}-{}'.format(pid, i),
                        Parameter_ID=pid,
                        Name=repl_placeholder(res),
                        Ordinal=i if d['DataType'] in {'Scalar', 'TypesSequential'} else None,
                    ))
                    domains[pid][res] = '{}-{}'.format(pid, i)

            if d['DataType'] == 'Binary-YesNo':
                for code in ['Yes', 'No']:
                    args.writer.objects['CodeTable'].append(dict(
                        ID='{}-{}'.format(pid, code.lower()),
                        Parameter_ID=pid,
                        Name=code,
                    ))
                    domains[pid][code] = '{}-{}'.format(pid, code.lower())

            # Add response "B" as code for all questions with domains!
            if pid in domains:
                args.writer.objects['CodeTable'].append(dict(
                    ID='{}-B'.format(pid),
                    Parameter_ID=pid,
                    Name='B',
                    Description='“blank”. The question is relevant to the domain in question, but '
                                'the respondent chose not to answer the question.',
                ))
                domains[pid]['B'] = '{}-{}'.format(pid, 'B')

            for d in rows:
                if time_range:
                    v = parse_time_range(d['Response'])
                    if v:
                        for vv, typ in [(v[0], '0'), (v[1], '1')]:
                            args.writer.objects['ValueTable'].append(value(
                                pid + typ, d, Value=str(vv)))
                    continue
                res = norm_answer(d['Response'], domains.get(pid), d['DataType'])
                if res is None:
                    # Sometimes NA responses have useful comments. Keep!
                    args.writer.objects['ValueTable'].append(value(pid, d, Value=None))
                    continue
                if pid in domains:
                    for i, rr in enumerate(res if isinstance(res, list) else [res], start=1):
                        args.writer.objects['ValueTable'].append(value(
                            pid, d,
                            ID='{}-{}-{}'.format(d['Set'], pid, i) if
                            d['DataType'].endswith('Multiple') else '{}-{}'.format(d['Set'], pid),
                            Code_ID=domains[pid][rr],
                            Value=rr,
                        ))
                else:
                    args.writer.objects['ValueTable'].append(value(pid, d, Value=res))
        tfids = [q['ID'][:-2] for q in args.writer.objects['ParameterTable'] if q['ID'].endswith('N0')]
        for q in args.writer.objects['ParameterTable']:
            q['Is_Timeframe_Comment'] = q['ID'] in tfids
        for name, mentioned in respondents.items():
            if mentioned or (name in editors.values()):
                args.writer.objects['contributors.csv'].append(dict(
                    ID=contributor_id(name),
                    Name=name,
                    Editor=name in editors.values(),
                ))
        for k in sorted(rationales):
            if not rationales_linked[k]:
                args.log.warning('Rationale {} not linked'.format(k))

    def schema(self, cldf):
        cldf.add_table(
            'contributors.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            },
            {
                "name": "Name",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#name",
            },
            {
                "name": "Editor",
                "datatype": {"base": "boolean", "format": "Yes|No"}
            }
        )

        cldf.add_component('MediaTable')
        cldf.add_columns(
            'ValueTable',
            {
                "name": "Contactset_ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#contributionReference",
                "dc:description": "Link to the corresponding contact set."
            },
            'Respondent')  # The expert who filled out the questionnaire. There may be more than one person per set.
        cldf['ValueTable'].common_props['dc:description'] = \
            ("The *ValueTable* lists answers to the questions in the GramAdapt questionnaire coded "
             "as values for the Focus group language (except for values for the two 'synthetic' "
             "parameters 'Focus language' and 'Contact pair', which may also be coded for the "
             "language of the Neighbour group).")

        t = cldf.add_component(
            'LanguageTable',
        )
        t.common_props['dc:description'] = \
            ("The GramAdapt dataset is constructed around *contact sets*, pairs of *Focus* and"
             "*Neighbour* language communities. This table lists the languages spoken by either "
             "of these communities.")
        t = cldf.add_component(
            'ContributionTable',
            {
                "name": "Type",
                "datatype": {"base": "string", "format": "contactset|rationale"},
            },
            {
                "name": "Focus_Language_ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#languageReference",
                "dc:description": "Link to the language spoken by the focus group in a contact set."
            },
            {
                'name': 'Neighbour_Language_ID',
                "dc:description":
                    "Link to the language spoken by the neighbour group in a contact set."
            },
            {
                'name': 'Author_IDs',
                'separator': ' ',
            },
            {
                'name': 'Reviewer_IDs',
                'separator': ' ',
                'dc:description': 'The GramAdapt team members responsible for checking the responses.'
            },
            {
                'name': 'Area',
                'dc:description':
                    'Information about the geographical location of each contact set based on'
                    ' Autotyp areal classification',
            },
            {
                "name": "Document",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#mediaReference",
                "dc:description": "Link to rendered Markdown document.",
            },
            {
                "name": "Source",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                "separator": ";",
            }
        )
        t.common_props['dc:description'] = \
            ("The GramAdapt dataset provides two types of contributions: "
             "(1) 'contact sets', i.e. descriptions of a contact situation between two "
             "neighbouring communities speaking different languages. Each contact set is unique in "
             "terms of the timeframe they respond for. We urge researchers who use this dataset to "
             "read the Comments column for questions CID P1, P2, and P3 carefully for each set, to "
             "get a sense of the heterogeneity of timeframes represented in each set, as well as "
             "the whole dataset. "
             "(2) 'rationales' explaning the goals, definitions and theoretical support for (sets "
             "of) questions in the GramAdapt questionnaire.")
        cldf['ContributionTable', 'ID'].common_props['dc:description'] = \
            ("(1) For contact sets: The unique identifier of a contact pair. The two digit IDs "
             "were assigned based on order of completion. Sets that are linked by language "
             "communities, but represent different time slices, contain a Roman alphabet symbol, "
             "i.e. Set06a and Set06b are for the contact scenario between Maltese and Sicilian, "
             "but for different time periods of contact. "
             "(2) For rationales the identifier are based on domain and question number.")
        cldf['ContributionTable', 'Description'].common_props.update({
            "dc:format": "text/markdown",
            "dc:conformsTo": "CLDF Markdown",
            "dc:description": "The rationale document formatted as CLDF Markdown.",
        })
        cldf.add_foreign_key('ContributionTable', 'Neighbour_Language_ID', 'LanguageTable', 'ID')
        cldf.add_foreign_key('ContributionTable', 'Reviewer_IDs', 'contributors.csv', 'ID')
        cldf.add_foreign_key('ContributionTable', 'Author_IDs', 'contributors.csv', 'ID')
        t = cldf.add_table(
            'questions.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            },
            {
                "name": "Name",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#name",
            },
            {
                "name": "Rationale",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#contributionReference",
                "dc:description": "Link to the rationale for this question.",
                "separator": " ",
            }
        )
        t.common_props['dc:description'] = \
            ("This table lists the questions of the GramAdapt questionnaire with links to the "
             "respective rationale.")
        t = cldf.add_component(
            'ParameterTable',
            {
                'name': 'datatype',
                'datatype': {'base': 'string', 'format': 'Binary-YesNo|Comment|Scalar|Types|TypesSequential|TypesMultiple|Value'},
                'dc:description':
                    "**Binary-YesNo**: A binary answer of either ‘Yes’ or ‘No;\n"
                    "**Comment**: Not preset, just a comment field, i.e. free response.\n"
                    "**Scalar**: A Likert 5 point scale. The response is in textual form, but represents ordinals on a "
                    "scale of 1-5 (e.g. “Neither positive nor negative” -> 3).\n"
                    "**Types**: A list of preset answers where only one can be chosen (e.g. “FL, NL, Some other "
                    "language, This is highly contextual”)\n"
                    "**TypesSequential**: A list of ordered, categorical answers where only one can be chosen\n"
                    "**Types-Multiple**: A list of preset answers, where multiple can be chosen\n"
                    "**Value**: A numerical value"
            },
            {
                'name': 'Question_ID',
                'dc:description': 'Links to the corresponding GramAdapt question.',
            },
            {
                'name': 'Domain',
                'dc:description':
                    'Indicating the domain to which the responses apply. Possible options are the '
                    'overview questionnaire (**OV**) and social domains (**DEM** = Exchange and Marriage; '
                    '**DFK** = Family and Kin; **DKN** = Knowledge; **DLB** = Labour; **DLC** = Local Community; '
                    '**DTR** = Trade).',
                'datatype': {'base': 'string', 'format': 'OV|DEM|DFK|DKN|DLB|DLC|DTR'}
            },
            {
                'name': 'Tag',
                'dc:description':
                    'Questions of the overview questionnaire may be tagged as {}. '
                    'Questions of the domains questionnaire may be tagged as {}.'.format(
                        '; '.join('**{}** = {}'.format(k, v) for k, v in TAGS.items() if len(k) == 2),
                        '; '.join('**{}** = {}'.format(k, v) for k, v in TAGS.items() if len(k) != 2),
                    ),
                'datatype': {'base': 'string', 'format': '|'.join(TAGS)},
            },
            {
                'name': 'Is_Timeframe_Comment',
                'dc:description': 'Flag signaling whether answers to this question describe a timeframe.',
                'datatype': {'base': 'boolean', 'format': 'yes|no'},
            },
            *[{
                'name': k.replace(' ', '_'),
                'dc:description': v,
                'datatype': {'base': 'boolean', 'format': 'yes|no'}
            } for k, v in MULTICAUSAL_FACTORS.items()],
        )
        t.common_props['dc:description'] = \
            ("Questions in GramAdapt may be broken up into several sub-questions. This table lists "
             "the atomic sub-questions.")
        cldf.add_foreign_key('ParameterTable', 'Question_ID', 'questions.csv', 'ID')
        cldf.add_component(
            'CodeTable',
            {
                'name': 'Ordinal',
                'datatype': {'base': 'integer', 'minimum': 1, 'maximum': 5},
                'dc:description': 'Ordinal, representing the value for a Scalar parameter on a 5 point Likert scale.'
            }
        )

    @contextlib.contextmanager
    def plot_data(self, name, fmt='svg'):
        name = pathlib.Path(name).stem
        try:
            yield self.cldf_reader()
        finally:
            plt.savefig(str(self.etc_dir / '{}.{}'.format(name, fmt)))
            plt.show()
