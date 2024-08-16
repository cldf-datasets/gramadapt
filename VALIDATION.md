# Validating the CLDF dataset

Run CLDF validation:
```shell
cldf validate cldf
```

Make sure the dataset can be loaded into SQLite:
```shell
rm -f laotpa.sqlite
cldf createdb cldf laotpa.sqlite 
```

## Technical validation described in the paper

The GramAdapt dataset has been designed to cover diverse contact scenarios as well as a diverse set
of languages. As such, it presents a first attempt or an exploration of the problem space rather than
a set of measurements for parameters with known meaning and expectations about the results.
Thus, validating the dataset boils down to validating the questionnaire, i.e. making sure suitable
questions were asked.


### Suitablity of domain selection

Questions P1 ask (for each social domain) whether the social domain in question has ever been a domain 
of social contact between Focus and Neighbour Group peoples.

Thus, the relevance of the social domains for the contact scenarios can be computed as precentage of
sets with a "Yes" answer to the P1 questions as follows
```sql
SELECT
    p.domain, 
    cast(sum(CASE c.cldf_name WHEN 'Yes' THEN 1 ELSE 0 END) AS float) / count(v.cldf_id) AS yes_ratio
FROM valuetable AS v 
JOIN codetable AS c
     ON v.cldf_codereference = c.cldf_id
JOIN parametertable AS p 
     ON v.cldf_parameterreference = p.cldf_id
JOIN "questions.csv" AS q 
     ON q.cldf_id = p.question_id 
WHERE q.cldf_contributionReference = 'P1'
GROUP BY p.cldf_id 
ORDER BY yes_ratio DESC;
```
yielding

domain | yes_ration
--- | ---
DTR|0.939393939393939
DLC|0.878787878787879
DLB|0.787878787878788
DFK|0.787878787878788
DKN|0.636363636363636
DEM|0.575757575757576


Contact sets partitioned into groups with equal number of relevant social domains can be computed as
```sql
select
    ndom, 
    group_concat(substr(set_id, 4), ', ') as sets, 
    count(set_id) as total 
from (
    select 
        count(distinct p.cldf_id) as ndom, 
        v.cldf_contributionReference as set_id 
    from valuetable as v 
    join codetable as c 
         on v.cldf_codereference = c.cldf_id 
    join parametertable as p 
         on v.cldf_parameterreference = p.cldf_id 
    join "questions.csv" as q 
         on q.cldf_id = p.question_id 
    where q.cldf_contributionReference = 'P1' and c.cldf_name = 'Yes' 
    group by v.cldf_contributionReference
) 
group by ndom 
order by ndom desc;
```

ndom | sets | total
---:| --- | ---:
6|02, 05, 06a, 07, 09, 12, 17, 18, 21, 22, 24, 25, 30|13
5|23, 27, 29|3
4|03, 04, 08, 10, 13, 15, 19, 20, 28, 32|10
3|01, 14, 16, 31, 33, 34|6
1|11|1


### Visualizing responses per datatype

To further assess the suitability of the questionnaire, we visualize the answers grouped by datatype.

The following three plots are created running `cldfbench` sub-commands.
Running these commands requires "installing" the dataset via `pip install -e .`, to install `cldfbench`
and register the subcommands.


#### Responses to binary questions

The following plot shows the answers to the yes-no questions as clustered heatmap (with grey meaning
missing data). Columns correspond to contact sets, rows to questions.
The leftmost column color-codes the questions by social domain. Questions often cluster
by domain - mostly because of systematically, by-domain missing data; but this is not always the case.

![](etc/binaryvalidity.png)


#### Responses to categorical questions

Of the 65 questions with answers from a fixed set of categories, 38 dealt with language selection. These
38 questions allowed the following answers:
- The Focus Group language
- The Neighbour Group language
- Some other language
- This is highly contextual
- B

and the answers were distributed as shown below:

![](etc/categoricalvalidity.png)


#### Responses to Likert-scale question

112 questions had answers mapped to a five-point [Likert scale](https://en.wikipedia.org/wiki/Likert_scale).
Ideally, questions would be assigned such that answers differ between contact sets. The distribution
of answers to the Likert-scale questions is shown below:

![](etc/likertvalidity.png)


#### Questions of type *Comment*

FIXME: see clld app


#### Time-range questions

FIXME:
