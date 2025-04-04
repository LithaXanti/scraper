from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver_manager.firefox import GeckoDriverManager  # type: ignore
from selenium.webdriver.common.action_chains import ActionChains

import time
import random
import pandas as pd


options = Options()
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)

SELECTORS = {
    'listings_container': 'ul.photo-cards',
    'single_listing': 'article.list-card',
    'price': 'list-card-price',
    'address': 'list-card-addr',
    'details': 'list-card-details',
    'beds': 'list-card-details li:first-child',
    'baths': 'list-card-details li:nth-child(2)',
    'sqft': 'list-card-details li:nth-child(3)',
    'link': 'a.list-card-link',
    'next_page': 'a[title="Next page"]',
}

def human_like_interaction(driver):
    """Simulate human-like mouse movements and scrolling"""
    actions = ActionChains(driver)

    for _ in range(random.randint(2, 4)):
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        actions.move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(0.5, 1.5))

        scroll_amount = random.randint(200, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))

def scrape_zillow():
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        url = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.30389632177734%2C%22south%22%3A37.69261367727707%2C%22north%22%3A37.87786982979634%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"
        driver.get(url)
        time.sleep(random.uniform(3, 6))

        scraped_data = []
        page_number = 1
        
        while True:
            print(f"Scraping page {page_number}")

            human_like_interaction(driver)

            try:
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['listings_container']))
                )
                listings = container.find_elements(By.CSS_SELECTOR, SELECTORS['single_listing'])
                print(f"Found {len(listings)} listings on page {page_number}")
            except Exception as e:
                print(f"Error locating listings container or elements: {e}")
                break

            for listing in listings:
                try:
                    data = {
                        'price': listing.find_element(By.CLASS_NAME, SELECTORS['price']).text,
                        'address': listing.find_element(By.CLASS_NAME, SELECTORS['address']).text,
                        'link': listing.find_element(By.CSS_SELECTOR, SELECTORS['link']).get_attribute('href'),
                    }
                    
                    # Handle details which might not always be present
                    try:
                        details = listing.find_element(By.CLASS_NAME, SELECTORS['details']).text
                        data['details'] = details
                        
                        # Try to get individual components
                        detail_items = listing.find_elements(By.CSS_SELECTOR, 'li')
                        if len(detail_items) >= 1:
                            data['beds'] = detail_items[0].text
                        if len(detail_items) >= 2:
                            data['baths'] = detail_items[1].text
                        if len(detail_items) >= 3:
                            data['sqft'] = detail_items[2].text
                    except Exception as e:
                        print(f"Error getting details for listing: {e}")
                        data['details'] = ''
                        data['beds'] = ''
                        data['baths'] = ''
                        data['sqft'] = ''

                    scraped_data.append(data)
                except Exception as e:
                    print(f"Error scraping listing: {e}")
                    continue

            try:
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['next_page']))
                )
                next_page.click()
                time.sleep(random.uniform(3, 6))
                page_number += 1
            except Exception as e:
                print(f"No more pages to scrape or error clicking next page: {e}")
                break

        if scraped_data:
            df = pd.DataFrame(scraped_data)
            df.to_csv('zillow_data.csv', index=False)
            print(f"Scraped {len(scraped_data)} listings saved to zillow_data.csv")
        else:
            print("No data scraped.")
            
    except Exception as e:
        print(f"Error occurred during scraping: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_zillow()