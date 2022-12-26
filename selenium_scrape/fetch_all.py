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

# Path to WebDriver
service = Service("C:\Program Files (x86)\chromedriver.exe")


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

        Xpath = '//h1[@data-testid="pagination-header-main-results"]'

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

        element = driver.find_element(
            By.CLASS_NAME, 'TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx')

        print(element.text)

        # <a class="TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx" href="/professor?tid=47"><div class="TeacherCard__InfoRatingWrapper-syjs0d-3 kcbPEB"><div class="TeacherCard__NumRatingWrapper-syjs0d-2 joEEbw"><div class="CardNumRating__StyledCardNumRating-sc-17t4b9u-0 eWZmyX"><div class="CardNumRating__CardNumRatingHeader-sc-17t4b9u-1 fVETNc">QUALITY</div><div class="CardNumRating__CardNumRatingNumber-sc-17t4b9u-2 gcFhmN">4.1</div><div class="CardNumRating__CardNumRatingCount-sc-17t4b9u-3 jMRwbg">38 ratings</div></div></div><div class="TeacherCard__CardInfo-syjs0d-1 fkdYMc"><div class="CardName__StyledCardName-sc-1gyrgim-0 cJdVEK">John Swain</div><div class="CardSchool__StyledCardSchool-sc-19lmz2k-2 gSTNdb"><div class="CardSchool__Department-sc-19lmz2k-0 haUIRO">Physics</div><div class="CardSchool__School-sc-19lmz2k-1 iDlVGM">Northeastern University</div></div><div class="CardFeedback__StyledCardFeedback-lq6nix-0 frciyA"><div class="CardFeedback__CardFeedbackItem-lq6nix-1 fyKbws"><div class="CardFeedback__CardFeedbackNumber-lq6nix-2 hroXqf">100%</div> would take again</div><div class="VerticalSeparator-sc-1l9ngcr-0 enhFnm"></div> <div class="CardFeedback__CardFeedbackItem-lq6nix-1 fyKbws"><div class="CardFeedback__CardFeedbackNumber-lq6nix-2 hroXqf">2</div> level of difficulty</div></div></div></div><button class="TeacherBookmark__StyledTeacherBookmark-sc-17dr6wh-0 kebbUY" type="button"><img src="/static/media/bookmark-default.b056b070.svg" alt="Bookmark" data-tooltip="true" data-tip="Save Professor" data-for="GLOBAL_TOOLTIP" currentitem="false"></button></a>

        return 0

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
