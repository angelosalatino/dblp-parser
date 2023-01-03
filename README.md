# 1. DBLP Parser
A simple python script for parsing DBLP dataset


## 1.1. Table of content
- [1. DBLP Parser](#1-dblp-parser)
  - [1.1. Table of content](#11-table-of-content)
- [2. Set up](#2-set-up)
- [3. Download DBLP](#3-download-dblp)
- [4. Parser](#4-parser)
  - [4.1. Type of documents extracted](#41-type-of-documents-extracted)
  - [4.2. Type of features extracted per document](#42-type-of-features-extracted-per-document)
- [5. Usage examples](#5-usage-examples)
  - [5.1. Parse all papers](#51-parse-all-papers)
    - [5.1.1. Parameters](#511-parameters)
    - [5.1.2. Generate JSONL file](#512-generate-jsonl-file)
    - [5.1.3. Generate Dataframe (pandas)](#513-generate-dataframe-pandas)
    - [5.1.4. Export by Year](#514-export-by-year)
- [6. Coming soon](#6-coming-soon)
- [7. Disclaimer](#7-disclaimer)

# 2. Set up

From your terminal run:
```bash
git clone https://github.com/angelosalatino/dblp-parser.git
cd dblp-parser
pip install -r requirements.txt
```

In order to work, it is important to download both the DBLP dump (dblp.xml.gz and unzip it) and the DTD file (dblp.dtd).
The basic requirements to run this code are ```pandas``` and ```lxml```.

# 3. Download DBLP

The code already provides facilities to download everything is needed:
* the dtd file,
* the latest dump available.

To do so, you need to run the following lines:

```python
dblp = DBLP()
dblp.download_latest_dump()
```

Otherwise, you can simply do this outside the Python environment using the terminal:
```bash
wget https://dblp.org/xml/dblp.xml.gz
wget https://dblp.org/xml/dblp.dtd
gzip -d dblp.xml.gz
```


# 4. Parser

## 4.1. Type of documents extracted

Here is the list of the 10 types of documents available within the DBLP dump:

```
"article",
"inproceedings",
"proceedings",
"book",
"incollection",
"phdthesis",
"mastersthesis",
"www",
"person",
"data"
```

## 4.2. Type of features extracted per document

Here are the 23 types of features that can be used to decribe a particular document in DBLP:

```
"address" 
"author" 
"booktitle"
"cdrom" 
"chapter" 
"cite" 
"crossref" 
"editor" 
"ee" 
"isbn"
"journal" 
"month" 
"note" 
"number" 
"pages" 
"publisher" 
"publnr" 
"school" 
"series" 
"title" 
"url"
"volume" 
"year"
```

In addition to this, the algorithm extract an additional feature: ```type```. This feature specififies the kind of document extracted (*article*, *inproceedings* and so on).

Finally, if the parameter ```include_key_and_mdate=True```, it will add two additional features: key and mdate which are attribute of the document entity in the XML file. 


# 5. Usage examples

## 5.1. Parse all papers

With this function (```parse_all```) you can parse all documents available in DBLP.

### 5.1.1. Parameters

| Parameter   | Default | Info |
| ----------- | ----------- | ----------- |
| dblp_path   | -      | File to load |
| save_path   | -      | Where to save the file |
| features_to_extract   | None      | Features to extract from the dump. If None (def.) extracts everything|
| include_key_and_mdate   | False      | Extracts further keys in the element tag|
| output   | "jsonl"      | Defines the kind of output (jsonl or dataframe)|

dblp_path:str, save_path:str, features_to_extract:dict=None, include_key_and_mdate:bool=False, output:str="jsonl"
### 5.1.2. Generate JSONL file

Within python you can run the following code:
```python
from dblp_parser import DBLP
dblp_path = "dblp.xml"
save_path = "dblp.jsonl"
dblp = DBLP()
dblp.parse_all(dblp_path, save_path)
```
This will extract all documents from *dblp.xml* and describe them according to the 23 features available in the dataset. 
The **output file** is a jsonl file in which each row is a dictionary. To be read, you must read line-by-line and load it as json dictionary.

Extract specific set of features (e.g., just title, url, ee and few others) per document:
```python
from dblp_parser import DBLP
dblp_path = "dblp.xml"
save_path = "dblp.jsonl"
dblp = DBLP()
features = {"url", "author", "ee", "journal", "number", "pages", "publisher", "series","booktitle", "title", "volume", "year"}
dblp.parse_all(dblp_path, save_path, features_to_extract=features)
```
This will create the final file with as many rows as the number of documents, described with just the required features.

### 5.1.3. Generate Dataframe (pandas)

Export DBLP in a **dataframe**:
```python
from dblp_parser import DBLP
dblp_path = "dblp.xml"
dblp = DBLP()
features = {"url", "author", "ee", "journal", "number", "pages", "publisher", "series","booktitle", "title", "volume", "year"}
df = dblp.parse_all(dblp_path, features_to_extract=features, output="dataframe")
print(df)
```

### 5.1.4. Export by Year

Export DBLP content of a given year:
```python
from dblp_parser import DBLP
dblp = DBLP()

dblp_path = "dblp.xml"
save_path = "dblp_2022.json"
dblp.parse_by_year("2022", dblp_path, save_path)
```

# 6. Coming soon
**_Soon will add new features and usecases_**
* parse just conferences papers
* parse just journal papers
* ... if you have an idea please open an issue 


# 7. Disclaimer

This work is inspired by: https://github.com/IsaacChanghau/DBLPParser
