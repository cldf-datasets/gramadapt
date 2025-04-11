# Releasing GramAdapt

Recreate the CLDF data from the raw data
```shell
cldfbench makecldf cldfbench_gramadapt.py --glottolog-version v5.1 --with-cldfreadme
```
and make sure it's valid
```shell
pytest
cldf validate --with-cldf-markdown cldf
```

Recreate the README and the rendered rationales:
```shell
cldfbench readme cldfbench_gramadapt.py
```

Recreate metadata for Zenodo:
```shell
cldfbench zenodo cldfbench_gramadapt.py --communities "gramadapt,cldf-datasets"
```

Recreate the SQLite database:
```shell
rm gramadapt.sqlite
cldf createdb cldf gramadapt.sqlite
```

Recreate the ERD of the database schema:
```shell
cldferd --format compact.svg cldf > erd.svg
```

Create a map showing the GramAdapt contact pairs running (requires `pip install cldfviz[cartopy]`):
```shell
cldfbench cldfviz.map cldf --parameters F,S --colormaps '{"Yes":"circle","No":"diamond"},tol' --output map.svg --language-labels --markersize 5 --format svg --width 20 --pacific-centered --with-ocean --no-legend --padding-top 10 --padding-bottom 12
```

Create plots to show the overall applicability of the questionnaire for the contact sets (see [VALIDATION.md](VALIDATION.md)).
```shell
cldfbench gramadapt.binaryvalidity
cldfbench gramadapt.categoricalvalidity
cldfbench gramadapt.likertvalidity
```
