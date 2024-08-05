from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Selenium WebDriver
service = Service('./chromedriver.exe')  # Update the path to your ChromeDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(service=service, options=options)

# URL to crawl
url = 'https://ppg.ly.gov.tw/ppg/#section-2'

# Open the URL
driver.get(url)

# Function to download a file
def download_file(file_url, save_path):
    driver.get(file_url)
    with open(save_path, 'wb') as file:
        file.write(driver.page_source.encode('utf-8'))

# Function to handle calendar events
def handle_calendar_events():
    # Get all days with events
    days_with_events = driver.find_elements(By.CSS_SELECTOR, '.day.has-event')
    
    for day in days_with_events:
        try:
            # Scroll the day element into view and click on the day to view events
            driver.execute_script("arguments[0].scrollIntoView();", day)
            driver.execute_script("arguments[0].click();", day)
            
            # Wait for the event details to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-12.col-sm-12.col-md-6.col-lg-8.col-xl-8'))
            )
            
            # Find event cards and click on each one
            #pills-b1 > div.row > div.col-12.col-sm-12.col-md-6.col-lg-8.col-xl-8 > div > div > div > div:nth-child(1) > div > div
            #pills-b1 > div.row > div.col-12.col-sm-12.col-md-6.col-lg-8.col-xl-8 > div > div > div > div:nth-child(2) > div > div
            event_cards = driver.find_elements(By.CSS_SELECTOR, '.col-12.col-sm-12 a')
            for card in event_cards:
                card_href = card.get_attribute('href')
                driver.get(card_href)
                
                # Wait for the event details page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'event-details'))
                )
                
                # Check for video and transcript buttons
                try:
                    video_button = driver.find_element(By.LINK_TEXT, '會議影片')
                    video_url = video_button.get_attribute('href')
                    download_file(video_url, f'video_{day.text}.mp4')
                except:
                    pass
                
                try:
                    transcript_button = driver.find_element(By.LINK_TEXT, '公報紀錄')
                    transcript_url = transcript_button.get_attribute('href')
                    download_file(transcript_url, f'transcript_{day.text}.pdf')
                except:
                    pass
                
                # Go back to the calendar
                driver.back()
                
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

# Navigate the calendar for the specified date range
months = ["0", "1", "2", "3", "4", "5", "6"]  # January to July values
year = "2024"

for month in months:
    try:
        # Select the year
        year_select = driver.find_element(By.XPATH, '//*[@id="pills-b1"]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/select[1]')
        year_select.click()
        year_option = driver.find_element(By.XPATH, f"//option[@value='{year}']")
        year_option.click()
        
        # Select the month by value
        month_select = driver.find_element(By.XPATH, '//*[@id="pills-b1"]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/select[2]')
        month_select.click()
        month_option = driver.find_element(By.XPATH, f"//option[@value='{month}']")
        month_option.click()
        
        # Handle events in the calendar for the selected month
        handle_calendar_events()
        
    except Exception as e:
        print(f"An error occurred while processing {year} month {month}: {e}")
        continue

# Close the driver
driver.quit()
