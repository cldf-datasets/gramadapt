# Releasing GramAdapt

```shell
cldfbench makecldf cldfbench_gramadapt.py --glottolog-version v5.0 --with-zenodo --with-cldfreadme
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


Multi-sub-question questions (describe in Data Records):
```sql
sqlite> select q.cldf_id, count(p.cldf_id) as n from `questions.csv` as q join parametertable as p on p.question_id = q.cldf_id group by q.cldf_id having n > 1 order by n desc;
DTR03|9
DLC25|9
DLB03|9
DKN03|9
DEM03|9
OL2|7
DTR02|6
OI1|5
DFK04|5
DEM27|5
DEM26|5
DTR27|4
DLC03|4
DLB21|4
DKN23|4
DEM39|4
DEM30|4
DEM29|4
DFK38|3
DFK02|3
DEM37|3
DEM28|3
DEM02|3
DEM31|2
```

Technical Validation:



Demonstrate suitability of Likert-scaled questions by value distributions?
```sql
sqlite>  select p.cldf_id, c.ordinal, count(v.cldf_id) from valuetable as v join codetable as c on c.cldf_id = v.cldf_codeReference join parametertable as p on p.cldf_id = v.cldf_parameterreference  where p.datatype = 'Scalar' and c.ordinal is not null group by p.cldf_id, c.ordinal order by p.cldf_id, c.ordinal;
```
Likert scale items that have no values:
```sql
sqlite> select p.cldf_id, c.ordinal from codetable as c, parametertable as p where p.cldf_id = c.cldf_parameterreference and c.ordinal is not null and not exists(select cldf_id from valuetable where cldf_codereference = c.cldf_id);
```

Usage:
Collecting related parameters for time-range questions:
```sql
sqlite> with trquestions as (select distinct q.cldf_id from "questions.csv" as q join parametertable as p on p.question_id = q.cldf_id where p.datatype = 'Value') select cldf_id, cldf_name from parametertable where question_id in trquestions order by question_id, cldf_id;
```

Collecting related values for time-range questions:
```sql
sqlite> select v.cldf_contributionReference, s.cldf_value, e.cldf_value, v.cldf_value from valuetable as v, valuetable as s, valuetable as e where v.cldf_parameterReference = 'DEM0a' and
 s.cldf_parameterReference = 'DEM0aN0' and e.cldf_parameterReference = 'DEM0aN1' and v.cldf_contributionReference = s.cldf_contributionReference and s.cldf_contributionReference = e.cldf_contributionReference;
set01|1000|2020|Around one millennium
set02|1020|2020|1000 years.
set05|1890|2020|IF exchange has occurred, it would have started no earlier than 1860 when Papapana ancestors were part of a migration from the south. Most likely, exchange would have started after 1894 when Papapana speakers finally settled in their contemporary location. Papapana and Rotokas speakers still practice exchange in the current day.
set06a|1300|2020|Since prehistory, documented since the 14th century.
set07|1839|2020|For a very long period of time, i.e., after they were resettled from Hwange national part.
set08|1820|2020|Two centuries up to the present but only in the context of trade and ritual matters, never in the form of intermarriage.
set09|1200|2020|Probably 800 years or so, since Tabelbala was founded; there's really no way to know
set12|1000|2020|It is difficult to say. Please see my comment on § 2 in KN [QID: DKN0a]
set13|1520|2020|Likely, several hundred years.
set14|1950|2020|1950-2020
set17|1950|2020|Approximately since 1950.
set18|1600|2020|For at least the last few hundred years, more likely a thousand years.
set21|1000|2020|Probably for the past 1000 years
set22|1990|2020|It is not frequent, but there are at least a few people in each village married to a Tai Lue person, and there are people who have married and moved to Tai Lue  villages. However, based on what my language informants are aware of, it seems to be a recent occurrence- beginning with people now in their 40's or 50's.
set24|1880|2020|Since the end of the XIX century and the beginning of the XX.
Contact is presently ongoing.
set25|0|2020|Western Toba and Wichí people practised exchange since they met one another. Neverthless, we have historical information since the 19th Century.
set28|1800|2020|The Williams ethnography has data from 1920, and six generations will have been claimed from then. So if we say each generation is about 20 years, then contact has been ongoing since at least 1800. But I imagine contact has been ongoing for much longer than that.
set29|1500|2020|For many hundreds of years, certainly stretching back a significant period of time prior to colonisation in the late 18th century.
set30|1000|2020|At least since the year 1000, that is, for more than 1000 years.
```

As mentioned in the "Particularities of this dataset" section, each contact set is unique in terms of the timeframe they respond for.
We urge researchers who use this dataset to read the Comments column for questions CID P1, P2, and P3 carefully for each set, 
to get a sense of the heterogeneity of timeframes represented in each set, as well as the whole dataset.

The timeframes given in CIDs P2N and P3N are broad and coarse approximations, often negotiated between the respondent and reviewer. 
These timeframes are to be used with caution. Always read the associated comments in the Comment column.

An end date >= 2020 indicates that social contact is ongoing at the time of data collection in 2021. 

Comments column for questions CID P1, P2, and P3:
```sql
sqlite> select p.cldf_name, v.cldf_value, v.cldf_comment from 
    valuetable as v 
        join 
    parametertable as p 
    on v.cldf_parameterreference = p.cldf_id 
        join 
    "questions.csv" as q 
    on q.cldf_id = p.question_id 
        where q.cldf_contributionReference = 'P3' and 
            v.cldf_contributionReference = 'set01' and 
            p.datatype = 'Comment' and 
            v.cldf_value is not null;
```
