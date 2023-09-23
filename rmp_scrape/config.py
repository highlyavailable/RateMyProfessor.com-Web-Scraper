# Description: Example configuration file for rmp_scrape
# Path: rmp_scrape\config.py
import os

testing = True
# Selenium: Path to WebDriver
path_to_webdriver = os.path.join(os.getcwd(), "rmp_scrape", "chromedriver.exe")
sid = 1256  # University of Wisconsin-Madison SID
# sid = 1224 # CWRU SID
page_reload_timeout = 10 # 100 seconds
show_more_timeout = 10 # 10 seconds
file_path = 'all_professors.json'