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
from selenium import webdriver # Webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Find elements by

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait  # Wait for elements to load
from selenium.webdriver.support import expected_conditions as EC  # Expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # Misc. exceptions

# Global
const_rmp_search_url = 'https://www.ratemyprofessors.com/search/professors' # RMP professor search URL

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
        self.rmp_professors_endpoint = f"{const_rmp_search_url}/{school_id}?q=*" # Build request endpoint for the school ID
        
        # Instantiate Chrome Options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('log-level=3')
        self.options.add_argument("start-maximized")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Create web driver
        self.driver = webdriver.Chrome(options=self.options) # Instantiate the webdriver object with the options
        self.driver.get(self.rmp_professors_endpoint)        # Load the RMP professors search page
        
        # Set attributes for the School
        # self.school_name = self.get_school_name()
        self.num_professors = self.get_num_professors()
        self.professors_list = []
        self.get_professors_list()
        self.dump_professors_list_to_csv('professors.csv')
    
    def dump_professors_list_to_csv(self, file_path):
        """Dumps the professors list to a CSV file.
        :param file_path (str): The file path to store the CSV file.
        """
        with open(file_path, 'w') as f:
            f.write('name,department,rating,num_ratings,would_take_again_pct,level_of_difficulty\n')
            for professor in self.professors_list:
                f.write(f"{professor.name},{professor.department},{professor.rating},{professor.num_ratings},{professor.would_take_again_pct},{professor.level_of_difficulty}\n")
    
    def get_school_name(self):
        """Fetches the school name from the professors search endpoint.
        :returns school_name (str): The full school name corresponding to the SID.
        """
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/h1/span/b'  # RMP error message Xpath
        school_name_element = self.driver.find_element(by=By.XPATH, value=Xpath)  # Find the error message element'
        school_name = school_name_element.text.strip()
        return school_name

    def get_num_professors(self, testing=False):
        """Fetches the number of professors from the professors search endpoint.
        :returns num_professors (int): The number of professors listed on the professors search endpoint.
        """
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div'  # RMP error message Xpath
        search_results_header_id = self.driver.find_element(By.XPATH, Xpath)  # Find the error message element
        num_professors = search_results_header_id.text.split('professors')[0].strip()
        return num_professors

    def get_professors_list(self):
        """Fetches the list of professors from the professors search endpoint.
        """

        # Find the show more button
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
        show_more_button = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, Xpath)))

        # Iterate through the eight teachers listed on the page
        professor_idx = 0
        while True:
            try:
                professor_idx += 1
                new_professor_Xpath = f"//*[@id='root']/div/div/div[4]/div[1]/div[1]/div[3]/a[{professor_idx}]"
                new_professor_text = self.driver.find_element(By.XPATH, new_professor_Xpath).text
                professor_attr_list = new_professor_text.split('\n')
                new_prof_obj = RMPProfessor(professor_attr_list)
                self.professors_list.append(new_prof_obj)
                print(new_prof_obj)
                
                if professor_idx % 8 == 0:
                    self.driver.execute_script("arguments[0].click();", show_more_button)
                    show_more_button = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, Xpath)))
                    time.sleep(3)

            except Exception as e:
                try:
                    self.driver.execute_script("arguments[0].click();", show_more_button)
                    show_more_button = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, Xpath)))
                    time.sleep(3)
                    new_professor_Xpath = f"//*[@id='root']/div/div/div[4]/div[1]/div[1]/div[3]/a[{professor_idx}]"
                    new_professor_text = self.driver.find_element(By.XPATH, new_professor_Xpath).text
                    professor_attr_list = new_professor_text.split('\n')
                    new_prof_obj = RMPProfessor(professor_attr_list)
                    self.professors_list.append(new_prof_obj)
                    print(new_prof_obj)
                    continue
                except Exception as e:
                    print(e)
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

    # Add an argument '-config' or '--config' to specify the config file path if you want to use a config file
    # instead of specifying the arguments
    parser.add_argument(
        "-config", "--config",
        help="Specify the config file path if you want to use a config file instead of specifying the arguments",
        type=str)

    args = parser.parse_args()

    if args.config is not None:
        # If the arguments are not specified, use the config file
        if args.sid is None and config.sid is not None:
            args.sid = config.sid

        if args.file_path is None and config.file_path is not None:
            args.file_path = config.file_path

    # Instantiate the RMPSchool object
    rmp_school = RMPSchool(args.sid)