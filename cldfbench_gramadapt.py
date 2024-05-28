import pathlib
import itertools
import collections

from clldutils.misc import slug
from clldutils.markup import add_markdown_text
from cldfbench import Dataset as BaseDataset, CLDFSpec
from cldfbench.metadata import get_creators_and_contributors

#
# FIXME: integrate bib!
#
NOTES = """
## Contact pairs

![](map.svg)


## Data model

![](erd.svg)
"""


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
    return s


def norm(rows, col):
    counts = collections.Counter([row[col] for row in rows])
    selected = counts.most_common(1)[0][0]
    for row in rows:
        if row[col] != selected:
            row[col] = selected


mr = collections.defaultdict(set)

def get_rationale(rationales, cid, qid, subid):
    """
    No rationales:
    - E6 is a comment box question so no need for a rationale
    - E1, 2, 3: No rationales.
    - C1 - 6: No rationales.

    P2, P2N and P3, P3N: I'm guessing P2 is P2Begin and P2N is P2End.
    These questions should be linked to a P2 rationale.
    """
    if cid in {'OE1', 'OE2', 'OE3', 'E6', 'OC1', 'OC2', 'OC3', 'OC4', 'OC5', 'OC6'}:
        return None
    # We must lookup more specific rationale first!
    for key, p in rationales.items():
        ccid, _, spec = key.partition('_')
        if ccid == cid and qid in spec:
            return p
    if cid in rationales:
        return rationales[cid]
    if cid.endswith('N') and cid[:-1] in rationales:
        return rationales[cid[:-1]]
    res = rationales.get('{}_{}'.format(cid, qid))
    if res:
        return res
    # 'missing rationale: {}'.format(d['CID'])
    mr[cid].add((qid, subid))
    return None


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gramadapt"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):  # called from "cldfbench download"
        self.raw_dir.xlsx2csv('QN_V1.0.0_Template.xlsx')
        self.raw_dir.xlsx2csv('set28_45a_V1.0.0.xlsx')

    def cmd_readme(self, args):
        return add_markdown_text(BaseDataset.cmd_readme(self, args), NOTES, section='Description')

    def cmd_makecldf(self, args):  # called from "cldfbench makecldf"
        self.schema(args.writer.cldf)
        glangs = {l.id: l for l in args.glottolog.api.languoids()}

        # We add two "synthetic" parameters which can later be used to plot contact pairs on a map.
        args.writer.objects['ParameterTable'].append(dict(
            ID='F',
            Name='Focus language',
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
        ))

        editors = {
            c['id']: c['name'] for c in get_creators_and_contributors(
                self.dir.joinpath('CONTRIBUTORS.md').read_text(encoding='utf8'))[0] if c['id']}

        # Add language metadata: GA_V1.0.0_Metadata.csv
        # SetID, Old_SetID, [q2o1answer], F_Lang, F_Glottocode, F_Iso, [q2o2answer], N_Lang, N_Glottocode, N_Iso, ContactPair, ContactPair_Iso, ConcactPair_glottocode, AArea, Surname, Respondents, Reviewer(s)
        for d in self.raw_dir.joinpath('On Zenodo copy').read_csv('GA_V1.0.0_Metadata.csv', dicts=True):
            args.writer.objects['CodeTable'].append(dict(
                ID='S-{}'.format(d['SetID']),
                Parameter_ID='S',
                Name=d['SetID'],
            ))
            for ltype in ['F', 'N']:  # We add both, focus and neighbouring languages to the table.
                glang = glangs.get(d['{}_Glottocode'.format(ltype)])
                args.writer.objects['LanguageTable'].append(dict(
                    ID='{}-{}'.format(d['SetID'], ltype),
                    Name=d[ltype + '_Lang'],
                    Glottocode=glang.id if glang else None,
                    Latitude=glang.latitude if glang else None,
                    Longitude=glang.longitude if glang else None,
                    Macroarea=glang.macroareas[0].name if glang and glang.macroareas else None,
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='F-{}-{}'.format(d['SetID'], ltype),
                    Language_ID='{}-{}'.format(d['SetID'], ltype),
                    Parameter_ID='F',
                    Code_ID='F-yes' if ltype == 'F' else 'F-no',
                    Value='Yes' if ltype == 'F' else 'No',
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='S-{}-{}'.format(d['SetID'], ltype),
                    Language_ID='{}-{}'.format(d['SetID'], ltype),
                    Parameter_ID='S',
                    Code_ID='S-{}'.format(d['SetID']),
                    Value=d['SetID'],
                ))
            args.writer.objects['ContributionTable'].append(dict(
                ID=d['SetID'],
                Name=d['ContactPair'],
                Contributor=d['Respondents'],
                Focus_Language_ID='{}-F'.format(d['SetID']),
                Neighbour_Language_ID='{}-N'.format(d['SetID']),
                Reviewers=[editors[eid.strip()] for eid in d['Reviewer(s)'].split(',')],
                Area=d['AArea'],
                # FIXME: Citation:
                # Kashima, Eri & Schokkin, Dineke. Set28: Nen and Idi.
                # In Eri Kashima, Francesca Di Garbo, Oona Raatikainen, Rosnátaly Avelino, Sacha Beck, Anna Berge, Ana Blanco, Ross Bowden, Nicolás Brid, Joseph M Brincat, María Belén Carpio, Alexander Cobbinah, Paola Cúneo, Anne-Maria Fehn, Saloumeh Gholami, Arun Ghosh, Hannah Gibson, Elizabeth Hall, Katja Hannß, Hannah Haynie, Jerry Jacka, Matias Jenny, Richard Kowalik, Sonal Kulkarni-Joshi, Maarten Mous, Marcela Mendoza, Cristina Messineo, Francesca Moro, Hank Nater, Michelle A Ocasio, Bruno Olsson, Ana María Ospina Bozzi, Agustina Paredes, Admire Phiri, Nicolas Quint, Erika Sandman, Dineke Schokkin, Ruth Singer, Ellen Smith-Dennis, Lameen Souag, Yunus Sulistyono, Yvonne Treis, Matthias Urban, Jill Vaughan, Deginet Wotango Doyiso, Georg Ziegelmeyer, Veronika Zikmundová. (2023).
                # GramAdapt Crosslinguistic Social Contact Dataset. (1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7508054

                #
                # Add respondent, reviewers? FIXME: add q202answer, etc.
                #
            ))

        rationales = {p.stem: p for p in self.dir.joinpath('rationale').glob('*.md')}

        domains = collections.defaultdict(dict)
        qids = set()
        #"Version","Set","Old_Set_ID","CID","QID","Sub.ID","Wording","Response","Comment","Respondent","Dom","DomOrder","DataType","Answer1","Answer2","Answer3","Answer4","Answer5","Answer6","Answer7","Answer8","Surname","X.q2o1answer.","FLang","F_ISO","F_Glottocode","X.q2o2answer.","NLang","N_ISO","N_Glottocode","ContactPair","ContactPair_ISO","ContactPair_Glottocode","AArea","Reviewer"
        # [q2o1answer], FLang, F_ISO, [q2o2answer], NLang, N_ISO, ContactPair, ContactPair_ISO, AArea, Reviewer
        vals = collections.defaultdict(lambda: collections.Counter())
        for (qid, subid), rows in itertools.groupby(
            sorted(
                self.raw_dir.read_csv('V1_0_1.csv', dicts=True),
                key=lambda r: (r['QID'], r['Sub.ID'], r['Set'])
            ),
            lambda r: (r['QID'], r['Sub.ID']),
        ):
            pid = '{}_{}'.format(qid, subid) if subid else qid
            rows = list(rows)
            assert len({r['Dom'] for r in rows}) == 1
            for col in ['Wording'] + ['Answer{}'.format(i + 1) for i in range(8)]:
                norm(rows, col)

            vals[pid].update([r['Response'] for r in rows])
            d = rows[0]
            cid = get_rationale(rationales, d['CID'], qid, subid)

            if qid not in qids:
                args.writer.objects['questions.csv'].append(dict(ID=qid))
                qids.add(qid)
            args.writer.objects['ParameterTable'].append(dict(
                ID=pid,
                Name=d['Wording'],
                Question_ID=qid,
                Description=cid.read_text(encoding='utf8') if cid else None,
                datatype=d['DataType'],
                Domain=d['Dom'],
            ))
            #
            # Add response "B" as code for all questions with domains!
            #
            if d['DataType'] in ['Scalar', 'Types', 'TypesMultiple']:
                for i in range(1, 9):
                    res = norm_answer(d['Answer{}'.format(i)])
                    if res is not None:
                        args.writer.objects['CodeTable'].append(dict(
                            ID='{}-{}'.format(pid, i),
                            Parameter_ID=pid,
                            Name=res,
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

            if pid in domains:
                args.writer.objects['CodeTable'].append(dict(
                    ID='{}-B'.format(pid),
                    Parameter_ID=pid,
                    Name='B',
                    Description='“blank”. The question is relevant to the domain in question, but the respondent chose not to answer the question.',
                ))
                domains[pid]['B'] = '{}-{}'.format(pid, 'B')

            for d in rows:
                res = norm_answer(d['Response'], domains.get(pid), d['DataType'])
                if res is None:
                    # FIXME: sometimes NA responses have useful comments. Keep!
                    args.writer.objects['ValueTable'].append(dict(
                        ID='{}-{}'.format(d['Set'], pid),
                        Code_ID=None,
                        Parameter_ID=pid,
                        Language_ID='{}-F'.format(d['Set']),
                        Value=None,
                        Comment=d['Comment'],
                    ))
                    continue
                if pid in domains:
                    for i, rr in enumerate(res if isinstance(res, list) else [res], start=1):
                        args.writer.objects['ValueTable'].append(dict(
                            ID='{}-{}-{}'.format(d['Set'], pid, i) if d['DataType'].endswith('Multiple') else '{}-{}'.format(d['Set'], pid),
                            Code_ID=domains[pid][rr],
                            Parameter_ID=pid,
                            Language_ID='{}-F'.format(d['Set']),
                            Value=rr,
                            Comment=d['Comment'],
                        ))
                else:
                    args.writer.objects['ValueTable'].append(dict(
                        ID='{}-{}'.format(d['Set'], pid),
                        Code_ID=None,
                        Parameter_ID=pid,
                        Language_ID='{}-F'.format(d['Set']),
                        Value=res,
                        Comment=d['Comment'],
                    ))

        return
        for k, v in sorted(mr.items()):
            print(k)
            for vv in v:
                print(vv)
            print('---')
        return


    def schema(self, cldf):
        # Extend the data schema:
        # -----------------------

        cldf.add_columns(
            'ValueTable',
            'Respondent')

        cldf.add_component(
            'LanguageTable',
        )
        t = cldf.add_component(
            'ContributionTable',
            {
                "name": "Focus_Language_ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#languageReference",
            },
            'Neighbour_Language_ID',
            {
                'name': 'Reviewers',
                'separator': ' & ',
                'dc:description': 'The GramAdapt team members responsible for checking the responses.'
            },
            {
                'name': 'Area',
                'dc:description': 'Information about the geographical location of each contact set based on Autotyp areal classification',
            }
        )
        t.common_props['dc:description'] = \
            ("Contributions in GramAdapt are 'contact sets', i.e. descriptions of a contact "
             "situation between two neighbouring languages. Each contact set is unique in terms of "
             "the timeframe they respond for. We urge researchers who use this dataset to read the "
             "Comments column for questions CID P1, P2, and P3 carefully for each set, to get a "
             "sense of the heterogeneity of timeframes represented in each set, as well as the "
             "whole dataset.")
        cldf['ContributionTable', 'ID'].common_props['dc:description'] = \
            ("The unique identifier of a contact pair. The two digit IDs were assigned based on "
             "order of completion. Sets that are linked by language communities, but represent "
             "different time slices, contain a Roman alphabet symbol, i.e. Set06a and Set06b are "
             "for the contact scenario between Maltese and Sicilian, but for different time "
             "periods of contact.")
        cldf.add_foreign_key('ContributionTable', 'Neighbour_Language_ID', 'LanguageTable', 'ID')
        cldf.add_table(
            'questions.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            }
        )
        cldf.add_component(
            'ParameterTable',
            'datatype',
            'Question_ID',
            {
                'name': 'Domain',
                'dc:description':
                    'Indicating the domain to which the responses apply. Possible options are the '
                    'overview questionnaire (OV) and social domains (DEM = Exchange and Marriage; '
                    'DFK = Family and Kin; DKN = Knowledge; DLB = Labour; DLC = Local Community; '
                    'DTR = Trade).',
                'datatype': {'base': 'string', 'format': 'OV|DEM|DFK|DKN|DLB|DLC|DTR'}
            }
        )
        cldf.add_foreign_key('ParameterTable', 'Question_ID', 'questions.csv', 'ID')
        cldf.add_component('CodeTable')
