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
# service = Service('./chromedriver.exe')  # Update the path to your ChromeDriver
# options = webdriver.ChromeOptions()# options.add_argument("--headless")  # Run in headless mode

options = webdriver.EdgeOptions()

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
# driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Edge(options=options)
# URL to crawl
url = 'https://ppg.ly.gov.tw/ppg/#section-2'

# Open the URL
driver.get(url)

def download_file(href_main):
    try:
        wait = WebDriverWait(driver, 20)
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text_content = soup.get_text()
        # print(text_content)
        if "公報紀錄" in text_content:

            video_count = text_content.count("會議影片")
            pdf_link = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > div > span:nth-child({video_count+1}) > span > a')
                ))

                # Click the PDF link to initiate the download
            pdf_link.click()
            print("PDF download initiated.")
            
            time.sleep(2)
            # try:
            
            #section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child(1) > span > a
            #section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > div > span:nth-child(2) > span > a
            #section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child(2) > span > a
            for i in range(video_count):

                video_link = driver.find_element(By.CSS_SELECTOR, f'#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child({i+1}) > span > a')
                print(video_link.text)
                if "會議影片" not in video_link.text:
                    print(f'wrong: {video_link.text}')
                    break
            
            
                video_link = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, f'#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > span:nth-child({i+1}) > span > a')
                    ))
                
                href = video_link.get_attribute('href')
            
                    # driver.get(href)
                if href == "https://ivod.ly.gov.tw/Demand/Meetvod?Meet=":
                    break
            # try:
            #     wait = WebDriverWait(driver, 20)
            #     pdf_link = wait.until(EC.element_to_be_clickable(
            #         (By.CSS_SELECTOR, '#section-0 > article:nth-child(1) > div > div > div:nth-child(1) > div > div > div:nth-child(7) > div > div > span:nth-child(2) > span > a')
            #     ))

            #     # Click the PDF link to initiate the download
            #     pdf_link.click()
            #     print("PDF download initiated.")
            # except Exception:
            #     break
                
                time.sleep(5)
                driver.get(href)

                video_link_certify = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body > div.wrapper > div > div.contents > div.contents-body.data-table.committee-data-table > div.data-list.committee-data-list > div.committee-data-info > div > div.clip-list-thumbnail > div.thumbnail-btn > p > a:nth-child(2)'))
                )
                    
                #main > section > div:nth-child(2) > article > div > div.row > div.col-12.col-sm-12.col-md-12.col-lg-12.col-xl-7 > div:nth-child(1) > div > div > div > div > div > div:nth-child(4) > div > span:nth-child(3) > a
                #main > section > div:nth-child(2) > article > div > div.row > div.col-12.col-sm-12.col-md-12.col-lg-12.col-xl-7 > div:nth-child(2) > div > div > div > div > div > div:nth-child(4) > div > span:nth-child(3) > a
                time.sleep(3)
                video_link_certify = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div > div.contents > div.contents-body.data-table.committee-data-table > div.data-list.committee-data-list > div.committee-data-info > div > div.clip-list-thumbnail > div.thumbnail-btn > p > a:nth-child(2)')
                href = video_link_certify.get_attribute('href')
                print(href)
                driver.get(href)
                # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "script")))
                time.sleep(10)
                # Find and process scripts only once the page is fully loaded
                soup = BeautifulSoup(driver.page_source, "html.parser")
                text_content = soup.get_text()

                # Clean up the text by stripping unnecessary whitespace
                text_content = text_content.strip()

                # Now try splitting by "會議時間：" 
                split_content = text_content.split("會議時間：")

                # Extract the first 16 characters from split_content[1]
                time_info = split_content[1][:16]

                all_scripts = soup.find_all("script")
                url = ""  # Initialize url variable
                download_video_dir = os.path.join(os.getcwd(), "output_video_new")
                os.makedirs(download_video_dir, exist_ok=True)  # Ensure the directory exists

                for number, script in enumerate(all_scripts):
                    if "readyPlayer" in script.text:
                        tmpText = re.sub(re.compile(r"\s+"), "", script.text)
                        tmpText = re.sub(r".*readyPlayer\(\"", "", tmpText)
                        url = re.sub(r".m3u8\".*", "", tmpText)
                        print(url + ".m3u8")
                        break  # Exit the loop once the URL is found
                    
                if url:
                    response = requests.get(url + ".m3u8")
                    filename = response.text.split()
                    url_new = url.replace("playlist", filename[len(filename) - 1])

                    # Specify output file path in the desired directory
                    downloader = M3U8Downloader(
                        input_file_path=url_new,
                        output_file_path=os.path.join(download_video_dir, f"{time_info}.mp4"),  # Modify this line
                    )
                    downloader.download_playlist()
                    driver.back()
                    time.sleep(2)
                    driver.back()
                    time.sleep(2)
                else:
                    print("No valid URL found in scripts.")
            

                
                # driver.get(href_main)
                # time.sleep(5)
                # except Exception as e:
                #     print(f"An error occurred: {e}")
                #     driver.back()
                #     break`
        else:
            pass
    except Exception:
        driver.back()
        time.sleep(2)
        driver.back()
        time.sleep(2)


# Function to handle calendar events
def handle_calendar_events():
    try:
        # Re-fetch all days with events to avoid stale elements
        days_with_events = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.day.has-event'))
        )

        # Loop through each day with events
        for index, day in enumerate(days_with_events):
            try:
                # Scroll the day element into view and click on the day to view events
                driver.execute_script("arguments[0].scrollIntoView(true);", day)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(day)).click()

                # Wait for the event details to load using the 'card-body' class
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-body'))
                )
                time.sleep(2)

                event_index = 1
                while True:
                    try:
                        # Locate the div containing event links for the specific event index
                        event_div = driver.find_element(By.CSS_SELECTOR, f'#pills-b1 > div.row > div.col-12.col-sm-12.col-md-6.col-lg-8.col-xl-8 > div > div > div > div:nth-child({event_index})')

                        # Find the anchor tag within the div
                        link = event_div.find_element(By.CSS_SELECTOR, 'span.card-title.fs-6.fw-bolder > a')
                        href_main = link.get_attribute('href')
                        print(f"Event Link URL: {href_main}")

                        # Visit the event details page
                        driver.get(href_main)
                        
                        # Wait for the event details page to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#page-top > span > div > header > article.Page-Strip > div > div > div > div > div > a:nth-child(2)'))
                        )
                        time.sleep(2)
                        download_file(href_main)
                        # Go back to the calendar
                        # time.sleep(5)
                        # driver.get(href_main)
                        time.sleep(5)
                        driver.back()

                        # Wait for the calendar page to load again
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.day.has-event'))
                        )
                        time.sleep(2)

                        event_index += 1

                    except NoSuchElementException:
                        print(f"No more events at index: {event_index}")
                        time.sleep(2)
                        break

                    except Exception as e:
                        print(f"An error occurred while processing events: {e}")
                        driver.back()  # Ensure we return to the calendar view even if something goes wrong
                        break

                # Re-fetch days after handling events on this specific day
                days_with_events = driver.find_elements(By.CSS_SELECTOR, '.day.has-event')

            except Exception as e:
                print(f"An error occurred in day with events, break this")
                break

    except TimeoutException:
        print("Timed out waiting for calendar days to load.")
    except Exception as e:
        print(f"An error occurred in handle_calendar_events: {e}")

# Navigate the calendar for the specified date range
months = ["0", "1", "2", "3", "4", "5", "6"]  # January to July values
year = "2024"

for month in months:
    try:
        # Re-select the year and month dropdown elements before each iteration
        year_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pills-b1"]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/select[1]'))
        )
        year_select = Select(year_select_element)
        year_select.select_by_value(year)

        # Adding a delay to ensure the dropdown updates correctly
        time.sleep(2)

        month_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pills-b1"]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/select[2]'))
        )
        month_select = Select(month_select_element)
        month_select.select_by_value(month)

        # Adding a delay to ensure the dropdown updates correctly
        time.sleep(2)

        # Handle events in the calendar for the selected month
        handle_calendar_events()
        print(f"Finished processing month {month+1}.")
        time.sleep(5)

    except StaleElementReferenceException:
        print(f"Stale element reference while processing {year} month {month}, re-attempting...")
        continue  # This will re-attempt the loop iteration

    except Exception as e:
        print(f"An error occurred while processing {year} month {month}: {e}")
        continue

# Close the driver
driver.quit()
