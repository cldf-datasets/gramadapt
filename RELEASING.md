# Releasing GramAdapt

```shell
cldfbench makecldf cldfbench_gramadapt.py --glottolog-version v5.1 --with-zenodo --with-cldfreadme
pytest
```

```shell
cldfbench readme cldfbench_gramadapt.py
```

```shell
rm gramadapt.sqlite
cldf createdb cldf gramadapt.sqlite
```

```shell
cldferd --format compact.svg cldf > erd.svg
```

Create a map showing the GramAdapt contact pairs running (requires `pip install cldfviz[cartopy]`):
```shell
cldfbench cldfviz.map cldf --parameters F,S --colormaps '{"Yes":"circle","No":"diamond"},tol' --output map.svg --language-labels --markersize 7 --format svg --width 20 --pacific-centered --with-ocean --no-legend --padding-top 3 --padding-bottom 3
```

Create plots to show the overall applicability of the questionnaire for the contact sets.
```shell
cldfbench gramadapt.binaryvalidity
cldfbench gramadapt.categoricalvalidity
cldfbench gramadapt.likertvalidity
```
