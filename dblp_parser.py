from datetime import datetime
import re
import os
import sys
from lxml import etree


class DBLP:
    """ The DBLP class that parses the XML DBLP dump """
    def __init__(self):


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
        dict
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
        set
            Refined set of features to extract. User might have prompt wrong features.

        """
        if len(features) == 0 or features is None:
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
        dict


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


    def parse_all(self, dblp_path:str, save_path:str, features_to_extract:dict=None,include_key_and_mdate:bool=False)->None:
        """
        This function parses the DBLP XML file and builds a jsonl file in which
        each row is json dictionary containing the description of a single article
        in DBLP.

        Parameters
        ----------
        dblp_path : str
            Source file of the DBLP file.
        save_path : str
            Destination file of the parsed DBLP file.
        features_to_extract : dict, optional
            User-defined features to extract. The default is None and then it
            will extract all features.
        include_key_and_mdate : bool, optional
            Defines whether to include key and mdate attribute from the
            document attribute list. The default is False.

        Returns
        -------
        None


        """
        self.__log_msg("Parsing all. Started.")

        features_to_extract = self.__check_features(features_to_extract)

        file = open(save_path, 'w', encoding='utf8')

        root = self.__open_dblp_file(dblp_path)

        for element in root:
            if element.tag in self.all_elements:
                attrib_values = self.__extract_features(element, features_to_extract, include_key_and_mdate)
                file.write(str(attrib_values) + '\n')

            self.__clear_element(element)
        file.close()
        self.__log_msg("Parsing all. Finished.")

    
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

def main():
    """
    Main function

    """
    dblp_path = "dblp.xml"
    save_path = "dblp.json"
    dblp = DBLP()
    dblp.parse_all(dblp_path, save_path)

if __name__ == '__main__':
    main()