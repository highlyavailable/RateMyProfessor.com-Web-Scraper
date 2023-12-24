__author__ = "Peter Bryant"
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"
__email__ = "peter.bryant@gatech.edu"
__status__ = "Development"

# Standard library imports
import json
import time
import os
import argparse
import importlib
import logging

import config

# Selenium imports
from selenium import webdriver  # Webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Find elements by

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait  # Wait for elements to load
from selenium.webdriver.support import expected_conditions as EC  # Expected conditions
# Misc. exceptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from rmp_statistics import rmp_stats

# Global
# RMP professor search URL
const_rmp_search_url = 'https://www.ratemyprofessors.com/search/professors'
const_print_stats = False

class RMPSchool:
    """
    Represents an instance of a school listed on RateMyProfessors.com, contains functions to instantiate School
    attributes, and supports and export to static JSON dump.
    """

    def __init__(self, school_id):
        """
        Constructor for RMPSchool class.
        :param school_id (int): The unique school ID that RateMyProfessor assigns to identify each University.
        """
        self.school_id = school_id                                               # Parameter for the school ID
        # Build request endpoint for the school ID
        self.rmp_professors_endpoint = f"{const_rmp_search_url}/{school_id}?q=*"

        # Instantiate Chrome Options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('log-level=3')
        self.options.add_argument("start-maximized")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])

        # Create web driver
        # Instantiate the webdriver object with the options
        self.driver = webdriver.Chrome(options=self.options)
        # Load the RMP professors search page
        self.driver.get(self.rmp_professors_endpoint)\
        
        # Reference to the show more button, used in multiple places 
        self.show_more_button = ""
        # Variable to indicate completion, can be set in various places 
        self.scrape_complete = False

        # Set attributes for the School
        self.school_name = self.get_school_name()
        self.num_professors = self.get_num_professors()
        self.professors_list = []
        self.get_professors_list()
        
        school_name_fp = self.school_name.replace(' ', '').replace('-', '_').lower()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        filename = f'output_data\\{school_name_fp}_professors.csv'
        full_path = os.path.join(script_directory, filename)
            
        self.dump_professors_list_to_csv(full_path)
        
        if const_print_stats:
            rmp_stats(full_path, school_name_fp)

    def dump_professors_list_to_csv(self, file_path):
        """Dumps the professors list to a CSV file.
        :param file_path (str): The file path to store the CSV file.
        """
        # Remove the file if it exists. Error is thrown otherwise.
        if os.path.exists(file_path):
            os.remove(file_path)
        # Create a a new file to write to
        with open(file_path, 'x') as f:
            f.write(
                'name,department,rating,num_ratings,would_take_again_pct,level_of_difficulty\n')
            for professor in self.professors_list:
                f.write(f"{professor.name},{professor.department},{professor.rating},{professor.num_ratings},{professor.would_take_again_pct},{professor.level_of_difficulty}\n")

    def get_school_name(self):
        """Fetches the school name from the professors search endpoint.
        :returns school_name (str): The full school name corresponding to the SID.
        """
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/h1/span/b'  # RMP error message Xpath
        school_name_element = self.driver.find_element(
            by=By.XPATH, value=Xpath)  # Find the error message element'
        school_name = school_name_element.text.strip()
        return school_name

    def get_num_professors(self, testing=False):
        """Fetches the number of professors from the professors search endpoint.
        :returns num_professors (int): The number of professors listed on the professors search endpoint.
        """
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div'  # RMP error message Xpath
        search_results_header_id = self.driver.find_element(
            By.XPATH, Xpath)  # Find the error message element
        num_professors = search_results_header_id.text.split('professors')[
            0].strip()
        return num_professors

    def gen_next_professor_element(self, idx):
        """
        Fetches the next professor object using the IDX value for the XPath
        If there is no next element, try pressing the show more button for more
        If there's no show more button, we have finished
        """
        try:
            new_professor_Xpath = f"//*[@id='root']/div/div/div[4]/div[1]/div[1]/div[3]/a[{idx}]"
            new_prof_elem =  self.driver.find_elements(
                        By.XPATH, new_professor_Xpath)[0]
            return new_prof_elem
        except (IndexError, NoSuchElementException) as  ine:
            #print("New Professor Element not found - Index Path")
            #print("Pressing button and retrying")

            # If the show more button is already gone
            # or if, after trying to press it, we find out it's gone
            # then we assume the scrape is complete
            if self.show_more_button == "" or self.push_show_more_button() == "": 
                self.scrape_complete = True
                return 1
            
            #If pressing the show more button worked, find the next element
            new_professor_Xpath = f"//*[@id='root']/div/div/div[4]/div[1]/div[1]/div[3]/a[{idx}]"
            new_prof_elem =  self.driver.find_element(
                        By.XPATH, new_professor_Xpath)
            
            return new_prof_elem
        except Exception as e:
            print(f"Gen_Next_Professor_Element: Some other error occured - \n {e.msg}")


    def set_show_more_button(self):
        """Find the Show More button, and attatches an ID to it to find it easily"""
        try:
            Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
            self.show_more_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, Xpath)))
            self.driver.execute_script(
                            "arguments[0].setAttribute('id', arguments[1]);", self.show_more_button, "RMP_Scrape")
        except Exception as e:
            #print(f"Set Show More Button: Some error occurred \n {e.msg}")
            raise e

    def push_show_more_button(self, mod_eight=False):
        """Push the show_more_button
            mod_eight will only be set where the function is called 
            after reaching a multiple of 8
        """
        if self.show_more_button == "": return ""
        try: 
            print("Searching for more Professors...")
            self.driver.execute_script(
                "arguments[0].click();", self.show_more_button)
            self.show_more_button = ""
            self.show_more_button = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "RMP_Scrape")))
            time.sleep(3)
        except StaleElementReferenceException as ser:
            # The reference to the button is stale, attempt to find it again
            try:
                self.set_show_more_button()
                #print("Searching for more Professors, Again...")
                self.driver.execute_script(
                    "arguments[0].click();", self.show_more_button)
                self.show_more_button = ""
                self.show_more_button = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, "RMP_Scrape")))
                time.sleep(3)
            except Exception as e:
                # Assume button has been taken out, meaning we're on the last page
                # Set the show_more_button to an empty string
                # and return an empty string
                # To signal there is no more after this page
                self.show_more_button = ""
                return ""
        except Exception as e:
            #print(f"Push SHow More Button: Some error occured - {e.msg}")
            return 

    def get_professors_list(self):
        """Fetches the list of professors from the professors search endpoint.
        """

        print("Search Started!")
        self.set_show_more_button()

        # Iterate through the eight teachers listed on the page
        professor_idx = 0
        while not self.scrape_complete:
            try:
                professor_idx += 1
                new_professor_text = ""
                new_prof_elem = self.gen_next_professor_element(professor_idx)

                if new_prof_elem == 1: break

                new_professor_text = new_prof_elem.text 
                
                professor_attr_list = new_professor_text.split('\n')
                new_prof_obj = RMPProfessor(professor_attr_list)
                self.professors_list.append(new_prof_obj)
                print(new_prof_obj)

                if professor_idx % 8 == 0:
                    self.push_show_more_button(mod_eight=True)
                    time.sleep(3)
                    continue

                if str(professor_idx) == self.num_professors:
                    print("IDX Reached num professors")
                    self.scrape_complete = True

            except NoSuchElementException as e:
                if new_professor_text == "":
                    # Could not find the professor element. 
                    # set IDX back by 1 and try again                        
                    professor_idx -= 1
                    continue
                else:
                    # It couldn't find something else
                    print("Could not find something else. Exiting...")
                    break
            except Exception as e:
                # a different error occurred
                print(f"Error Occured while getting professor list:  {e.msg}")
                break

            


class RMPProfessor:
    def __init__(self, professor_attr_list):
        self.name = None
        self.department = None
        self.rating = None
        self.num_ratings = None
        self.would_take_again_pct = None
        self.level_of_difficulty = None
        self.get_attr_from_list(professor_attr_list)

    def get_attr_from_list(self, professor_attr_list):
        self.name = professor_attr_list[3]
        self.department = professor_attr_list[4]
        self.rating = professor_attr_list[1]
        self.num_ratings = professor_attr_list[2].split(' ')[0]
        self.would_take_again_pct = professor_attr_list[6]
        self.level_of_difficulty = professor_attr_list[8]

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'name': self.name,
            'department': self.department,
            'rating': self.rating,
            'num_ratings': self.num_ratings,
            'would_take_again_pct': self.would_take_again_pct,
            'level_of_difficulty': self.level_of_difficulty
        }


if __name__ == "__main__":

    # Command line argument parser
    parser = argparse.ArgumentParser()

    # Add an argument '-s' or '--sid' to specify the RMP school id
    parser.add_argument(
        "-s", "--sid", help="Specify the RMP school id", type=int)

    # Add an argument '-f' or '--file_path' to specify the file path to store the scraped data
    parser.add_argument(
        "-f", "--file_path", help="Specify the file path to store the scraped data", type=str)

    parser.add_argument(
        "-t", "--statistics", help="Run and Print the statistics of the School", action='store_true')

    # Add an argument '-config' or '--config' to specify the config file path if you want to use a config file
    # instead of specifying the arguments
    parser.add_argument(
        "-config", "--config",
        help="Specify the config file path if you want to use a config file instead of specifying the arguments",
        type=str)

    args = parser.parse_args()
    if args.statistics:
        const_print_stats = True

    if args.config is not None:
        # If the arguments are not specified, use the config file
        if args.sid is None and config.sid is not None:
            args.sid = config.sid

        if args.file_path is None and config.file_path is not None:
            args.file_path = config.file_path

    # Instantiate the RMPSchool object
    rmp_school = RMPSchool(args.sid)
