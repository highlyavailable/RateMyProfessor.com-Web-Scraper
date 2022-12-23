__author__ = "Peter Bryant, Jarvis Jia"
__credits__ = ["Peter Bryant", "Jarvis Jia", "Bryan Li", "Swathi Annamaneni", "Aidan Shine"]
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"

import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re

def scrape_courses():
    """
    Function to scrapes course data from the UW-Madison course guide page and stores them in the all-courses.json file
    within the parent directory. The data includes:
        - Course Name
        - Course Subject
        - Course Code
        - Course Credits
        - Course Description
        - Course Prerequisites

    Args:
        None
    
    Returns:
        None: The function does not return anything, but it does write to the all-courses.json file.

    Notes:
        - This function produces a static file that is used by the rest of the application. It is not meant to be called
        by the user. It should be called atleast every semester to update the course data.

    """

    # Set up the url from UW-Madison course guide page 
    url = 'https://guide.wisc.edu/courses/'

    # scrape the overall data from request
    data = requests.get(url)

    my_data = []

    # beautiful soup package to scrape the page
    soup = BeautifulSoup(data.text, 'html.parser')

    # select the articles from page
    articles = soup.select('p')

    # main website information list
    weblist = []

    # open a file to store the course information
    open("all-courses.json", 'w').close()

    # find courses web link
    myuls = soup.findAll('ul', attrs={"class":"nav levelone"})

    for ul in myuls: 
        for link in ul.find_all('a'):
            weblist.append(link.get('href'))

    # get course subject name
    subjectList = []

    for ul in myuls: 
        for link in ul.find_all('a'):
            subjectList.append(link.get_text().split(" (")[0])

    # concat webname to get real link
    webname_count_subject = 0

    # each course dictionary to hold course info
    current_dict = {}

    # Loop through each course
    for webname in weblist: 

        url = 'https://guide.wisc.edu' + webname
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        # i counts each course
        i = 0
        # j counts each subject
        j = 0
        
        # count is used to indicate one course finished
        count = 0

        for link in soup.find_all('p'):
            if 'Last Taught' in link.get_text().replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\u2014', u''):
                count = count + 1

        #find the informatin we want,like description, credits, name, last taught
        for link in soup.find_all('p'):
            
            i = i + 1

            # get the course code, name and subject
            if i == 1:
                # replace every chaotic character by html
                courses = link.get_text().replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\n', u'').replace(u'\u2014', u'').split("  ", 1)
                courseCode = re.split('(\d+)',courses[0]) #use re to split character and strings
                current_dict[f'{webname[9:-1]} {j}'] = {}
                current_dict[f'{webname[9:-1]} {j}']['code'] = courseCode[0].replace(u'\xa0', u' ') + courseCode[1]
                current_dict[f'{webname[9:-1]} {j}']['name'] = courses[1]
                current_dict[f'{webname[9:-1]} {j}']['subject'] = subjectList[webname_count_subject]

            # get the credit information
            if i == 2 : 
                current_dict[f'{webname[9:-1]} {j}']['credits'] = link.get_text().replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\u2014', u'')[:-1]

            # get the course description
            if i == 3 : 
                current_dict[f'{webname[9:-1]} {j}']['description'] = link.get_text().replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\n', u'').replace(u'\u2014', u'')
            
            # get the course requisite
            if i == 4 : 
                current_dict[f'{webname[9:-1]} {j}']['requisite'] = link.get_text().replace("Requisites: ", "").replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\u2014', u'')


            # get the course last taught information
            if 'Last Taught' in link.get_text().replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\u2014', u''):
                current_dict[f'{webname[9:-1]} {j}']['last taught'] = link.get_text().replace(u'\xa0', u'').replace(u'\u200b', u'').replace(u'\xa9', u'').replace(u'\u2022', u'').replace(u'\u2014', u'')
                i = 0
                j = j + 1
            
            if j == count:
                break
                #close the file after attaching        
        webname_count_subject = webname_count_subject + 1

    # write into the file and close
    with open("all-courses.json", "a") as outfile:
        json.dump(current_dict,  outfile, indent = 4)
    outfile.close()


if __name__ == '__main__':
    scrape_courses()
    