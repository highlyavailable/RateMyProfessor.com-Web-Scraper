__author__ = "Peter Bryant"
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"
__email__ = "pbryant2@wisc.edu"
__status__ = "Development"

# Standard library imports
import requests
import json
import math
import time
import os
import sys
import argparse
import importlib

# Local imports
from professor import Professor

# Web scraping imports
import re                                               # Regular expressions
from bs4 import BeautifulSoup                           # BeautifulSoup
from selenium import webdriver                          # Selenium
from selenium.webdriver.common.keys import Keys         # Selenium: Keyboard keys
# Selenium: Find elements by
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service   # Selenium: Path to WebDriver
# Selenium: Wait for page to load
from selenium.webdriver.support.ui import WebDriverWait
# Selenium: Expected conditions for page load
from selenium.webdriver.support import expected_conditions as EC
# Selenium: Timeout exception
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Selenium: Path to WebDriver
path_to_webdriver = "C:\Program Files (x86)\chromedriver.exe"

# Command line argument parser
parser = argparse.ArgumentParser()

# Add an argument '-t' or '--testing' to run the program in testing mode
parser.add_argument(
    "-t", "--testing", help="Run the program in testing mode", action="store_true")

# Add an argument '-s' or '--sid' to specify the RMP school id
parser.add_argument(
    "-s", "--sid", help="Specify the RMP school id", type=int, default=-1)

# Add an argument '-prt' or '--page_reload_timeout' to specify the timeout for reloading the RMP page
parser.add_argument(
    "-prt", "--page_reload_timeout", help="Specify the timeout for reloading the RMP page", type=int)

# Add an argument '-smt' or '--show_more_timeout' to specify the timeout for clicking the show more button
parser.add_argument(
    "-smt", "--show_more_timeout", help="Specify the timeout for clicking the show more button", type=int)

# Add an argument '-f' or '--file_path' to specify the file path to store the scraped data
parser.add_argument(
    "-f", "--file_path", help="Specify the file path to store the scraped data", type=str)

# Add an argument '-config' or '--config' to specify the config file path if you want to use a config file instead of specifying the arguments
parser.add_argument(
    "-config", "--config", help="Specify the config file path if you want to use a config file instead of specifying the arguments", type=str)

args = parser.parse_args()

class RateMyProfApi:
    """
    RateMyProfAPI class contains functions to scrape professor data from RateMyProfessors.com
    """

    def __init__(self, school_id):
        """
        Constructor for RateMyProfApi class.
        Args: school_id (int): Unique School ID that RateMyProfessor assigns to identify each University.
        """
        self.school_id = school_id  # Parameter for the school ID

        self.url = 'https://www.ratemyprofessors.com/search/teachers?query=*&sid=' + \
            str(self.school_id)

        self.options = webdriver.ChromeOptions()  # Create a new Chrome session

        # Ignore SSL certificate errors
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument('log-level=3')  # Ignore warnings

        # Path to WebDriver
        self.service = Service(path_to_webdriver)

    def num_professors(self, testing=False):
        """
        Returns the number of professor results for the given school_id.
        """

        if testing:
            print("-----------------num_professors()-------------------")
            start = time.time()

        # Check RMP page error
        try:
            # RMP error message Xpath
            Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/div/div'
            # Find the error message element
            element = self.driver.find_element(By.XPATH, Xpath)
            error_message = element.text.strip().replace(
                "\n", "")  # Save the error message text
            # Error message string to check for
            error_string = 'No professors with "" in their name'
            # If the error message string is in the error message, return 0.
            if error_string in error_message:
                print(
                    "***WARNING: RateMyProfessor error, returned total number of professors on RMP. Reloading page...***")
                return 0
        except:
            pass

        # Find the number of professors
        Xpath = '//h1[@data-testid="pagination-header-main-results"]'
        element = self.driver.find_element(By.XPATH, Xpath)

        # Save the first word from the element text, which is the number of professors.
        num_profs = int(element.text.split()[0])

        if testing:
            end = time.time()
            print("Number of professors: ", num_profs)
            print("num_professors() finished in ", end - start, " seconds.")
        return num_profs

    def scrape_professors(self, args):
        """
        Scrapes all professors from the school with the given school_id and populates a JSON file with the data.
        Return: true if successful, false if not.
        """
        testing = args.testing  # Testing mode
        
        if testing:
            print("-----------------scrape_professors()----------------")

            print("Scraping professors from RateMyProfessors.com at \nURL: ", self.url)
            print("University SID: ", self.school_id)
            start = time.time()

        # Number of professors with RMP records associated with the given university SID.
        num_profs = 0

        # Reload page until the number of professors is not 0.
        timeout = time.time()
        while True:
            # Create a new instance of the Chrome driver
            self.driver = webdriver.Chrome(
                service=self.service, options=self.options)
            self.driver.get(self.url)  # Navigate to the page
            num_profs = self.num_professors(testing)

            # If the number of professors is not 0, break out of the loop.
            if num_profs != 0:
                break

            # If the number of professors is 0, close the driver and try again.
            else:
                self.driver.quit()                      # Close the driver

                # Page reload timeout:
                # If the page reload timeout option is set
                if args.page_reload_timeout != None:
                    # If the timeout has been reached, return false.
                    if timeout - time.time() >= args.page_reload_timeout:
                        if testing:
                            print(
                                "Timeout error waiting for num_professors(). Retrying num_professors()...")
                        return False

        if testing:
            print("-------------scrape_professors() cont.--------------")

         # Xpath to the school name
        school_name_xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/h1/span/b'

        # Find the professor's school
        school_name = self.driver.find_element(
            By.XPATH, school_name_xpath).get_attribute('innerHTML')

        # Click the show more button to load all professors
        if testing:
            print("School name: ", school_name)
            print("Clicking 'Show More' button...")

        times_pressed = 0
        timeout_show_more = time.time()  # Timeout for show more button

        # Number of times the 'Show More' button should be pressed
        # (total number of professors found - first 8 professors) // (professors per page load)
        num_press_show_more = (num_profs - 8) // 8

        show_more_timeout_exception_count = 0  # Number of times the show more timeout has been reached
        while num_press_show_more:
            try:
                # Show more button
                show_more_button_xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
                # show_more_button = self.driver.find_element(By.XPATH, show_more_button_xpath)  # Find the show more button
                self.driver.execute_script("arguments[0].click();", WebDriverWait(
                    self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, show_more_button_xpath))))

                times_pressed += 1
                num_press_show_more -= 1

                if args.show_more_timeout != None:
                    if time.time() - timeout_show_more >= args.show_more_timeout:
                        print(
                            "Show more timeout reached when waiting for 'Show More' button.")
                        break

            except TimeoutException as e:
                show_more_timeout_exception_count += 1
                if show_more_timeout_exception_count >= 3:
                    print(
                        "Show more timeout exception max count reached (3). Breaking out of 'Show More' loop.")
                    break
                if testing:
                    print(
                        "Encountered Selenium TimeoutException when pressing 'Show More'.")
                    print("Retrying pressing 'Show More'....")

            except IndexError as e:
                if testing:
                    print("Encountered IndexError while pressing 'Show More'.")
                break

        if testing:
            print("Done pressing 'Show More' button (pressed "+str(times_pressed) + " times in " +
                  str(time.time() - timeout_show_more), " seconds.)...")

        # If the file path is specified, use that file path. Otherwise, use the default file path.
        if args.file_path != None:
            file_path = args.file_path
        else:
            file_path = 'profs_from_' + school_name.replace(" ", "") + '.json'

        # If the destination file exists and is not empty, clear the file
        with open(file_path, 'a') as f:
            if os.stat(file_path).st_size != 0:
                f.truncate(0)

        # Click the show more button until all professors are shown
        for i in range(1, num_profs):
            all_prof_dict = {}  # Dictionary to store all professor data
            prof_dict = {}  # Dictionary to store professor data
            prof_dict["Name"] = ""
            prof_dict["School"] = ""
            prof_dict["Department"] = ""
            prof_dict["Rating"] = ""
            prof_dict["NumRatings"] = ""
            prof_dict["Difficulty"] = ""
            prof_dict["WouldTakeAgain"] = ""

            try:
                # Xpath to the unique professor card
                prof_card_div = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[3]/a[' + str(
                    i) + ']'

                # 1. Professor's School
                # Xpath to the professor's school
                prof_school_xpath = prof_card_div + '/div/div[2]/div[2]/div[2]'
                # Find the professor's school
                prof_dict['School'] = self.driver.find_element(
                    By.XPATH, prof_school_xpath).get_attribute('innerHTML')

                # If the professor's school is not the same as the school name corresponding to the school_id, skip the professor.
                if prof_dict['School'] != school_name:
                    continue

                # 2. Professor's Rating
                # Xpath to the professor's rating
                prof_rating_xpath = prof_card_div + '/div/div[1]/div/div[2]'
                # Find the professor rating card
                prof_dict['Rating'] = self.driver.find_element(
                    By.XPATH, prof_rating_xpath).get_attribute('innerHTML')

                # 3. Professor's Number of Ratings
                # Xpath to the professor's number of ratings
                prof_num_rating_xpath = prof_card_div + \
                    '/div/div[1]/div/div[3]'
                # Find the professor's number of ratings
                prof_dict['NumRatings'] = self.driver.find_element(
                    By.XPATH, prof_num_rating_xpath).get_attribute('innerHTML')

                # 4. Professor's Name
                # Xpath to the professor's name
                prof_name_xpath = prof_card_div + '/div/div[2]/div[1]'
                # Find the professor's name
                prof_dict['Name'] = self.driver.find_element(
                    By.XPATH, prof_name_xpath).get_attribute('innerHTML')

                # 5. Professor's Department
                # Xpath to the professor's department
                prof_department_xpath = prof_card_div + \
                    '/div/div[2]/div[2]/div[1]'
                # Find the professor's department
                prof_dict['Department'] = self.driver.find_element(
                    By.XPATH, prof_department_xpath).get_attribute('innerHTML')

                # 6. Professor's Difficulty
                # Xpath to the professor's Difficulty
                prof_difficulty_xpath = prof_card_div + \
                    '/div/div[2]/div[3]/div[3]/div'
                # Find the professor's Difficulty
                prof_dict['Difficulty'] = self.driver.find_element(
                    By.XPATH, prof_difficulty_xpath).get_attribute('innerHTML')

                # 7. Professor's Would Take Again
                # Xpath to the professor's Would Take Again
                prof_WTA_xpath = prof_card_div + \
                    '/div/div[2]/div[3]/div[1]/div'
                # Find the professor's Difficulty
                prof_dict['WouldTakeAgain'] = self.driver.find_element(
                    By.XPATH, prof_WTA_xpath).get_attribute('innerHTML')

                all_prof_dict[i] = prof_dict

                all_prof_json = json.dumps(all_prof_dict)

                # Write to file in JSON format 'all-professors.json'
                with open(file_path, 'a') as f:
                    f.write(all_prof_json)  # Write the JSON to the file
                    # Add a comma and newline to separate each professor
                    f.write(",\n")

            except NoSuchElementException as e:
                if testing:
                    print(
                        "Encountered NoSuchElementException while scraping professor data at index " + str(i) + ".")
                    print("No longer scraping professor data.")
                    print("Error: ", e)
                break

        self.driver.close()
        self.driver.quit()

        if testing:
            end = time.time()
            print("scrape_professors() finished in ", end - start, " seconds.")
            print("----------------------------------------------------")

        return True


if __name__ == "__main__":

    if args.config is not None:
        config = importlib.import_module(
            args.config)  # Load the config.py file

        # Set the arguments to the values specified in the config file if the argument is not specified in the command line
        if config.sid is not None and args.sid == -1:
            args.sid = config.sid

        if config.testing is not None and args.testing is False:
            args.testing = config.testing

        if config.page_reload_timeout is not None and args.page_reload_timeout is None:
            args.page_reload_timeout = config.page_reload_timeout

        if config.show_more_timeout is not None and args.show_more_timeout is None:
            args.show_more_timeout = config.show_more_timeout

        if config.file_path is not None and args.file_path is None:
            args.file_path = config.file_path

    # Required arguments check
    if args.sid == -1:
        print("Error: No RMP school id specified.")
        print("Please specify the RMP school id using the -s or --sid argument.")
        print("Alternatively, you can specify the RMP school id in the config.py file.")
        exit(1)

    if args.testing:
        print("----------------------TESTING-----------------------")
        start = time.time()

    RateMyProf = RateMyProfApi(args.sid)
    RateMyProf.scrape_professors(args)

    if args.testing:
        end = time.time()
        print("Finished in ", end - start, " seconds.")
