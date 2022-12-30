# RateMyProfessor.com-Web-Scraper
A Python script that uses Selenium to scrape professor ratings from [RateMyProfessors.com](https://www.ratemyprofessors.com/) and saves them to a JSON file.

## Requirements
- Python 3.6+
- Selenium
- ChromeDriver

## Usage
Using the script is simple but requires the user to already have the `sid`, that is the unique school ID, of the school they want to scrape as assigned by RateMyProfessors.com. The `sid` can be found by searching for the school on RateMyProfessors.com and looking at the URL. For example, the `sid` for the University of Wisconsin-Madison is `1256` and can be found in the URL `https://www.ratemyprofessors.com/search/teachers?query=*&sid=1256`. I want to point out that the  `sid` should be a unique identifier for the university, however, I have found that some universities have multiple. For example, the University of Wisconsin-Madison has `1256` and `18418`. I have not found any other universities with multiple `sid`s, but if you find one, please let me know. In the meantime have reached out to RateMyProfessors.com to see if they can clarify this issue.

Once you have the `sid`, you have a few options to run the script from command line with arguments specified using the following flags:

### Required Arguments
- `-s` or `--sid`: The `sid` of the school you want to scrape. 

### Optional Arguments
- `-config` or `--config`: The config file path if you want to use a config file instead of specifying the arguments.  
- `-f` or `--file_path`: The file path to store the scraped data.
- `-prt` or `--page_reload_timeout`: The timeout for reloading the RMP page.
- `-smt` or `--show_more_timeout`: The timeout for clicking the show more button.

You have the option to run the script directly from the command line by specifying which arguments you want to use, but only the `sid` argument is required. If you do not specify the `file_path` argument, the script will save the scraped data to a file named `profs_from_YourSchoolName.json` in the project directory. 

The `page_reload_timeout` and `show_more_timeout` arguments are options that I have added to help with the scraping process. The `page_reload_timeout` argument is used to specify how many seconds the script should wait while trying to load the page at [www.ratemyprofessors.com/search/teachers?query=*&sid=YourSID](https://www.ratemyprofessors.com/search/teachers?query=*&sid=YourSID). For some reason while working on this script, I noticed that the page would sometimes not load properly. This would cause the script to fail to find the 'Show More' button and would result in the script not scraping any data. The `page_reload_timeout` argument allows the user to specify how many seconds the script should wait before reloading the page. Whereas most of the time you visit this page, you will see a reasonable amount of professors for a given school, like so:

On other occasions, you will see a page that looks like this despite the fact that you are requesting the same page (even if for you are requesting this page for the first time).

To combat this I added the `page_reload_timeout` command line argument that will let you designate how many seconds you want to wait for the correct page to load. This is not optimal, but I assume it is a probably with RateMyProfessors.com's internals and is only used so that the script is functional.

 It also seems RateMyProfessors.com runs into some issues when a user presses the 'Show More' button at the bottom of the professor's list for a given school (e.g. [www.ratemyprofessors.com/search/teachers?query=*&sid=1256](https://www.ratemyprofessors.com/search/teachers?query=*&sid=1256). After pressing the 'Show More' button the site will on occasion load the page with professors at a different school than the one corresponding to the given `sid`. For example, here is a screenshot of the page after accessing the professors for the University of Wisconsin-Madison and then pressing the 'Show More' button four times. As you can see, the page is now showing a professor from Grand Valley State University, and subsequent presses will show professors from other schools. As a temporary fix, I have added the `show_more_timeout` argument to allow the user to specify how many seconds the script should continue pressing the 'Show More' button before the script scrapes the data from the page. This fix is not optimal, as after the page is filled with a lot of professors, the script must check what school the professor is from before writing the data to the JSON file. 

1. Install the requirements by running `pip3 install -r requirements.txt` in the project directory.
2. Run `python3 rmp_scrape/fetch.py` to scrape the data.


