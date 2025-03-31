import collections


def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)
    contribs = collections.Counter([r['Type'] for r in cldf_dataset['ContributionTable']])
    assert contribs['contactset'] == 35 and contribs['rationale'] == 90
