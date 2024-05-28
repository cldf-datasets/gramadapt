<a name="ds-structuredatasetmetadatajson"> </a>

# StructureDataset GramAdapt Crosslinguistic Social Contact Dataset

**CLDF Metadata**: [StructureDataset-metadata.json](./StructureDataset-metadata.json)

This dataset is a first attempt at collecting socio-cultural-demographic data about contact scenarios, including attempts at quantification as well as qualitative elaborations by respondents.

Respondents were approached as academic collaborators, not as volunteers in an experiment. Respondents were not chosen at random. Respondents were chosen based on their published research and fieldwork experience with either or both Focus and Neighbour language communities.

property | value
 --- | ---
[dc:bibliographicCitation](http://purl.org/dc/terms/bibliographicCitation) | Eri Kashima, Francesca Di Garbo, Oona Raatikainen, Rosnátaly Avelino, Sacha Beck, Anna Berge, Ana Blanco, Ross Bowden, Nicolás Brid, Joseph M Brincat, María Belén Carpio, Alexander Cobbinah, Paola Cúneo, Anne-Maria Fehn, Saloumeh Gholami, Arun Ghosh, Hannah Gibson, Elizabeth Hall, Katja Hannß, Hannah Haynie, Jerry Jacka, Matias Jenny, Richard Kowalik, Sonal Kulkarni-Joshi, Maarten Mous, Marcela Mendoza, Cristina Messineo, Francesca Moro, Hank Nater, Michelle A Ocasio, Bruno Olsson, Ana María Ospina Bozzi, Agustina Paredes, Admire Phiri, Nicolas Quint, Erika Sandman, Dineke Schokkin, Ruth Singer, Ellen Smith-Dennis, Lameen Souag, Yunus Sulistyono, Yvonne Treis, Matthias Urban, Jill Vaughan, Deginet Wotango Doyiso, Georg Ziegelmeyer, Veronika Zikmundová. (2023). GramAdapt Crosslinguistic Social Contact Dataset. (1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7508054
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF StructureDataset](http://cldf.clld.org/v1.0/terms.rdf#StructureDataset)
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/cldf-datasets/gramadapt
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/cldf-datasets/gramadapt/tree/25c2059">cldf-datasets/gramadapt 25c2059</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v5.0">Glottolog v5.0</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.10.12</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | gramadapt
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-valuescsv"></a>Table [values.csv](./values.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ValueTable](http://cldf.clld.org/v1.0/terms.rdf#ValueTable)
[dc:extent](http://purl.org/dc/terms/extent) | 12924


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | 
[Code_ID](http://cldf.clld.org/v1.0/terms.rdf#codeReference) | `string` | References [codes.csv::ID](#table-codescsv)
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | 
`Respondent` | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 68


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal` | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 

## <a name="table-contributionscsv"></a>Table [contributions.csv](./contributions.csv)

Contributions in GramAdapt are 'contact sets', i.e. descriptions of a contact situation between two neighbouring languages. Each contact set is unique in terms of the timeframe they respond for. We urge researchers who use this dataset to read the Comments column for questions CID P1, P2, and P3 carefully for each set, to get a sense of the heterogeneity of timeframes represented in each set, as well as the whole dataset.

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ContributionTable](http://cldf.clld.org/v1.0/terms.rdf#ContributionTable)
[dc:extent](http://purl.org/dc/terms/extent) | 34


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | The unique identifier of a contact pair. The two digit IDs were assigned based on order of completion. Sets that are linked by language communities, but represent different time slices, contain a Roman alphabet symbol, i.e. Set06a and Set06b are for the contact scenario between Maltese and Sicilian, but for different time periods of contact.<br>Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Contributor](http://cldf.clld.org/v1.0/terms.rdf#contributor) | `string` | 
[Citation](http://cldf.clld.org/v1.0/terms.rdf#citation) | `string` | 
[Focus_Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
`Neighbour_Language_ID` | `string` | References [languages.csv::ID](#table-languagescsv)
`Reviewers` | list of `string` (separated by ` & `) | The GramAdapt team members responsible for checking the responses.
`Area` | `string` | Information about the geographical location of each contact set based on Autotyp areal classification

## <a name="table-questionscsv"></a>Table [questions.csv](./questions.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 280


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 381


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[ColumnSpec](http://cldf.clld.org/v1.0/terms.rdf#columnSpec) | `json` | 
`datatype` | `string` | 
`Question_ID` | `string` | References [questions.csv::ID](#table-questionscsv)
`Domain` | `string` | Indicating the domain to which the responses apply. Possible options are the overview questionnaire (OV) and social domains (DEM = Exchange and Marriage; DFK = Family and Kin; DKN = Knowledge; DLB = Labour; DLC = Local Community; DTR = Trade).

## <a name="table-codescsv"></a>Table [codes.csv](./codes.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF CodeTable](http://cldf.clld.org/v1.0/terms.rdf#CodeTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1535


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | The parameter or variable the code belongs to.<br>References [parameters.csv::ID](#table-parameterscsv)
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 

