# Using the GramAdapt dataset

Using the GramAdapt data quantitatively is not straightforward due to its inhomogeneous nature: Some
questions have binary "yes" or "no" answers, others have answers on a Likert scale, and some have
textual answers. In addition, some questions are sub-questions, or logically dependent questions
meaning they cannot simply be treated in isolation.

But since the GramAdapt data is available in a format that is amenable to computational re-use,
exploratory analysis is easy and we can programmatically detect the issues outlined above and 
extract meaningful sets of data in an informed way.

The GramAdapt dataset follows the principles of "tidy data", putting each type of data into a
separate table. Exploring multi-table data is particularly easy via SQL and since every CLDF dataset
can be converted to a SQLite database automatically, we start our exploration doing that:
```shell
cldf createdb cldf/ gramadapt.sqlite
```

The schema of the resulting database looks as follows
![](erd.svg)

The database can now be queried, for example using [`sqlite3` - the command line shell for SQLite](https://www.sqlite.org/cli.html).
In the following we will describe queries by giving the SQL code of the query, followed by a
table listing the results. `sqlite3` can be used to run the query either by interactively providing the
SQL
```shell
$ sqlite3 gramadapt.sqlite 
SQLite version 3.45.1 2024-01-30 16:01:20
Enter ".help" for usage hints.
sqlite> select count(*) from valuetable;
13097
```
or by providing the SQL as [input](https://swcarpentry.github.io/shell-novice/04-pipefilter.html) for
`sqlite3`:
```shell
$ echo "select count(*) as nvalues from valuetable" | sqlite3 -header gramadapt.sqlite 
nvalues
13097
```
possibly from a file:
```shell
$ sqlite3 gramadapt.sqlite < query.sql 
13097
```


## Datatypes

GramAdapt contains questions with responses of the following datatypes:

- `Binary-YesNo`: A binary answer of either `Yes` or `No` (or `B`, see below).
- `Comment`: Not preset, just a comment field, i.e. free response.
- `Scalar`: A Likert 5 point scale. The response is in textual form, but can be numeracised on a scale of 1-5 (e.g. “Neither positive nor negative” -> 3).
- `Types`: A list of preset answers where only one can be chosen (e.g. “FL, NL, Some other language, This is highly contextual”)
- `TypesMultiple`: A list of preset answers, where multiple can be chosen
- `Value`: A numerical value

The distribution of datatypes is
```sql
select 
   coalesce(datatype, 'none') as datatype, 
   count(cldf_id) as nquestions 
from parametertable 
group by datatype 
order by nquestions desc;
```

datatype|nquestions
--- | ---:
Binary-YesNo|141
Scalar|112
Types|65
Comment|34
Value|28
TypesMultiple|6
TypesSequential|4
none|2


Except for datatypes `Value` and `Comment`, all valid responses are linked to a "code", i.e. a row in
`CodeTable` (via `cldf_codeReference`). The list of valid responses for such questions can be computed
as shown here for the question with ID `OS7``:
```sql
select cldf_id, cldf_name from codetable where cldf_parameterreference = 'OS7';
```

cldf_id|cldf_name
--- | ---
OS7-1|Fewer than 50 persons
OS7-2|From 50 to 99 persons
OS7-3|From 100 to 199 persons
OS7-4|From 200 to 399 persons
OS7-5|From 400 to 1,000 persons
OS7-6|More than 1,000 persons in the absence of indigenous urban aggregations
OS7-7|One or more indigenous towns of more than 5,000 inhabitants but none of more than 50,000
OS7-B|B


## Missing data

NA responses (“not applicable”) indicate that a question is not applicable for a particular sample set.
NAs only arise in the dataset 
1. if a social domain is assessed as a “no social contact” domain by the respondent, and/or 
2. if a “no” response to questions O1, I1, or T1, renders subsequently dependent questions irrelevant 
   (i.e. a “no” response to O1 means questions O2 and O3 should be skipped.)

NA responses are still recorded in the dataset, marked with an empty `value`:
```sql
sqlite> select count(*) from ValueTable where cldf_value is null;
2865
```

Sometimes NA responses are accompanied by useful comments:
```sql
sqlite> select count(*) from ValueTable where cldf_value is null and cldf_comment is not null;
58
```

A different type of missing data is marked with a `value` of `B` for “blank”, meaning the question is 
relevant to the domain in question, but the respondent chose not to answer the question. This is 
qualitatively different from an NA response. Since `B` responses are allowed for every question, this
means that even "binary" questions have **three** possible answers:
```sql
sqlite> select * from codetable where cldf_parameterReference = 'DEM00';
DEM00-yes|DEM00|Yes||
DEM00-no|DEM00|No||
DEM00-B|DEM00|B|“blank”. The question is relevant to the domain in question, but the respondent chose not to answer the question.|
```


## Sub-questions

"Questions", i.e. rows in `ParameterTable` are grouped together (turning them into "sub-questions") via
the `Question_ID` column. E.g. some sub-questions are variations of the basic question limited to a
specific social domain.

Questions that are grouped with others in this way can be explored using the following SQL:
```sql
select 
   q.cldf_id as QID, 
   count(p.cldf_id) as nsubquestions, 
   q.cldf_name as base_question 
from parametertable as p
join "questions.csv" as q 
     on q.cldf_id = p.question_id 
group by p.question_id having nsubquestions > 1 
order by nsubquestions desc;
```

QID | nsubquestions | base_question
--- |---------------| ---
DTR03| 9             |Involvement in trade
DLC25| 9             |Involvement in the Local Community
DLB03| 9             |Involvement in work
DKN03| 9             |Involvement in the knowledge domain
DEM03| 9             |Social categories
OL2| 7             |Restrictions in access to literacy in terms of social categories
DTR02| 6             |Traded good types
OI1| 5             |Is Focus Group stated as an expression of identity?
DFK04| 5             |Looking after children
DEM27| 5             |Marrying within
DEM26| 5             |Marrying out
DTR27| 4             |Looking after children during trade
DLC03| 4             |Looking after children in the local community
DLB21| 4             |Looking after children during work
DKN23| 4             |Looking after children in the knowledge domain
DEM39| 4             |Child socialisation
DEM30| 4             |Child rearing obligations
OT2| 3             |What is the overall time frame when the largest number of people had the most opportunities for interaction?
OT1| 3             |How long have Focus Group and Neighbour Group people been in contact overall?
DTR0b| 3             |What is the time frame when the largest number of people had the most opportunities for interaction in trade?
DTR0a| 3             |How long have Focus Group and Neighbour Group people traded for?
DLC0b| 3             |What is the time frame when the largest number of people had the most opportunities for interaction in the local community?
DLC0a| 3             |How long have Focus Group and Neighbour Group people been in contact in the local community?
DLB0b| 3             |What is the time frame when the largest number of people had the most opportunities for interaction in the labour domain?
DLB0a| 3             |How long have Focus Group people and Neighbour Group people worked together for?
DKN0b| 3             |What is the time frame when the largest number of people had the most opportunities for interaction in the knowledge domain?
DKN0a| 3             |How long have Focus Group and Neighbour Group people been involved in the knowledge domain together for?
DFK38| 3             |Are any of the following features characteristic when speaking to one’s Neighbour Group in-laws?
DFK0b| 3             |What’s the time frame of densest contact between Focus Group and Neighbour Group as far as family formation is concerned?
DFK0a| 3             |How long have Focus Group and Neighbour Group peoples been forming families with each other for?
DFK02| 3             |Co-residential units
DEM37| 3             |What type of marriage payments and transfers are expected when Focus Group and Neighbour Group marry?
DEM28| 3             |Polygyny
DEM0b| 3             |What is the time frame when the largest number of people had the most opportunities for interaction in exchange?
DEM0a| 3             |How long have Focus Group and Neighbour Group people practised exchange for?
DEM02| 3             |Characteristic of the domain of Exchange
DEM31| 2             |Intermarriage
DEM29| 2             |Polyandry


## Time-range questions

A special type of grouped questions are "time-range questions". Time-range questions are coded as three
sub-questions, two with datatype `Value` specifying start and end year of a time-range, and one with
datatype `Comment` describing the time-range in a textual way.

Collecting related parameters for time-range questions:
```sql
with trquestions as (
    select distinct q.cldf_id 
    from "questions.csv" as q 
    join parametertable as p on p.question_id = q.cldf_id 
    where p.datatype = 'Value'
) 
select cldf_id, cldf_name 
from parametertable 
where question_id in trquestions order by question_id, cldf_id;
```

QID | Question
--- | ---
DEM0a|How long have Focus Group and Neighbour Group people practised exchange for? 
DEM0aN0|Coarse time range, start [DEM0aN]
DEM0aN1|Coarse time range, end [DEM0aN]
DEM0b|What is the time frame when the largest number of people had the most opportunities for interaction in exchange?
DEM0bN0|Coarse time range, start [DEM0bN]
DEM0bN1|Coarse time range, end [DEM0bN]
DFK0a|How long have Focus Group and Neighbour Group peoples been forming families with each other for?
DFK0aN0|Coarse time range, start [DFK0aN]
DFK0aN1|Coarse time range, end [DFK0aN]
DFK0b|What’s the time frame of densest contact between Focus Group and Neighbour Group as far as family formation is concerned?
DFK0bN0|Coarse time range, start [DFK0bN]
DFK0bN1|Coarse time range, end [DFK0bN]
DKN0a|How long have Focus Group and Neighbour Group people been involved in the knowledge domain together for?
DKN0aN0|Coarse time range, start [DKN0aN]
DKN0aN1|Coarse time range, end [DKN0aN]
DKN0b|What is the time frame when the largest number of people had the most opportunities for interaction in the knowledge domain?
DKN0bN0|Coarse time range, start [DKN0bN]
DKN0bN1|Coarse time range, end [DKN0bN]
DLB0a|How long have Focus Group people and Neighbour Group people worked together for?
DLB0aN0|Coarse time range, start [DLB0aN]
DLB0aN1|Coarse time range, end [DLB0aN]
DLB0b|What is the time frame when the largest number of people had the most opportunities for interaction in the labour domain?
DLB0bN0|Coarse time range, start [DLB0bN]
DLB0bN1|Coarse time range, end [DLB0bN]
DLC0a|How long have Focus Group and Neighbour Group people been in contact in the local community?
DLC0aN0|Coarse time range, start [DLC0aN]
DLC0aN1|Coarse time range, end [DLC0aN]
DLC0b|What is the time frame when the largest number of people had the most opportunities for interaction in the local community?
DLC0bN0|Coarse time range, start [DLC0bN]
DLC0bN1|Coarse time range, end [DLC0bN]
DTR0a|How long have Focus Group and Neighbour Group people traded for?
DTR0aN0|Coarse time range, start [DTR0aN]
DTR0aN1|Coarse time range, end [DTR0aN]
DTR0b|What is the time frame when the largest number of people had the most opportunities for interaction in trade?
DTR0bN0|Coarse time range, start [DTR0bN]
DTR0bN1|Coarse time range, end [DTR0bN]
OT1|How long have Focus Group and Neighbour Group people been in contact overall?
OT1N0|Coarse time range, start [OT1N]
OT1N1|Coarse time range, end [OT1N]
OT2|What is the overall time frame when the largest number of people had the most opportunities for interaction?
OT2N0|Coarse time range, start [OT2N]
OT2N1|Coarse time range, end [OT2N]


Collecting related values for time-range questions:
```sql
select 
    v.cldf_contributionReference, s.cldf_value, e.cldf_value, v.cldf_value 
from valuetable as v, valuetable as s, valuetable as e 
where 
    v.cldf_parameterReference = 'DEM0a' and
    s.cldf_parameterReference = 'DEM0aN0' and 
    e.cldf_parameterReference = 'DEM0aN1' and 
    v.cldf_contributionReference = s.cldf_contributionReference and 
    s.cldf_contributionReference = e.cldf_contributionReference;
```

Set | Start | End | Description
--- | ---:| ---:| ---
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
set24|1880|2020|Since the end of the XIX century and the beginning of the XX. Contact is presently ongoing.
set25|0|2020|Western Toba and Wichí people practised exchange since they met one another. Neverthless, we have historical information since the 19th Century.
set28|1800|2020|The Williams ethnography has data from 1920, and six generations will have been claimed from then. So if we say each generation is about 20 years, then contact has been ongoing since at least 1800. But I imagine contact has been ongoing for much longer than that.
set29|1500|2020|For many hundreds of years, certainly stretching back a significant period of time prior to colonisation in the late 18th century.
set30|1000|2020|At least since the year 1000, that is, for more than 1000 years.


As mentioned in the "Particularities of this dataset" section, each contact set is unique in terms of the timeframe they respond for.
We urge researchers who use this dataset to read the Comments column for questions CID P1, P2, and P3 carefully for each set,
to get a sense of the heterogeneity of timeframes represented in each set, as well as the whole dataset.

The timeframes given in CIDs P2N and P3N are broad and coarse approximations, often negotiated between the respondent and reviewer.
These timeframes are to be used with caution. Always read the associated comments in the Comment column.

An end date >= 2020 indicates that social contact is ongoing at the time of data collection in 2021.
