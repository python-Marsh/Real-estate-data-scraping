import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load the CSV file
df = pd.read_csv('/Users/user/Desktop/testdata.csv')  # Replace with your CSV file path
postcodes = df.iloc[:, 0].tolist()
distance_NHS_text=[]

# Initialize the WebDriver (you may need to adjust the path to your WebDriver)
for x in range(len(postcodes)):
    driver = webdriver.Chrome()  # Replace with your ChromeDriver path
    url='https://www.nhs.uk/service-search/hospital/results/'
    driver.get(url + postcodes[x])
    time.sleep(5)
    try:
        distance_NHS = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'distance_0'))
    )
        temp = distance_NHS.text
        # Extract the numeric part using regular expression
        match = re.search(r'\d+(\.\d+)?', temp)
        if match:
            distance_NHS_text.append(match.group())
        else:
            distance_NHS_text.append('No distance found')


    except Exception as e:
        print(e)
        
print(distance_NHS_text)        
df = pd.DataFrame(distance_NHS_text, columns=['Hospital distance'])

# Specify the file path
file_path = '/Users/user/Desktop/NHS_Distances.csv'  # Replace with your desired file path

# Write the DataFrame to a CSV file
df.to_csv(file_path, index=False)
print(df)
print("CSV file has been written.")