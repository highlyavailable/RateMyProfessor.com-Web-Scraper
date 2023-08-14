__author__ = "Peter Bryant"
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"
__email__ = "pbryant2@wisc.edu"
__status__ = "Development"

# Standard library imports
import json
import time
import os
import argparse
import importlib

# Path to Chrome WebDriver
import rmp_scrape.driver_config as driver_config

# Selenium imports
from selenium import webdriver                                                  # Webdriver
from selenium.webdriver.common.by import By                                     # Find elements by
from selenium.webdriver.chrome.service import Service                           # Chrome service
from selenium.webdriver.support.ui import WebDriverWait                         # Wait for elements to load
from selenium.webdriver.support import expected_conditions as EC                # Expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException # Misc. exceptions

dev_path = 'C:\Program Files (x86)\chrome-win64\chrome.exe'
path_to_webdriver = driver_config.path_to_webdriver # Init global path to WebDriver

const_rmp_search_url = 'https://www.ratemyprofessors.com/search/professors/{sid}?q=*' # RMP professor search URL

class RateMyProf:
    """
    RateMyProf class contains functions to scrape professor data from RateMyProfessors.com
    """

    def __init__(self, school_id):
        """
        Constructor for RateMyProfApi class.
        Args: school_id (int): Unique School ID that RateMyProfessor assigns to identify each University.
        """
        self.school_id = school_id                            # Parameter for the school ID
        self.url = const_rmp_search_url.format(sid=self.school_id) # Query URL for the school ID
        self.options = webdriver.ChromeOptions() 
        self.options.binary_location = dev_path             # Create a new Chrome session
        self.options.headless = True

        # Ignore SSL certificate errors
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument('log-level=3')
        self.driver = None

        self.service = Service(path_to_webdriver) # Init Chrome service

    def num_professors(self, testing=False):
        """
        Returns the number of professor results for the given school_id.
        """

        if testing:
            print("-----------------num_professors()-------------------")
            start = time.time()

        # Check RMP page error
        try:
            Xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/div/div' # RMP error message Xpath
            element = self.driver.find_element(By.XPATH, Xpath)     # Find the error message element
            error_message = element.text.strip().replace("\n", "")  # Save the error message text
            error_string = 'No professors with "" in their name'    # Error message comp string
            
            # If the error message string is in the error message, return 0.
            if error_string in error_message:
                print(
                    "***WARNING: RateMyProfessors.com error, returned total number of professors on RMP. Reloading page...***")
                return 0
        # If the error message element is not found, continue.
        except:
            pass

        Xpath = '//h1[@data-testid="pagination-header-main-results"]' # Xpath for the number of professors
        element = self.driver.find_element(By.XPATH, Xpath)           # Find the element
        num_profs = int(element.text.split()[0])  # Save the number of professors (first word in the text)

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

        num_profs = 0 # Number of professors

        # Reload page until the number of professors is not 0 (RMP error)
        timeout = time.time()
        while True:
            self.driver = webdriver.Chrome(service=self.service, options=self.options) # Init Chrome driver
            self.driver.get(self.url) # Load the URL
            num_profs = self.num_professors(testing)  # Get the number of professors

            # If the number of professors is not 0, break out of the loop.
            if num_profs != 0:
                break
            # If the number of professors is 0, close the driver and try again.
            else:
                self.driver.quit() # Close the driver

                # If PAGE RELOAD TIMEOUT option is set
                if args.page_reload_timeout is not None:
                    # If PAGE RELOAD TIMEOUT has been reached, return false.
                    if timeout - time.time() >= args.page_reload_timeout:
                        if testing:
                            print("PAGE RELOAD TIMEOUT reached waiting for num_professors(). Returning False.")
                        return False

        if testing:
            print("-------------scrape_professors() cont.--------------")

        school_name_xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[1]/div/h1/span/b' # Xpath for the school name
        school_name = self.driver.find_element(By.XPATH, school_name_xpath).get_attribute('innerHTML') # Find the school name
        if testing:
            print("School name: ", school_name, "\n")
        # Click the show more button to load all professors

     
        times_pressed = 0                     # Number of times the show more button has been pressed
        timeout_show_more = time.time()       # Timeout for show more button
        show_more_button_xpath = '//*[@id="root"]/div/div/div[4]/div[1]/div[1]/div[4]/button'
        while self.driver.find_elements(By.XPATH, show_more_button_xpath):
            try:
                 # Show more button xpath

                # Wait for the show more button to be clickable, then click it.
                self.driver.execute_script("arguments[0].click();", WebDriverWait(
                    self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, show_more_button_xpath))))

                times_pressed += 1 # Increment the number of times the show more button has been pressed
                if testing:
                     print(f"Clicking 'Show More' button {times_pressed} times.")


            except TimeoutException as e:
                print(f"TimeoutException: {e}")


            except IndexError as e:
                print(f"IndexError: {e}")

        if testing:
            print("Done pressing 'Show More' button (pressed "+ str(times_pressed) + " times in " +
                  str(time.time() - timeout_show_more), " seconds.)...\n")

        # If the file path is specified, use that file path. Otherwise, use the default file path.
        if args.file_path is not None:
            file_path = args.file_path
        else:
            file_path = 'profs_from_' + school_name.replace(" ", "") + '.json'

        # If the destination file exists and is not empty, clear the file
        with open(file_path, 'a') as f:
            if testing:
                print("Creating file: '" + file_path + "'...")
            if os.stat(file_path).st_size != 0:
                print("'" + file_path + "' already exists. Clearing file...")
                f.truncate(0)
                if testing:
                    print("File cleared.\n")

        # Click the show more button until all professors are shown
        for i in range(1, num_profs):
            all_prof_dict = {}  # Dictionary to store all professor data
            prof_dict = {
                "Name": "",
                "School": "",
                "Department": "",
                "Rating": "",
                "NumRatings": "",
                "Difficulty": "",
                "WouldTakeAgain": ""
            }
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
                        "Encountered NoSuchElementException while scraping professor data at index " + str(i) + ". No longer scraping professor data.")
                    # print("Error: ", e)
                break

        self.driver.close()
        self.driver.quit()

        if testing:
            end = time.time()
            print(str(i-1) + " professors scraped and written to, '" +
                  file_path + "'.")
            print("scrape_professors() finished in ", end - start, " seconds.")
            print("----------------------------------------------------")

        return True


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":

    # Command line argument parser
    parser = argparse.ArgumentParser()

    # Add an argument '-t' or '--testing' to run the program in testing mode
    parser.add_argument(
        "-t", "--testing", help="Run the program in testing mode", type=str2bool, nargs='?',
        const=True)

    # Add an argument '-s' or '--sid' to specify the RMP school id
    parser.add_argument(
        "-s", "--sid", help="Specify the RMP school id", type=int)

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

    # print("args ", args)

    if args.config is not None:
        config = importlib.import_module(
            args.config)  # Load the config.py file

        # If the arguments are not specified, use the config file
        if args.sid is None and config.sid is not None:
            args.sid = config.sid

        if args.testing is None and config.testing is not None:
            args.testing = config.testing

        if config.page_reload_timeout is not None and args.page_reload_timeout is None:
            args.page_reload_timeout = config.page_reload_timeout

        if args.show_more_timeout is None and config.show_more_timeout is not None:
            args.show_more_timeout = config.show_more_timeout

        if args.file_path is None and config.file_path is not None:
            args.file_path = config.file_path

    # Required arguments check
    if args.sid is None:
        print("Error: No RMP school id specified.")
        print("Please specify the RMP school id using the -s or --sid argument.")
        print("Alternatively, you can specify the RMP school id in the config.py file.")
        exit(1)

    if args.testing is not None and args.testing:
        print("----------------------TESTING-----------------------")
        start = time.time()
        print("Arguments:")
        print("sid: ", args.sid)
        print("testing: ", args.testing)
        print("page_reload_timeout: ", args.page_reload_timeout)
        print("show_more_timeout: ", args.show_more_timeout)
        print("file_path: ", args.file_path)

    RateMyProf = RateMyProf(args.sid)
    RateMyProf.scrape_professors(args)

    if args.testing:
        end = time.time()
        print("Finished in ", end - start, " seconds.")
