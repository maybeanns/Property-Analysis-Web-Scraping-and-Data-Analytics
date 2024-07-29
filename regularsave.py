import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_property_data(driver, url):
    driver.get(url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li[aria-label='Listing']"))
    )
    
    properties = []
    cards = driver.find_elements(By.CSS_SELECTOR, "li[aria-label='Listing']")
    
    for card in cards:
        try:
            location = card.find_element(By.CSS_SELECTOR, "div[aria-label='Location']").text.strip()
            price = card.find_element(By.CSS_SELECTOR, "span[aria-label='Price']").text.strip()
            beds = card.find_element(By.CSS_SELECTOR, "span[aria-label='Beds']").text.strip()
            area = card.find_element(By.CSS_SELECTOR, "span[aria-label='Area']").text.strip()
            
            properties.append({
                'Location': location,
                'Price': price,
                'Beds': beds,
                'Area': area
            })
        except Exception as e:
            print(f"Error extracting property data: {e}")
    
    return properties

def save_to_csv(data, filename, mode='a'):
    try:
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Location', 'Price', 'Beds', 'Area'])
            if mode == 'w':
                writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# Main execution
base_url = 'https://www.zameen.com/Houses_Property/Islamabad-3-{}.html'
all_properties = []
csv_filename = 'islamabad_properties2.csv'

# Set up the Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # Write header to CSV
    save_to_csv([], csv_filename, mode='w')
    
    for page in range(1, 301):  # 300 pages
        url = base_url.format(page)
        print(f"Scraping page {page}...")
        try:
            property_data = extract_property_data(driver, url)
            all_properties.extend(property_data)
            print(f"Extracted {len(property_data)} properties from page {page}")
            
            # Save data every 10 pages
            if page % 10 == 0:
                save_to_csv(all_properties, csv_filename)
                all_properties = []  # Clear the list to free up memory
                print(f"Saved data up to page {page}")
            
            time.sleep(2)  # Add a delay to be respectful to the server
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue  # Continue to next page if there's an error
finally:
    # Save any remaining data
    if all_properties:
        save_to_csv(all_properties, csv_filename)
    driver.quit()

print("Data extraction and saving completed.")