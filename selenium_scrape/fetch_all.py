__author__ = "Peter Bryant"
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"

# Standard library imports
import requests
import json
import math

# Local imports
from professor import Professor

# Web scraping imports
import re
from bs4 import BeautifulSoup
from selenium import webdriver
# Give access to "enter" and "space" key to
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

service = Service("C:\Program Files (x86)\chromedriver.exe")  # Path to WebDriver

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

    def num_professors(self, testing=False):
        """
        Returns the number of professor results for the given school_id.
        """
        url = 'https://www.ratemyprofessors.com/search/teachers?query=*&sid=' + \
            str(self.school_id)

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('log-level=3')

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)                  # Navigate to the page

        Xpath='//h1[@data-testid="pagination-header-main-results"]'

        element = driver.find_element(By.XPATH, Xpath)

        # Save the first word from the element text, which is the number of professors.
        num_profs = element.text.split()[0]

        driver.close()  # Close the browser
        driver.quit()  # Quit the WebDriver and close all associated windows


        return int(num_profs)

    def scrape_professors(self, testing=False):
        """
        Scrapes all professors from the school with the given school_id. 
        Return: a list of Professor objects, defined in professor.py.
        """
        if testing:
            print("-------ScrapeProfessors--------")
            print("Scraping professors from RateMyProfessors.com...")
            print("University SID: ", self.school_id)

        professors = dict()

        # The number of professors with RMP records associated with this university school_id.
        num_of_prof = self.num_professors()

        if testing:
            print("Number of Professors Total: ", num_of_prof)

        url = 'https://www.ratemyprofessors.com/search/teachers?query=*&sid=' + \
            str(self.school_id)

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('log-level=3')

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)                  # Navigate to the page

        Xpath='//h1[@data-testid="pagination-header-main-results"]'

        element = driver.find_element(By.XPATH, Xpath)

        return 0
        for i in range(1, num_of_pages + 1):  # the loop insert all professor into list

           
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

        if testing:
            print("Professors actually added: ", str(len(professors)))

        return professors


if __name__ == "__main__":
    # # Testing
    uw_school_id_1 = RateMyProfApi(1256)
    uw_school_id_1.scrape_professors(testing=True)

    # uw_school_id_2 = RateMyProfApi(18418)
    # uw_school_id_2.scrape_professors(testing=False)
