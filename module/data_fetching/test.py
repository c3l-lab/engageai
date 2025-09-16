from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.chrome.options import Options
import time

# Setup options (optional)
options = Options()
# Set up Chrome browser
driver = webdriver.Chrome(options=options)  # or webdriver.Chrome(executable_path='/path/to/chromedriver')

options.add_experimental_option("detach", True)

# Open Google
driver.get("https://www.google.com")

# Find the search box
search_box = driver.find_element(By.NAME, "q")

# Enter a search term
search_box.send_keys("Selenium Python")

# Press Enter
search_box.send_keys(Keys.RETURN)

# Wait a few seconds to load results
time.sleep(3)

# Print the title of the results page
print("Page title:", driver.title)

# Close the browser
# driver.quit()

time.sleep()
