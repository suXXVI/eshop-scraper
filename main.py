from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# headless browser setup
options = Options()
options.add_argument("--headless")
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
except Exception as e:
    print("Error:", e)
    driver.quit()
    exit()


# Keep clicking "Load more results" until it disappears
while True:
    print('scraping...');
    try:
        load_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Load more results"]]'))
        )
        load_more_button.click()
        time.sleep(2)  # Give time for new products to load
    except (TimeoutException, NoSuchElementException):
        print("No more 'Load more results' button found.")
        break

    grid_container = parent_container.find_element(By.CLASS_NAME, "ljMhgM")
    cards = grid_container.find_elements(By.CLASS_NAME, "y83ib")
    print(f"{len(cards)} games")
    


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

        print(f"{title:<60} | {price:<10}")
    except Exception as e:
        print("Error parsing card:", e)

driver.quit()