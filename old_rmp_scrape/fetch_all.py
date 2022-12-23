__author__ = "Peter Bryant, Jarvis Jia"
__credits__ = ["Peter Bryant", "Jarvis Jia", "Bryan Li", "Swathi Annamaneni", "Aidan Shine"]
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"

import requests
import json
import math
from .professor import Professor

class RateMyProfApi:
    """
    RateMyProfAPI class contains functions to scrape professor data from RateMyProfessors.com
    """
    def __init__(self, school_id):
        """
        Constructor for RateMyProfApi class.
        Args: school_id (int): UID that RateMyProfessor assigns to identify schools.
        """
        self.UniversityId = school_id
        

    def scrape_professors(self, testing = False): 
        """
        Scrapes all professors from the school with the given school_id. 
        Return: a list of Professor objects, defined in professor.py.
        """
        if testing:
            print("-------ScrapeProfessors--------")
            print("Scraping professors from RateMyProfessors.com...")
            print("University ID: ", self.UniversityId)
        
        professors = dict() 
        num_of_prof = self.NumProfessors() # The number of professors with RMP records associated with this university school_id.
        
        if testing:
            print("Number of Professors Total: ", num_of_prof)

        num_of_pages = math.ceil(num_of_prof/20)   # The API returns 20 professors per page.
        for i in range(1, num_of_pages + 1):  # the loop insert all professor into list
            
            # first RMP seed 1256
            if self.UniversityId == '1256':
                page = requests.get(
                    "http://www.ratemyprofessors.com/filter/professor/?&page="
                    + str(i)
                    + "&queryoption=TEACHER&query=*&sid="
                    + str(self.UniversityId)
                )
            
            # second RMP seed 18418
            else:
                page = requests.get(
                    "http://www.ratemyprofessors.com/filter/professor/?&page="
                    + str(i)
                    + "&queryoption=TEACHER&queryBy=schoolId&sid="
                    + str(self.UniversityId)
                )
            
            json_response = json.loads(page.content)

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

    def NumProfessors(self):
        """
        Helper function to get the number of professors in the school with the given school_id.
        """
        if self.UniversityId == '1256':
            # first RMP seed 1256
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page=1&queryoption=TEACHER&queryBy=schoolId&sid="
                + str(self.UniversityId)
            )
        else: 
            # second RMP seed 18418
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page=1&queryoption=TEACHER&query=*&sid="
                + str(self.UniversityId)
            )

        temp_jsonpage = json.loads(page.content)
        num_of_prof = (temp_jsonpage["searchResultsTotal"]) 
        return num_of_prof

