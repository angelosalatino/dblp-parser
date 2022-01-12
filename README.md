# DBLP Parser
A simple python script for parsing DBLP dataset


## Table of content
- [DBLP Parser](#dblp-parser)
  - [Table of content](#table-of-content)
  - [Set up](#set-up)
  - [Type of documents extracted](#type-of-documents-extracted)
  - [Type of features extracted per document](#type-of-features-extracted-per-document)
  - [Usage examples](#usage-examples)
    - [Parse all papers](#parse-all-papers)
  - [Coming soon](#coming-soon)
- [Disclaimer](#disclaimer)

## Set up

From your terminal run:
```bash
git clone https://github.com/angelosalatino/dblp-parser.git
cd dblp-parser
wget https://dblp.org/xml/dblp.xml.gz
wget https://dblp.org/xml/dblp.dtd
gzip -d dblp.xml.gz
```

## Type of documents extracted

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

## Type of features extracted per document

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


## Usage examples

### Parse all papers

Within python you can run the following code:
```python
dblp_path = "dblp.xml"
save_path = "dblp.json"
dblp = DBLP()
dblp.parse_all(dblp_path, save_path, features_to_extract=features)
```
This will extract all documents from *dblp.xml* and describe them according to the 23 features available in the dataset. 
The **output file** is a jsonl file in which each row is a dictionary. To be read, you must read line-by-line and load it as json dictionary.

Extract specific set of features (e.g., just title, url, ee and few others) per document:
```python
dblp_path = "dblp.xml"
save_path = "dblp.json"
dblp = DBLP()
features = {"url", "author", "ee", "journal", "number", "pages", "publisher", "series","booktitle", "title", "volume", "year"}
dblp.parse_all(dblp_path, save_path, features_to_extract=features)
```
This will create the final file with as many rows as the number of documents, described with just the required features.

## Coming soon
**_Soon will add new features and usecases_**
* Will let export the output both as jsonl files and pandas dataframes
* parse just conferences papers
* parse just journal papers
* ... if you have an idea please open an issue 


# Disclaimer

This work is inspired by: https://github.com/IsaacChanghau/DBLPParser
