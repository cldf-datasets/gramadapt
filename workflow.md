# Converting GramAdapt questionnaires to CLDF

This repository is structured in a way that allows converting GramAdapt questionnaires to CLDF with the help of
the [cldfbench software](https://github.com/cldf/cldfbench/blob/master/README.md).


## Repository layout

- The excel sheets containing the questionnaire data as collected go into [raw/](raw/).
- Additional metadata such as the set metadata sheet goes into [raw/](raw/), too.
- The CLDF output will be created in [cldf/](cldf/) - so nothing in this directory should be edited "by hand", 
  because such changes will be oveerwritten the next time the conversion process is run.
- The Python code that implements the GramAdapt-specific parts of the CLDF conversion is at [cldfbench_gramadapt.py](cldfbench_gramadapt.py).


## Conversion requirements

The CLDF conversion is run locally on the maintainer's machine, which requires a [local clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
of this repository.

Since the CLDF conversion is driven by `cldfbench`, this package must be installed prior to running the conversion.
This should be done
- within a dedicated [virtual environment](https://docs.python.org/3/tutorial/venv.html)
- running `pip install -e .` at the root of the repository clone (this will use the information about dependencies in
  [setup.py](https://github.com/cldf-datasets/gramadapt/blob/1616b98dea1727113e5972ec3dba0b9ddfdede7f/setup.py#L14-L21).

Installing `cldfbench` will also install a commandline tool `cldfbench` which is used to run the conversion. Running
`cldfbench -h` shows a list of available subcommands (only a few of them are rewuired here, see below).

Since `cldfbench` will lookup language metadata in Glottolog data, we also need a clone of the [glottolog/glottolog repository](https://github.com/glottolog/glottolog)
and the `pyglottolog` package (to be installed via `pip install pyglottolog`).


## Conversion overview

`cldfbench` supports a two-step conversion workflow, implemented as two commandlind commands
- `cldfbench download`: Many `cldfbench`-curated datasets use this to actually download raw data (hence the name). Here, we repurpose the command
  to [extract CSV data from the Excel sheets](https://github.com/cldf-datasets/gramadapt/blob/1616b98dea1727113e5972ec3dba0b9ddfdede7f/cldfbench_gramadapt.py#L50-L52) for simpler access later
- `cldfbench makecldf` runs the actual conversion to CLDF, see [the implementation](https://github.com/cldf-datasets/gramadapt/blob/1616b98dea1727113e5972ec3dba0b9ddfdede7f/cldfbench_gramadapt.py#L54-L192)

A couple more `cldfbench` subcommands are used to convert metadata into various formats for various purposes:
- `cldfbench zenodo` will create metadata that is picked up by Zenodo when pushing a release there for archiving
- `cldfbench cldfreadme` will create a (more) human readable of the CLDF metadata in [cldf/README.md](cldf/README.md)
- `cldfbench readme` will create a landing page for the repository at README.md


## Conversion walk-through

Typically, conversion would be triggered by new data.

1. Put new questionaires in `raw/`, ideally using a naming convention for files that allows addressing
   them via `.glob()` so that rewriting code in `cldfbench_gramadapt.py` is not necessary.
2. Extract data from excel sheets:
   ```shell
   cldfbench download cldfbench_gramadapt.py
   ```
3. Recreate the CLDF data:
   ```shell
   cldfbench makecldf cldfbench_gramadapt.py --glottolog-version v5.0 --glottolog PATH/TO/CLONE/OF/glottolog/glottolog
   ```
4. Validate the output:
   ```shell
   pytest
   ```
5. Inspect whether the changes are reasonable:
   ```shell
   git diff -b cldf
   ```
6. Commit and push changes.


## Visualization

Create a map showing the GramAdapt contact pairs running (requires `pip install cldfviz`):
```shell
cldfbench cldfviz.map cldf --parameters F,S --colormaps '{"Yes":"circle","No":"diamond"},tol' --output map.svg --language-labels --markersize 7 --format svg --width 20 --pacific-centered --with-ocean --no-legend --padding-top 3 --padding-bottom 3
```
