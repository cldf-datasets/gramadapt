import pathlib
import collections

from clldutils.misc import slug
from csvw.dsv import Dialect
from cldfbench import Dataset as BaseDataset, CLDFSpec

LCODES = {
    'ieu': 'mexi1248',
}


def norm_answer(s, opts=None, dt=''):
    if s.strip() == 'NA':
        return None
    if s.startswith('q2o1answer'):
        s = '[' + s
    if s == 'Published materials by other researchers in other fields':
        s = 'Published materials by researchers in other fields'
    if 'Impressions from my own fieldwork with a related community' in s:
        s = s.replace(
            'Impressions from my own fieldwork with a related community',
            'Impressions from my own fieldwork with the exact or related community')
    if opts:
        if dt.endswith('Multiple'):
            res = []
            for opt in opts:
                if opt in s:
                    res.append(opt)
                    s = s.replace(opt, '').strip()
            assert not s
            return res

        for opt in opts:
            if s == opt:
                return opt
            if slug(s) == slug(opt):
                return opt
        return s
    return s


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gramadapt"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        self.raw_dir.xlsx2csv('QN_V1.0.0_Template.xlsx')
        self.raw_dir.xlsx2csv('set28_45a_V1.0.0.xlsx')

    def cmd_makecldf(self, args):
        glangs = {}
        for l in args.glottolog.api.languoids():
            glangs[l.id] = l
            if l.iso:
                glangs[l.iso] = l
        args.writer.cldf.add_component(
            'LanguageTable',
        )
        args.writer.cldf.add_table(
            'contactpairs.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            },
            {
                "name": "Focus_Language_ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#languageReference",
            },
            'Neighbour_Language_ID',
            'Area',
        )
        args.writer.cldf.add_foreign_key('contactpairs.csv', 'Neighbour_Language_ID', 'LanguageTable', 'ID')

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
        args.writer.objects['ParameterTable'].append(dict(
            ID='S',
            Name='Contact pair',
        ))

        for d in self.raw_dir.read_csv('QN_SetMetadata.Sheet1QNSetMetadata.csv', dicts=True, dialect=Dialect(skipRows=1)):
            if d['FLang'] == 'FLNA':
                continue
            args.writer.objects['CodeTable'].append(dict(
                ID='S-{}'.format(d['Set']),
                Parameter_ID='S',
                Name=d['Set'],
            ))
            for ltype in ['F', 'N']:
                glang = glangs[LCODES.get(d[ltype + 'ISO'], d[ltype + 'ISO'])]
                args.writer.objects['LanguageTable'].append(dict(
                    ID='{}-{}'.format(d['Set'], ltype),
                    Name=d[ltype + 'Lang'],
                    Glottocode=glang.id,
                    Latitude=glang.latitude,
                    Longitude=glang.longitude,
                    Macroarea=glang.macroareas[0].name if glang.macroareas else None,
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='F-{}-{}'.format(d['Set'], ltype),
                    Language_ID='{}-{}'.format(d['Set'], ltype),
                    Parameter_ID='F',
                    Code_ID='F-yes' if ltype == 'F' else 'F-no',
                    Value='Yes' if ltype == 'F' else 'No',
                ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='S-{}-{}'.format(d['Set'], ltype),
                    Language_ID='{}-{}'.format(d['Set'], ltype),
                    Parameter_ID='S',
                    Code_ID='S-{}'.format(d['Set']),
                    Value=d['Set'],
                ))
            args.writer.objects['contactpairs.csv'].append(dict(
                ID=d['Set'],
                Focus_Language_ID='{}-F'.format(d['Set']),
                Neighbour_Language_ID='{}-N'.format(d['Set']),
                Area=d['AArea'],
            ))
        args.writer.cldf.add_table(
            'questions.csv',
            {
                "name": "ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
            }
        )
        args.writer.cldf.add_component('ParameterTable', 'datatype', 'Question_ID')
        args.writer.cldf.add_foreign_key('ParameterTable', 'Question_ID', 'questions.csv', 'ID')
        args.writer.cldf.add_component('CodeTable')

        domains = collections.defaultdict(dict)
        qids = set()
        #Version, Set, Old_Set_ID, CID, QID, Sub-ID, Wording, Response, Comment, Respondent, Dom, DomOrder, DataType, Answer1, Answer2, Answer3, Answer4, Answer5, Answer6, Answer7, Answer8, Surname,
        # [q2o1answer], FLang, F_ISO, [q2o2answer], NLang, N_ISO, ContactPair, ContactPair_ISO, AArea, Reviewer
        for d in self.raw_dir.read_csv('QN_V1.0.0_Template.set51.csv', dicts=True):
            if not d['QID']:
                continue
            pid = d['Sub-ID'] or d['QID']

            if d['QID'] not in qids:
                args.writer.objects['questions.csv'].append(dict(ID=d['QID']))
                qids.add(d['QID'])
            args.writer.objects['ParameterTable'].append(dict(
                ID=pid,
                Name=d['Wording'],
                Question_ID=d['QID'],
                datatype=d['DataType'],
            ))
            if d['DataType'] in ['Scalar', 'Types', 'TypesMultiple']:
                for i in range(1, 9):
                    res = norm_answer(d['Answer{}'.format(i)])
                    if res is not None:
                        if pid == 'DFK39':
                            res = res.replace('q2o2answer', '-----')
                            res = res.replace('q2o1answer', 'q2o2answer')
                            res = res.replace('-----', 'q2o1answer')
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

        for d in self.raw_dir.read_csv('set28_45a_V1.0.0.set51.csv', dicts=True):
            if not d['QID']:
                continue
            pid = d['Sub-ID'] or d['QID']
            res = norm_answer(d['Response'], domains.get(pid), d['DataType'])
            if res is None:
                continue
            if isinstance(res, list):
                assert d['DataType'].endswith('Multiple')
            if pid in domains:
                for i, rr in enumerate(res if isinstance(res, list) else [res], start=1):
                    args.writer.objects['ValueTable'].append(dict(
                        ID='{}-{}-{}'.format('set28', pid, i) if d['DataType'].endswith('Multiple') else '{}-{}'.format('set28', pid),
                        Code_ID=domains[pid][rr],
                        Parameter_ID=pid,
                        Language_ID='set28-F',
                        Value=rr,
                    ))
            else:
                args.writer.objects['ValueTable'].append(dict(
                    ID='{}-{}'.format('set28', pid),
                    Code_ID=None,
                    Parameter_ID=pid,
                    Language_ID='set28-F',
                    Value=res,
                ))
