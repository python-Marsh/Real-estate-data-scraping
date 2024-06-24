import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fuzzywuzzy import fuzz
import time
import re

# Load the CSV file
input_file = '/Users/user/Desktop/testdata.csv'
df = pd.read_csv(input_file)
postcodes = df.iloc[:, 0].tolist()
options = df.iloc[:, 1].tolist()

links = []
options_cleaned_list = []
property_details = []

def clean_address(text):
    return re.sub(r'Select a property to continue\.\s*', '', text).strip()

# Clean all the commas
for y in options:
    options_cleaned_list.append(y.replace(",", ""))

# Initialize the WebDriver 
driver = webdriver.Chrome()

try:
    for x in range(len(postcodes)):
        url = 'https://propertychecker.co.uk/results/?postcode='
        driver.get(url + postcodes[x])
        time.sleep(3)  # Wait a bit for the page to load

        try:
            # Wait for the elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//strong'))
            )
            address_boxes = driver.find_elements(By.XPATH, '//strong')
            found = False
            print(f"Found {len(address_boxes)} address boxes")
            
            for address_box in address_boxes:
                address_text = clean_address(address_box.text.replace(",", ""))
                print(f"Address text: {address_text}")

                if fuzz.ratio(address_text, options_cleaned_list[x]) > 99:  # Adjust the threshold as needed
                    parent_element = address_box.find_element(By.XPATH, '../../../..')
                    links.append(parent_element.get_attribute('href'))
                    print("Found match!")
                    found = True
                    break
            
            if not found:
                print(f"No close match found for {postcodes[x]} with option {options[x]}")
                links.append('N/A')

        except Exception as e:
            print(f"Error locating element for {postcodes[x]} with option {options[x]}: {e}")
            links.append('N/A')

    time.sleep(3)

    # Function to extract property details
    def extract_property_details(link):
        print(f"Extracting details from: {link}")
        driver.get(link)
        time.sleep(3)  # Wait a bit for the page to load
        try:
            current_energy_rating = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//dt[normalize-space(text())="Current Energy Rating"]/following-sibling::dd'))
            ).text
            
            habitable_rooms = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//dt[normalize-space(text())="Habitable Rooms"]/following-sibling::dd'))
            ).text
            print(f"Habitable rooms: {habitable_rooms}")
            
            year_built = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//dt[normalize-space(text())="Year Built"]/following-sibling::dd'))
            ).text
            print(f"Year built: {year_built}")
            
            return current_energy_rating, habitable_rooms, year_built
        except Exception as e:
            print(f"Error extracting details from {link}: {e}")
            return 'N/A', 'N/A', 'N/A'

    # Extract details for each property link
    for link in links:
        if link != 'N/A':
            current_energy_rating, habitable_rooms, year_built = extract_property_details(link)
            property_details.append([link, current_energy_rating, habitable_rooms, year_built])
        else:
            property_details.append(['N/A', 'N/A', 'N/A', 'N/A'])

finally:
    # Close the WebDriver after scraping details
    driver.quit()

# Create a DataFrame to save the property details
property_df = pd.DataFrame(property_details, columns=['Link', 'Current energy ratings', 'Habitable rooms', 'Year built'])

# Save the DataFrame to a CSV file
property_df.to_csv('/Users/user/Desktop/property_details.csv', index=False)

print("Property details have been saved to property_details.csv")
