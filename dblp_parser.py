from datetime import datetime
import re
import os
import sys
import pandas as pd
import json
from lxml import etree
import requests
from hurry.filesize import size
import gzip
import shutil


class DBLP:
    """ The DBLP class that parses the XML DBLP dump """
    
    def __init__(self, download:bool = False):
        """
        

        Parameters
        ----------
        download : bool, optional
            Wether to download the latest dump. The default is False.

        Returns
        -------
        None.

        """

        # Element types in DBLP
        self.all_elements = {"article",
                             "inproceedings",
                             "proceedings",
                             "book",
                             "incollection",
                             "phdthesis",
                             "mastersthesis",
                             "www",
                             "person",
                             "data"}


        # Feature types in DBLP
        self.all_features = {"address"  :"str",
                             "author"   :"list",
                             "booktitle":"str",
                             "cdrom"    :"str",
                             "chapter"  :"str",
                             "cite"     :"list",
                             "crossref" :"str",
                             "editor"   :"list",
                             "ee"       :"list",
                             "isbn"     :"str",
                             "journal"  :"str",
                             "month"    :"str",
                             "note"     :"str",
                             "number"   :"str",
                             "pages"    :"str",
                             "publisher":"str",
                             "publnr"   :"str",
                             "school"   :"str",
                             "series"   :"str",
                             "title"    :"str",
                             "url"      :"str",
                             "volume"   :"str",
                             "year"     :"str"}
        
        if download:
            self.__download_dtd()
            self.__download_and_prepare_dataset()
            
            self.__log_msg("Dataset prepared. You can now parse it.")

    
    def __download_dtd(self)->None:
        """Function that downloads the DTD from the DBLP website.
        Args:
            None
        Returns:
            None
        """
        filename = "dblp.dtd"
        url = "https://dblp.uni-trier.de/xml/dblp.dtd"
        self.__download_file(url, filename)
        
        self.__log_msg(f"DTD downloaded from {url}.")
        

    
    def __download_and_prepare_dataset(self)->None:
        """Function that downloads the whole dataset (latest dump) from the DBLP website.
        Then it decompresses it
        Args:
            None
        Returns:
            None
        """
        filename_zip = "dblp.xml.gz"
        url = "https://dblp.uni-trier.de/xml/dblp.xml.gz"
        self.__download_file(url, filename_zip)
        
        self.__log_msg(f"Latest dump of DBLP downloaded from {url}.")
        
        filename_unzip = "dblp.xml"
        

        with gzip.open(filename_zip, 'rb') as f_in:
            with open(filename_unzip, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        self.__log_msg("File unzipped and ready to be parsed.")
                
        
    
    
    def __download_file(self, url:str, filename:str)->bool:
        """Function that downloads files (general).
        
        Args:
            url (string): Url of where the model is located.
            filename (string): location of where to save the model
        Returns:
            boolean: whether it is successful or not.
        """
        is_downloaded = False
        with open(filename, 'wb') as file:
            response = requests.get(url, stream=True)
            total = response.headers.get('content-length')
    
            if total is None:
                #f.write(response.content)
                self.__log_msg('There was an error while downloading the DTD.')
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                    downloaded += len(data)
                    file.write(data)
                    done = int(50*downloaded/total)
                    sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                    sys.stdout.flush()
                sys.stdout.write('\n')
                # self.__log_msg('[*] Done!')
                is_downloaded = True
    
        return is_downloaded
    
    
    def __open_dblp_file(self, dblp_path:str)->etree._Element:
        """
        Opens the DBLP file and returns the XML tree.
        It raises some errors if the files (includng dtd) are not available.

        Parameters
        ----------
        dblp_path : str
            Source file of the DBLP file.

        Returns
        -------
        root : etree._Element


        """
        if not os.path.exists(os.path.join(os.path.dirname(dblp_path),"dblp.dtd")):
            print("Warning! File **dblp.dtd** not found in the same directory of the source file. This may cause issues when loading.")

        try:
            parser = etree.XMLParser(resolve_entities=True,
                                     dtd_validation=False,
                                     load_dtd=True,
                                     no_network=False,
                                     encoding="ISO-8859-1")
            tree = etree.parse(dblp_path, parser=parser)
            root = tree.getroot()
            self.__log_msg("Successfully loaded \"{}\".".format(dblp_path))
            return root

        except IOError:
            self.__log_msg("ERROR: Failed to load file \"{}\". Please check your XML and DTD files.".format(dblp_path))
            sys.exit()


    def __init_features(self, features:set, attributes:dict=None)->dict:
        """
        Initialise the dictionary that will host the document information.

        Parameters
        ----------
        features : set
            User-defined set of features.
        attributes : dict, optional
            The initialised set of document attributes. This
            is important as the dictionary might already be initialized. Hence,
            in this case it important to add new features instead of creating
            it again from scratch. The default is None.

        Returns
        -------
        attributes : dict
            Initialised set of article attibutes.

        """

        if attributes is None:
            attributes = dict()

        for feature in features:
            if self.all_features[feature] == "str":
                attributes[feature] = str()
            elif self.all_features[feature] == "list":
                attributes[feature] = list()
        return attributes


    def __check_features(self, features:set)->set:
        """
        Checks if the user has prompt the correct features.

        Parameters
        ----------
        features : set
            Set of user-define features to extract from the DBLP dump.

        Returns
        -------
        refined_set_of_features : set
            Refined set of features to extract. User might have prompt wrong features.

        """

        if features is None:
            return self.all_features

        if len(features) == 0:
            return self.all_features

        refined_set_of_features = set()
        for feature in features:
            if feature not in self.all_features:
                self.__log_msg("WARNING: Discarding feature \"{}\" as it cannot be extracted from the DBLP dump.".format(feature))
            else:
                refined_set_of_features.add(feature)

        return refined_set_of_features

    def __log_msg(self, message:str)->None:
        """
        Prints log with current time.

        Parameters
        ----------
        message : str
            The message to print out.

        Returns
        -------
        None


        """
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "DBLP", message)



    def __clear_element(self, element:etree._Element)->None:
        """
        Frees up memory for temporary element tree after processing the element.

        Parameters
        ----------
        element : etree._Element
            The element of the xml tree to remove as it has just been processed.

        Returns
        -------
        None


        """
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]


    def __count_pages(self, pages:str)->str:
        """
        Borrowed from: https://github.com/billjh/dblp-iter-parser/blob/master/iter_parser.py
        Parse pages string and count number of pages. There might be multiple pages separated by commas.
        VALID FORMATS:
            51         -> Single number
            23-43      -> Range by two numbers
        NON-DIGITS ARE ALLOWED BUT IGNORED:
            AG83-AG120
            90210H     -> Containing alphabets
            8e:1-8e:4
            11:12-21   -> Containing colons
            P1.35      -> Containing dots
            S2/109     -> Containing slashes
            2-3&4      -> Containing ampersands and more...
        INVALID FORMATS:
            I-XXI      -> Roman numerals are not recognized
            0-         -> Incomplete range
            91A-91A-3  -> More than one dash
            f          -> No digits
        ALGORITHM:
            1) Split the string by comma evaluated each part with (2).
            2) Split the part to subparts by dash. If more than two subparts, evaluate to zero. If have two subparts,
               evaluate by (3). If have one subpart, evaluate by (4).
            3) For both subparts, convert to number by (4). If not successful in either subpart, return zero. Subtract first
               to second, if negative, return zero; else return (second - first + 1) as page count.
            4) Search for number consist of digits. Only take the last one (P17.23 -> 23). Return page count as 1 for (2)
               if find; 0 for (2) if not find. Return the number for (3) if find; -1 for (3) if not find.

        Parameters
        ----------
        pages : str
            The string describing the page numbers.

        Returns
        -------
        str
            The page count

        """
        cnt = 0
        try:
            for part in re.compile(r",").split(pages):
                subparts = re.compile(r"-").split(part)
                if len(subparts) > 2:
                    continue
                else:
                    try:
                        re_digits = re.compile(r"[\d]+")
                        subparts = [int(re_digits.findall(sub)[-1]) for sub in subparts]
                    except IndexError:
                        continue
                    cnt += 1 if len(subparts) == 1 else subparts[1] - subparts[0] + 1
            return "" if cnt == 0 else str(cnt)
        except TypeError:
            return ""


    def __extract_features(self, elements:etree._Element, features_to_extract:dict, include_key_and_mdate:bool=False)->dict:
        """
        Extracts the values of features.

        Parameters
        ----------
        elements : etree._Element
            The XML item to process (article, inproceedings and so forth).
        features_to_extract : dict
            The set of user-defined features to extract.
        include_key_and_mdate : bool, optional
            Defines whether to include key and mdate attribute from the
            document attribute list. The default is False.

        Returns
        -------
        attributes : dict


        """



        if include_key_and_mdate:
            attributes = {  'type'    : elements.tag,
                            'key'     : elements.attrib['key'],
                            'mdate'   : elements.attrib['mdate']}#,
                            #'publtype': elements.attrib['publtype']}
        else:
            attributes = { 'type'    : elements.tag}

        attributes = self.__init_features(features_to_extract, attributes)

        for sub_element in elements:
            if sub_element.tag not in features_to_extract:
                continue
            if sub_element.tag == 'title':
                try:
                    text = re.sub("<.*?>|\\n", "", etree.tostring(sub_element).decode('utf-8'))
                except Exception:
                    text = sub_element.text

            elif sub_element.tag == 'pages':
                text = self.__count_pages(sub_element.text)
            else:
                text = sub_element.text


            if text is not None and len(text) > 0:
                try:
                    if self.all_features[sub_element.tag] == "str":
                        attributes[sub_element.tag] = text
                    elif self.all_features[sub_element.tag] == "list":
                        attributes[sub_element.tag] = attributes.get(sub_element.tag) + [text]
                except KeyError:
                    print("Key {} not found within the set of features to extract.".format(sub_element.tag))
        return attributes
    
    
    def download_latest_dump(self)->None:
        """
        Downloads the latest dump of the DBLP dataset

        Returns
        -------
        None

        """
        self.__download_dtd()
        self.__download_and_prepare_dataset()
        
        self.__log_msg("Dataset prepared. You can now parse it.")
        
    
    def parse_by_year(self, year:str, dblp_path:str, save_path:str=None, features_to_extract:dict=None, include_key_and_mdate:bool=False, output:str="jsonl")->None:
        """
        This function parses the DBLP XML file and finds all the relevant records in a given year.
        It builds a jsonl file in which each row is json dictionary containing 
        the description of a single article in DBLP.

        Parameters
        ----------
        year : str
            The year of which records are desired.
        dblp_path : str
            Source file of the DBLP file.
        save_path : str, optional
            Destination file of the parsed DBLP file. This is important when
            extracting the JSONL. If extracting dataframe there is no need. It
            will raise an exception if the save_path is not provided when
            extracting the JSONL. The default is JSONL.
        features_to_extract : dict, optional
            User-defined features to extract. The default is None and then it
            will extract all features.
        include_key_and_mdate : bool, optional
            Defines whether to include key and mdate attribute from the
            document attribute list. The default is False.
        output : str, optional
            Defines the kind of output to return. Accepted values are "jsonl"
            and "dataframe". Based on these parameters it will respectively
            create a jsonl file or return a dataframe.

        Returns
        -------
        dataframe : pandas.DataFrame
            the dataframe containing all papers. This is returned only if
            output is set to "dataframe"


        """

        if output not in ["jsonl", "dataframe"]:
            raise ValueError("Outputs available are 'jsonl', or 'dataframe'.")


        features_to_extract = self.__check_features(features_to_extract)



        root = self.__open_dblp_file(dblp_path)

        if output == "jsonl":

            if save_path is None:
                raise ValueError("No save path provided.")

            self.__log_msg("Parsing all. Started.")

            with open(save_path, 'w', encoding='utf8') as file:

                for element in root:
                    if element.tag in self.all_elements:
                        attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                        if attrib_values["year"] == year:
                            file.write(json.dumps(attrib_values) + '\n')

                    self.__clear_element(element)

            file.close()

            self.__log_msg("Parsing all. Finished.")

        elif output == "dataframe":

            self.__log_msg("WARNING. This operation may take some time and will certainly use an abundance of RAM.")

            self.__log_msg("Parsing all. Started.")

            dataframe = pd.DataFrame(columns=list(features_to_extract))
            for element in root:
                if element.tag in self.all_elements:
                    attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                    if attrib_values["year"] == year:
                        dataframe = dataframe.append(attrib_values, ignore_index=True)


            self.__log_msg("Parsing all. Finished.")
            return dataframe


    def parse_by_years(self, years:list, dblp_path:str, save_path:str=None, features_to_extract:dict=None, include_key_and_mdate:bool=False, output:str="jsonl")->None:
        """
        This function parses the DBLP XML file and finds all the relevant records in a given set of years.
        It builds a jsonl file in which each row is json dictionary containing 
        the description of a single article in DBLP.
    
        Parameters
        ----------
        years : list
            The years of which records are desired.
        dblp_path : str
            Source file of the DBLP file.
        save_path : str, optional
            Destination file of the parsed DBLP file. This is important when
            extracting the JSONL. If extracting dataframe there is no need. It
            will raise an exception if the save_path is not provided when
            extracting the JSONL. The default is JSONL.
        features_to_extract : dict, optional
            User-defined features to extract. The default is None and then it
            will extract all features.
        include_key_and_mdate : bool, optional
            Defines whether to include key and mdate attribute from the
            document attribute list. The default is False.
        output : str, optional
            Defines the kind of output to return. Accepted values are "jsonl"
            and "dataframe". Based on these parameters it will respectively
            create a jsonl file or return a dataframe.
    
        Returns
        -------
        dataframe : pandas.DataFrame
            the dataframe containing all papers. This is returned only if
            output is set to "dataframe"
    
    
        """
    
        if output not in ["jsonl", "dataframe"]:
            raise ValueError("Outputs available are 'jsonl', or 'dataframe'.")
    
    
        features_to_extract = self.__check_features(features_to_extract)
    
        years = set(years)
    
        root = self.__open_dblp_file(dblp_path)
    
        if output == "jsonl":
    
            if save_path is None:
                raise ValueError("No save path provided.")
    
            self.__log_msg("Parsing all. Started.")
    
            with open(save_path, 'w', encoding='utf8') as file:
    
                for element in root:
                    if element.tag in self.all_elements:
                        attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                        if attrib_values["year"] in years:
                            file.write(json.dumps(attrib_values) + '\n')
    
                    self.__clear_element(element)
    
            file.close()
    
            self.__log_msg("Parsing all. Finished.")
    
        elif output == "dataframe":
    
            self.__log_msg("WARNING. This operation may take some time and will certainly use an abundance of RAM.")
    
            self.__log_msg("Parsing all. Started.")
    
            dataframe = pd.DataFrame(columns=list(features_to_extract))
            for element in root:
                if element.tag in self.all_elements:
                    attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                    if attrib_values["year"] in years:
                        dataframe = dataframe.append(attrib_values, ignore_index=True)
    
    
            self.__log_msg("Parsing all. Finished.")
            return dataframe
        

    def parse_all(self, dblp_path:str, save_path:str=None, features_to_extract:dict=None, include_key_and_mdate:bool=False, output:str="jsonl")->None:
        """
        This function parses the DBLP XML file and builds a jsonl file in which
        each row is json dictionary containing the description of a single article
        in DBLP.

        Parameters
        ----------
        dblp_path : str
            Source file of the DBLP file.
        save_path : str, optional
            Destination file of the parsed DBLP file. This is important when
            extracting the JSONL. If extracting dataframe there is no need. It
            will raise an exception if the save_path is not provided when
            extracting the JSONL. The default is JSONL.
        features_to_extract : dict, optional
            User-defined features to extract. The default is None and then it
            will extract all features.
        include_key_and_mdate : bool, optional
            Defines whether to include key and mdate attribute from the
            document attribute list. The default is False.
        output : str, optional
            Defines the kind of output to return. Accepted values are "jsonl"
            and "dataframe". Based on these parameters it will respectively
            create a jsonl file or return a dataframe.

        Returns
        -------
        dataframe : pandas.DataFrame
            the dataframe containing all papers. This is returned only if
            output is set to "dataframe"


        """

        if output not in ["jsonl", "dataframe"]:
            raise ValueError("Outputs available are 'jsonl', or 'dataframe'.")


        features_to_extract = self.__check_features(features_to_extract)



        root = self.__open_dblp_file(dblp_path)

        if output == "jsonl":

            if save_path is None:
                raise ValueError("No save path provided.")

            self.__log_msg("Parsing all. Started.")

            with open(save_path, 'w', encoding='utf8') as file:

                for element in root:
                    if element.tag in self.all_elements:
                        attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                        file.write(json.dumps(attrib_values) + '\n')

                    self.__clear_element(element)

            file.close()

            self.__log_msg("Parsing all. Finished.")

        elif output == "dataframe":

            self.__log_msg("WARNING. This operation may take some time and will certainly use an abundance of RAM.")

            self.__log_msg("Parsing all. Started.")

            dataframe = pd.DataFrame(columns=list(features_to_extract))
            for element in root:
                if element.tag in self.all_elements:
                    attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                    dataframe = dataframe.append(attrib_values, ignore_index=True)


            self.__log_msg("Parsing all. Finished.")
            return dataframe



    def print_features(self)->None:
        """
        Prints the available features that can be extracted from the DBLP dump.

        Returns
        -------
        None


        """
        print("""The features that can be extracted from the DBLP dump are: {}.\n
              For more info, check on https://dblp.uni-trier.de/faq/index.html"""
              .format(", ".join([k for k,v in self.all_features.items()])))

