<a name="ds-structuredatasetmetadatajson"> </a>

# StructureDataset GramAdapt Crosslinguistic Social Contact Dataset

**CLDF Metadata**: [StructureDataset-metadata.json](./StructureDataset-metadata.json)

**Sources**: [sources.bib](./sources.bib)

This dataset is a first attempt at collecting socio-cultural-demographic data about contact scenarios, including attempts at quantification as well as qualitative elaborations by respondents.

Respondents were approached as academic collaborators, not as volunteers in an experiment. Respondents were not chosen at random. Respondents were chosen based on their published research and fieldwork experience with either or both Focus and Neighbour language communities.

property | value
 --- | ---
[dc:bibliographicCitation](http://purl.org/dc/terms/bibliographicCitation) | Eri Kashima, Francesca Di Garbo, Oona Raatikainen, Rosnátaly Avelino, Sacha Beck, Anna Berge, Ana Blanco, Ross Bowden, Nicolás Brid, Joseph M Brincat, María Belén Carpio, Alexander Cobbinah, Paola Cúneo, Anne-Maria Fehn, Saloumeh Gholami, Arun Ghosh, Hannah Gibson, Elizabeth Hall, Katja Hannß, Hannah Haynie, Jerry Jacka, Matias Jenny, Richard Kowalik, Sonal Kulkarni-Joshi, Maarten Mous, Marcela Mendoza, Cristina Messineo, Francesca Moro, Hank Nater, Michelle A Ocasio, Bruno Olsson, Ana María Ospina Bozzi, Agustina Paredes, Admire Phiri, Nicolas Quint, Erika Sandman, Dineke Schokkin, Ruth Singer, Ellen Smith-Dennis, Lameen Souag, Yunus Sulistyono, Yvonne Treis, Matthias Urban, Jill Vaughan, Deginet Wotango Doyiso, Georg Ziegelmeyer, Veronika Zikmundová. (2023). GramAdapt Crosslinguistic Social Contact Dataset. (1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7508054
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF StructureDataset](http://cldf.clld.org/v1.0/terms.rdf#StructureDataset)
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/cldf-datasets/gramadapt
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/cldf-datasets/gramadapt/tree/56e73bc">cldf-datasets/gramadapt 56e73bc</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v5.0">Glottolog v5.0</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.10.12</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | gramadapt
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-valuescsv"></a>Table [values.csv](./values.csv)

The *ValueTable* lists answers to the questions in the GramAdapt questionnaire coded as values for the Focus group language (except for values for the two 'synthetic' parameters 'Focus language' and 'Contact pair', which may also be coded for the language of the Neighbour group).

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ValueTable](http://cldf.clld.org/v1.0/terms.rdf#ValueTable)
[dc:extent](http://purl.org/dc/terms/extent) | 13163


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | 
[Code_ID](http://cldf.clld.org/v1.0/terms.rdf#codeReference) | `string` | References [codes.csv::ID](#table-codescsv)
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
[Contactset_ID](http://cldf.clld.org/v1.0/terms.rdf#contributionReference) | `string` | Link to the corresponding contact set.<br>References [contributions.csv::ID](#table-contributionscsv)
`Respondent` | `string` | 

## <a name="table-contributorscsv"></a>Table [contributors.csv](./contributors.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 49


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
`Editor` | `boolean`<br>Valid choices:<br> `Yes` `No` | 

## <a name="table-mediacsv"></a>Table [media.csv](./media.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF MediaTable](http://cldf.clld.org/v1.0/terms.rdf#MediaTable)
[dc:extent](http://purl.org/dc/terms/extent) | 90


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Media_Type](http://cldf.clld.org/v1.0/terms.rdf#mediaType) | `string`<br>Regex: `[^/]+/.+` | 
[Download_URL](http://cldf.clld.org/v1.0/terms.rdf#downloadUrl) | `anyURI` | 
[Path_In_Zip](http://cldf.clld.org/v1.0/terms.rdf#pathInZip) | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

The GramAdapt dataset is constructed around *contact sets*, pairs of *Focus* and*Neighbour* language communities. This table lists the languages spoken by either of these communities.

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 68


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal`<br>&ge; -90<br>&le; 90 | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal`<br>&ge; -180<br>&le; 180 | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string`<br>Regex: `[a-z0-9]{4}[1-9][0-9]{3}` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string`<br>Regex: `[a-z]{3}` | 

## <a name="table-contributionscsv"></a>Table [contributions.csv](./contributions.csv)

The GramAdapt dataset provides two types of contributions: (1) 'contact sets', i.e. descriptions of a contact situation between two neighbouring communities speaking different languages. Each contact set is unique in terms of the timeframe they respond for. We urge researchers who use this dataset to read the Comments column for questions CID P1, P2, and P3 carefully for each set, to get a sense of the heterogeneity of timeframes represented in each set, as well as the whole dataset. (2) 'rationales' explaning the goals, definitions and theoretical support for (sets of) questions in the GramAdapt questionnaire.

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ContributionTable](http://cldf.clld.org/v1.0/terms.rdf#ContributionTable)
[dc:extent](http://purl.org/dc/terms/extent) | 124


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | (1) For contact sets: The unique identifier of a contact pair. The two digit IDs were assigned based on order of completion. Sets that are linked by language communities, but represent different time slices, contain a Roman alphabet symbol, i.e. Set06a and Set06b are for the contact scenario between Maltese and Sicilian, but for different time periods of contact. (2) For rationales the identifier are based on domain and question number.<br>Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | The rationale document formatted as CLDF Markdown.
[Contributor](http://cldf.clld.org/v1.0/terms.rdf#contributor) | `string` | 
[Citation](http://cldf.clld.org/v1.0/terms.rdf#citation) | `string` | 
`Type` | `string`<br>Valid choices:<br> `contactset` `rationale` | 
[Focus_Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | Link to the language spoken by the focus group in a contact set.<br>References [languages.csv::ID](#table-languagescsv)
`Neighbour_Language_ID` | `string` | Link to the language spoken by the neighbour group in a contact set.<br>References [languages.csv::ID](#table-languagescsv)
`Author_IDs` | list of `string` (separated by ` `) | References [contributors.csv::ID](#table-contributorscsv)
`Reviewer_IDs` | list of `string` (separated by ` `) | The GramAdapt team members responsible for checking the responses.<br>References [contributors.csv::ID](#table-contributorscsv)
`Area` | `string` | Information about the geographical location of each contact set based on Autotyp areal classification
[Document](http://cldf.clld.org/v1.0/terms.rdf#mediaReference) | `string` | Link to rendered Markdown document.<br>References [media.csv::ID](#table-mediacsv)
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)

## <a name="table-questionscsv"></a>Table [questions.csv](./questions.csv)

This table lists the questions of the GramAdapt questionnaire with links to the respective rationale.

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 265


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Rationale](http://cldf.clld.org/v1.0/terms.rdf#contributionReference) | list of `string` (separated by ` `) | Link to the rationale for this question.<br>References [contributions.csv::ID](#table-contributionscsv)

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

Questions in GramAdapt may be broken up into several sub-questions. This table lists the atomic sub-questions.

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 394


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[ColumnSpec](http://cldf.clld.org/v1.0/terms.rdf#columnSpec) | `json` | 
`datatype` | `string`<br>Regex: `Binary-YesNo|Comment|Scalar|Types|TypesSequential|TypesMultiple|Value` | **Binary-YesNo**: A binary answer of either ‘Yes’ or ‘No; **Comment**: Not preset, just a comment field, i.e. free response. **Scalar**: A Likert 5 point scale. The response is in textual form, but represents ordinals on a scale of 1-5 (e.g. “Neither positive nor negative” -> 3). **Types**: A list of preset answers where only one can be chosen (e.g. “FL, NL, Some other language, This is highly contextual”) **TypesSequential**: A list of ordered, categorical answers where only one can be chosen **Types-Multiple**: A list of preset answers, where multiple can be chosen **Value**: A numerical value
`Question_ID` | `string` | Links to the corresponding GramAdapt question.<br>References [questions.csv::ID](#table-questionscsv)
`Domain` | `string`<br>Valid choices:<br> `OV` `DEM` `DFK` `DKN` `DLB` `DLC` `DTR` | Indicating the domain to which the responses apply. Possible options are the overview questionnaire (**OV**) and social domains (**DEM** = Exchange and Marriage; **DFK** = Family and Kin; **DKN** = Knowledge; **DLB** = Labour; **DLC** = Local Community; **DTR** = Trade).
`Is_Timeframe_Comment` | `boolean`<br>Valid choices:<br> `yes` `no` | Flag signaling whether answers to this question describe a timeframe.

## <a name="table-codescsv"></a>Table [codes.csv](./codes.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF CodeTable](http://cldf.clld.org/v1.0/terms.rdf#CodeTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1529


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | The parameter or variable the code belongs to.<br>References [parameters.csv::ID](#table-parameterscsv)
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
`Ordinal` | `integer`<br>&ge; 1<br>&le; 5 | Ordinal, representing the value for a Scalar parameter on a 5 point Likert scale.

