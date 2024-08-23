from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from bs4 import BeautifulSoup
from pym3u8downloader import M3U8Downloader
import time
import re
import os
import requests

# Set up the Selenium WebDriver
service = Service('./chromedriver.exe')  # Update the path to your ChromeDriver
# options = webdriver.ChromeOptions()# options.add_argument("--headless")  # Run in headless mode

options = webdriver.ChromeOptions()

# Option to set the default download directory
# Set the download directory to "twly-meeting-fetchers/output_text_record"
download_dir = os.path.join(os.getcwd(), "output_text_record")
os.makedirs(download_dir, exist_ok=True)  # Ensure the directory exists
prefs = {
    "download.default_directory": download_dir,  # Set default download directory
    "download.prompt_for_download": False,       # Disable download prompt
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True   # Automatically open PDF files externally
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=service, options=options)
# driver = webdriver.Edge(options=options)
# URL to crawl
url = 'https://ppg.ly.gov.tw/ppg/sittings/2024022730/details?meetingDate=113/03/01&meetingTime=&departmentCode=null'

driver.get(url)
# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find and print text content
text_content = soup.get_text()
print(text_content)
if "公報紀錄" in text_content:
    print("true")
else:
    print("false")
count = text_content.count("會議影片")
print(f"Number of '會議影片': {count}")
# index = 1
# while True:
#     print(f'index: {index}')
#     try:
#         video_link = driver.find_element(By.CSS_SELECTOR, f'#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child({index}) > span > a')
#         text_link = driver. find_element(By.CSS_SELECTOR, '#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > div > span:nth-child(2) > span > a')
#         #section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child(3) > span > a
#         #section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > div > span:nth-child(2) > span > a
#         print(video_link.text)
#         print(text_link.text)
#         # if "會議影片" not in video_link.text:
#         #     print(f'wrong: {video_link.text}')
#         #     break
#         index+=1
#     except Exception:
#         print(f'wrong index: {index}')
#         break
           
      