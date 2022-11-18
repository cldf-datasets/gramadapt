<a name="ds-structuredatasetmetadatajson"> </a>

# StructureDataset The title

**CLDF Metadata**: [StructureDataset-metadata.json](./StructureDataset-metadata.json)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF StructureDataset](http://cldf.clld.org/v1.0/terms.rdf#StructureDataset)
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/cldf-datasets/gramadapt
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/cldf-datasets/gramadapt/tree/1616b98">cldf-datasets/gramadapt 1616b98</a></li><li><a href="https://github.com/glottolog/glottolog/tree/51e5fe3f92">Glottolog v4.6-21-g51e5fe3f92</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.8.10</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | gramadapt
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-valuescsv"></a>Table [values.csv](./values.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ValueTable](http://cldf.clld.org/v1.0/terms.rdf#ValueTable)
[dc:extent](http://purl.org/dc/terms/extent) | 412


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

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 64


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

## <a name="table-contactpairscsv"></a>Table [contactpairs.csv](./contactpairs.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 32


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Focus_Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
`Neighbour_Language_ID` | `string` | References [languages.csv::ID](#table-languagescsv)
`Area` | `string` | 

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
`datatype` | `string` | 
`Question_ID` | `string` | References [questions.csv::ID](#table-questionscsv)

## <a name="table-codescsv"></a>Table [codes.csv](./codes.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF CodeTable](http://cldf.clld.org/v1.0/terms.rdf#CodeTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1202


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | The parameter or variable the code belongs to.<br>References [parameters.csv::ID](#table-parameterscsv)
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 

