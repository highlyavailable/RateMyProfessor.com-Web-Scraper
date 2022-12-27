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

        # Click the show more button until all professors are shown
        for i in range(1, num_profs):
            prof_dict = {}  # Dictionary to store professor data
            prof_dict["Name"] = ""
            prof_dict["School"] = ""
            prof_dict["Department"] = ""
            prof_dict["Rating"] = ""
            prof_dict["NumRatings"] = ""
            prof_dict["Difficulty"] = ""
            prof_dict["WouldTakeAgain"] = ""

            try:
                # 1. Professor's Rating
                # Xpath to the unique professor card
                prof_card_div = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[3]/a[' + str(i) + ']'
                # Xpath to the professor's rating
                prof_rating_xpath = prof_card_div + '/div/div[1]/div/div[2]'
                # Find the professor rating card
                prof_dict['Rating'] = self.driver.find_element(By.XPATH, prof_rating_xpath).get_attribute('innerHTML')

                # 2. Professor's Number of Ratings
                # Xpath to the professor's number of ratings
                prof_num_rating_xpath = prof_card_div + '/div/div[1]/div/div[3]'
                # Find the professor's number of ratings
                prof_dict['NumRatings'] = self.driver.find_element(By.XPATH, prof_num_rating_xpath).get_attribute('innerHTML')

                # 3. Professor's Name
                # Xpath to the professor's name
                prof_name_xpath = prof_card_div + '/div/div[2]/div[1]'
                # Find the professor's name
                prof_dict['Name'] = self.driver.find_element(By.XPATH, prof_name_xpath).get_attribute('innerHTML')

                # 4. Professor's Department
                # Xpath to the professor's department
                prof_department_xpath = prof_card_div + '/div/div[2]/div[2]/div[1]'
                # Find the professor's department
                prof_dict['Department'] = self.driver.find_element(By.XPATH, prof_department_xpath).get_attribute('innerHTML')

                # 5. Professor's School
                # Xpath to the professor's school
                prof_school_xpath = prof_card_div + '/div/div[2]/div[2]/div[2]'
                # Find the professor's school
                prof_dict['School'] = self.driver.find_element(By.XPATH, prof_school_xpath).get_attribute('innerHTML')

                # 6. Professor's Difficulty
                # Xpath to the professor's Difficulty
                prof_difficulty_xpath = prof_card_div + '/div/div[2]/div[3]/div[3]/div'
                # Find the professor's Difficulty
                prof_dict['Difficulty'] = self.driver.find_element(By.XPATH, prof_difficulty_xpath).get_attribute('innerHTML')

                # 7. Professor's Would Take Again
                # Xpath to the professor's Would Take Again
                prof_WTA_xpath = prof_card_div + '/div/div[2]/div[3]/div[1]/div'
                # Find the professor's Difficulty
                prof_dict['WouldTakeAgain'] = self.driver.find_element(By.XPATH, prof_WTA_xpath).get_attribute('innerHTML')

                print(prof_dict)

                # If i is a multiple of 8, 
                if i % 8 == 0:
                    # Show more button
                    show_more_button_xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
                    show_more_button = self.driver.find_element(By.XPATH, show_more_button_xpath)  # Find the show more button
                    show_more_button.click()
                    print("Clicked show more button.")

            except Exception as e:
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
    testing = True

    if testing:
        print("----------------------TESTING-----------------------")
        start = time.time()

    uw_school_id_1 = RateMyProfApi(config.sid)
    uw_school_id_1.scrape_professors(testing=testing)

    if testing:
        end = time.time()
        print("Finished in ", end - start, " seconds.")
