#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 10:37:17 2023

@author: aas358
"""

from dblp_parser import DBLP



def parse_year_2022():
    dblp = DBLP()
    
    dblp_path = "dblp.xml"
    save_path = "dblp_2022.json"
    dblp.parse_by_year("2022", dblp_path, save_path)
    
    
def parse_everything():
    dblp = DBLP()
    
    dblp_path = "dblp.xml"
    save_path = "dblp.json"
    dblp.parse_all(dblp_path, save_path)
    
    
def parse_a_selectio_of_features():
    dblp = DBLP()
    
    dblp_path = "dblp.xml"
    save_path = "dblp.jsonl"
    features = {"url", "author", "ee", "journal", "number", "pages", "publisher", "series","booktitle", "title", "volume", "year"}
    dblp.parse_all(dblp_path, save_path, features_to_extract=features)
    
def generate_dataframe():
    dblp = DBLP()
    
    dblp_path = "dblp.xml"
    features = {"url", "author", "ee", "journal", "number", "pages", "publisher", "series","booktitle", "title", "volume", "year"}
    df = dblp.parse_all(dblp_path, features_to_extract=features, output="dataframe")
    print(df)


def main():
    """
    Main function

    """
    
    # parse_everything()
    # parse_a_selectio_of_features()
    # generate_dataframe()
    parse_year_2022()


if __name__ == '__main__':
    main()