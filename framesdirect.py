# Libraries Used
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Step 1 - Configuration and Data Fetching
# Setup Selenium and WebDriver
print("Setting up webdriver...")
chrome_option = Options()
chrome_option.add_argument('--headless')
chrome_option.add_argument('--disable-gpu')
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)
print("done setting up..")

# Install the chrome driver (This is a one time thing)
print("Installing Chrome WD")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "https://www.framesdirect.com/eyeglasses/"
print(f"Visting {url} page")
driver.get(url)

# Further instruction: wait for JS to load the files
try:
    print("Waiting for product tiles to load")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'mobile_body_wrapper'))
    )
    print("Done...Proceed to parse the data")
except (TimeoutError, Exception) as e:
    print(f"Error waiting for {url}: {e}")
    driver.quit()
    print("Closed")

# Step 2 - Data Parsing and Extraction
# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, 'html.parser')

# Temporary storage for the extracted data
framedirect_data = []


# Locate all product tiles and extract the data for each product.
product_list = page.find_all("div", class_='prod-holder')
print(f"Found {len(product_list)} products")


for plist in product_list:
    product_info = plist.find('div', class_='prod-image-holder')


    if product_info:
        brand_name = product_info.find('div', class_='catalog-name')
        brand = brand_name.text if brand_name else None # product brand


        product_name = product_info.find('div', class_='product_name')
        pname = product_name.text if product_name else None

        if not brand or not pname:
            continue

        # for price
        price_cnt = product_info.find('div', class_='prod-price-wrap')
        if price_cnt:
            # Former Price
            former_price_tag = price_cnt.find('div', class_='prod-catalog-retail-price')
            former_price = former_price_tag.text.strip().replace("$", "") if former_price_tag else None
            former_price =float(former_price) if former_price else None
            # Current Price
            current_price_tag = price_cnt.find('div', class_='prod-aslowas')
            current_price = current_price_tag.text .strip().replace("$", "") if current_price_tag else None
            current_price =float(current_price) if current_price else None
        else:
            former_price = current_price = None
    else:
        brand = pname = former_price = current_price = None 
        # Automatically applies missing value, if the product info is not available.

    
    discount_tag = plist.find('div', class_='frame-discount size-11')
    discount = discount_tag.text if discount_tag else None
    discount = discount if discount else None

    # Assignment: Add the category
              
    data = {
        'Brand': brand,
        'Product_Name': pname,
        'Former_Price': former_price,
        'Current_Price': current_price,
        'Discount': discount
    }
    # Append data to the list
    framedirect_data.append(data)


    # Step 3 - Data Storage and Finalization
# Save to CSV file
column_name = framedirect_data[0].keys() # get the column names
with open('framedirect_data.csv', mode='w', newline='', encoding='utf-8') as csv_file: # open up the file with context manager
    dict_writer = csv.DictWriter(csv_file, fieldnames=column_name)
    dict_writer.writeheader()
    dict_writer.writerows(framedirect_data)
print(f"Saved {len(framedirect_data)} records to CSV")

# Save to JSON file
with open("framedirect.json", mode='w') as json_file:
    json.dump(framedirect_data, json_file, indent=4)
print(f"Saved {len(framedirect_data)} records to JSON")

# close the browser
driver.quit()
print("End of Web Extraction")
