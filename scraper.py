from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import random
import json
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",

]

options = Options()
options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)

base_url = "https://www.redfin.com/neighborhood/547223/CA/Los-Angeles/Hollywood-Hills"
driver.get(base_url)
def wait_for_element(driver, selector, timeout=10):
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

print(f"Page title: {driver.title}")
if "Access" in driver.title or "blocked" in driver.page_source.lower():
    print("Warning: Redfin has blocked the request!")
    driver.quit()
    exit()

scraped_data = []
page_number = 1

while True:
    print(f"Scraping page {page_number}")

    try:
        container = driver.find_element("css selector", "div[data-rf-test-id='homes-container']")
        listings = container.find_elements("css selector", "div[data-rf-test-name='property-card']")
    except Exception as e:
        print(f"An error occurred while locating the container or listings: {e}")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        break

    print(f"Found {len(listings)} listings on page {page_number}")

    for listing in listings:
        try:
            price = listing.find_element("css selector", "span[data-rf-test-id='ab-price']").text.strip()
        except:
            price = "N/A"

        try:
            address = listing.find_element("css selector", "div[data-rf-test-id='ab-address']").text.strip()
        except:
            print("Address not found")
            continue

        try:
            beds = listing.find_element("css selector", "div[data-rf-test-id='ab-beds']").text.strip()
        except:
            beds = "N/A"

        try:
            baths = listing.find_element("css selector", "div[data-rf-test-id='ab-baths']").text.strip()
        except:
            baths = "N/A"

        try:
            sqft = listing.find_element("css selector", "div[data-rf-test-id='ab-sqFt']").text.strip()
        except:
            sqft = "N/A"

        try:
            link = listing.find_element("css selector", "a[data-rf-test-name='property-card-link']").get_attribute("href")
            link = f"https://www.redfin.com{link}" if link.startswith("/") else link
        except:
            print("Link not found")
            continue

        try:
            image_element = listing.find_element("css selector", "img[data-rf-test-id='property-card-image']")
            image_url = image_element.get_attribute("src")
        except:
            image_url = "N/A"

        try:
            json_script = listing.find_element("css selector", "script[type='application/ld+json']").get_attribute("innerHTML")
            json_data = json.loads(json_script)
            latitude = json_data[0]["geo"]["latitude"]
            longitude = json_data[0]["geo"]["longitude"]
        except:
            latitude = "N/A"
            longitude = "N/A"

        scraped_data.append({
            "price": price,
            "address": address,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "link": link,
            "image_url": image_url,
            "latitude": latitude,
            "longitude": longitude
        })

    try:
        next_button = driver.find_element("css selector", "button.PageArrow__direction--next")
        next_button.click()
        def wait_for_element(driver, selector, timeout=10):
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        page_number += 1
    except:
        print("No more pages")
        break
    
    

import pandas as pd
df = pd.DataFrame(scraped_data)
df.to_csv("redfin_listings.csv", index=False)
print(f"{len(df)}Data saved to CSV")

driver.quit()    