from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# setup headless browser
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# load up the eshop
url = "https://www.nintendo.com/us/store/games/#products"
driver.get(url)

# wait for the game grid to load
try:
    # Wait for parent container first
    parent_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cedmum"))
    )

    # Then find the grid inside the parent
    grid_container = parent_container.find_element(By.CLASS_NAME, "ljMhgM")

    # Then find all the cards inside the grid
    cards = grid_container.find_elements(By.CLASS_NAME, "y83ib")
    print(len(cards))

except Exception as e:
    print("Error:", e)
    driver.quit()
    exit()

# loop through cards and extract info
for card in cards:
    try:
        title_tag = card.find_element(By.TAG_NAME, "h2")
        price_tag = card.find_element(By.TAG_NAME, "span")
        link_tag = card.find_element(By.TAG_NAME, "a")
        thumbnail_tag = card.find_element(By.TAG_NAME, "img")

        title = title_tag.text.strip()
        price = price_tag.text.strip()
        link = link_tag.get_attribute("href")
        thumbnail = thumbnail_tag.get_attribute("src")

        print(f"{title:<60} | {price:<10} | {link}")
    except Exception as e:
        print("Error parsing card:", e)

driver.quit()