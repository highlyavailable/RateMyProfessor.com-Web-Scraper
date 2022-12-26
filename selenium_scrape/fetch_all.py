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

# Configuration imports
import config


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
        self.service = Service(config.path_to_webdriver)

    def num_professors(self, testing=False):
        """
        Returns the number of professor results for the given school_id.
        """

        if testing:
            print("-----------------num_professors()-------------------")
            start = time.time()

        # Check RMP page error
        try:
            Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/div/div'
            element = self.driver.find_element(By.XPATH, Xpath)
            error_message = element.text.strip().replace("\n", "")
            error_string = 'No professors with "" in their name'
            if error_string in error_message:
                print(
                    "***WARNING: RateMyProfessor error, returned total number of professors on RMP. Returning error code 0.***")
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
            print("----------------------------------------------------")
        return num_profs

    def scrape_professors(self, testing=False):
        """
        Scrapes all professors from the school with the given school_id and populates a JSON file with the data.
        Return: true if successful, false if not.
        """
        if testing:
            print("-----------------scrape_professors()----------------")

            print("Scraping professors from RateMyProfessors.com at \nURL: ", self.url)
            print("University SID: ", self.school_id)
            start = time.time()

        # Number of professors with RMP records associated with the given university SID.
        num_profs = 0

        # Restart scrape_professors() if the number of professors is 0.
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

                # If the function takes more than 3 minutes to return a non-zero value, return false.
                if timeout - time.time() > 180:
                    if testing:
                        print(
                            "Timeout error waiting for num_professors(). Returning false.")
                        return False

                print("Retrying num_professors()...")

        if testing:
            print("-------------scrape_professors() cont.--------------")

        # Show more button
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
        element = self.driver.find_element(
            By.XPATH, Xpath)  # Find the show more button

        # Click the show more button until all professors are shown
        while True:
            try:
                element.click()
            except:
                break

        # All professor div with professor cards
        Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[3]'
        element = self.driver.find_element(
            By.XPATH, Xpath)  # Find the show more button
        professor_div = element.get_attribute('innerHTML')

        professor_div_a_tags = BeautifulSoup(
            professor_div, 'html.parser').find_all('a')  # Get all a tags
        for i in range(1, len(professor_div_a_tags)):
            print(professor_div_a_tags[i]['href'])
            Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[3]/a[' + str(i) + ']/div/div[2]/div[1]'

            element = self.driver.find_element(
                By.XPATH, Xpath)  # Find the professor name
            professor_name = element.get_attribute('innerHTML')
            print(professor_name)

        if testing:
            print("Number of professors <a> tags: ", len(professor_div_a_tags))

        # Get the HTML of the page
        html = self.driver.page_source

        self.driver.close()
        self.driver.quit()

        if testing:
            end = time.time()
            print("scrape_professors() finished in ", end - start, " seconds.")
            print("----------------------------------------------------")

        return True

        # iterate through the professor
        for json_professor in json_response["professors"]:

            # load in professor information
            professor = Professor(
                json_professor["tid"],
                json_professor["tFname"],
                json_professor["tLname"],
                json_professor["tNumRatings"],
                json_professor["overall_rating"],
                json_professor["rating_class"],
                json_professor["tDept"]
            )

            professors[professor.ratemyprof_id] = professor

        return professors


if __name__ == "__main__":
    testing = True
    if testing:
        print("----------------------TESTING-----------------------")
        start = time.time()
    uw_school_id_1 = RateMyProfApi(config.sid)
    uw_school_id_1.scrape_professors(testing=testing)

    if testing:
        end = time.time()
        print("Finished in ", end - start, " seconds.")
