import psycopg2
from psycopg2.extras import execute_batch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def extract_property_data(driver, url):
    driver.get(url)
    
    # Wait for the property cards to load
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

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Location', 'Price', 'Beds', 'Area'])
        writer.writeheader()
        writer.writerows(data)

# Main execution
base_url = 'https://www.zameen.com/Homes/Islamabad-3-{}.html?beds_in=1%2C2%2C3%2C4'
all_properties = []

# Set up the Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    for page in range(1, 9):  # 8 pages
        url = base_url.format(page)
        print(f"Scraping page {page}...")
        property_data = extract_property_data(driver, url)
        all_properties.extend(property_data)
        print(f"Extracted {len(property_data)} properties from page {page}")
        time.sleep(2) 
finally:
    driver.quit()

# Save the data to a CSV file
save_to_csv(all_properties, 'islamabad_properties2.csv')

def insert_into_database(properties):
    conn = psycopg2.connect(
        dbname="zameen_properties",
        user="postgres",
        password="anns",
        host="localhost"
    )
    cur = conn.cursor()

    insert_query = """
    INSERT INTO properties (location, price, beds, area)
    VALUES (%s, %s, %s, %s)
    """

    execute_batch(cur, insert_query, [
        (prop['Location'], prop['Price'], prop['Beds'], prop['Area'])
        for prop in properties
    ])

    conn.commit()
    cur.close()
    conn.close()



# After scraping, insert into database
insert_into_database(all_properties)

print(f"Total properties extracted and inserted: {len(all_properties)}")