import pathlib
import itertools
import collections

from clldutils.misc import slug
from cldfbench import Dataset as BaseDataset, CLDFSpec


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


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gramadapt"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):  # called from "cldfbench download"
        self.raw_dir.xlsx2csv('QN_V1.0.0_Template.xlsx')
        self.raw_dir.xlsx2csv('set28_45a_V1.0.0.xlsx')

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
                Area=d['AArea'],
                #
                # Add respondent, reviewers? FIXME: add q202answer, etc.
                #
            ))

        rationales = {p.stem: p for p in self.dir.joinpath('rationale').glob('*.md')}
        mr = collections.Counter()

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
            pid = subid or qid

            rows = list(rows)

            for col in ['Wording'] + ['Answer{}'.format(i + 1) for i in range(8)]:
                norm(rows, col)

            vals[pid].update([r['Response'] for r in rows])

            d = rows[0]
            cid = d['CID']

            #
            # FIXME: CID is the link to rationale docs!
            #
            cid = rationales.get(cid)
            if not cid:
                cid = rationales.get('{}_{}'.format(cid, pid))
                if not cid:
                    #'missing rationale: {}'.format(d['CID'])
                    mr.update([cid])

            if qid not in qids:
                args.writer.objects['questions.csv'].append(dict(ID=qid))
                qids.add(qid)
            args.writer.objects['ParameterTable'].append(dict(
                ID=pid,
                Name=d['Wording'],
                Question_ID=qid,
                datatype=d['DataType'],
            ))
            #
            # FIXME: add response "B" as code for all questions with domains!
            # B: for “blank”. The question is relevant to the domain in question, but the respondent chose not to answer the question.
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
        for k, v in mr.most_common():
            print(k, v)
        return


    def schema(self, cldf):
        # Extend the data schema:
        # -----------------------
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
            'Area',
        )
        cldf.add_foreign_key('ContributionTable', 'Neighbour_Language_ID', 'LanguageTable', 'ID')
        cldf.add_table(
            'questions.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            }
        )
        cldf.add_component('ParameterTable', 'datatype', 'Question_ID')
        cldf.add_foreign_key('ParameterTable', 'Question_ID', 'questions.csv', 'ID')
        cldf.add_component('CodeTable')
