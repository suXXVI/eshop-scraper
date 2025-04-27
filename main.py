from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from db import insert_game

# Setup chrome options
def get_chrome_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return options

# Setup main list driver
list_driver = webdriver.Chrome(options=get_chrome_options())

# load the Nintendo shop
url = "https://www.nintendo.com/us/store/games/#products"
list_driver.get(url)

# wait for the grid to load
try:
    print("Initializing...")
    parent_container = WebDriverWait(list_driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cedmum"))
    )
except Exception as e:
    print("Error:", e)
    list_driver.quit()
    exit()
    
count = 0

# click "Load more results" until none
while True:
    try:
        load_more_button = WebDriverWait(list_driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Load more results"]]'))
        )
        load_more_button.click()
        count += 40
        print(f"Loading {count} games")
        time.sleep(2)
    except (TimeoutException, NoSuchElementException):
        print("No more 'Load more results' button found.")
        break

# collect all game info
grid_container = parent_container.find_element(By.CLASS_NAME, "ljMhgM")
cards = grid_container.find_elements(By.CLASS_NAME, "y83ib")
print(f"{len(cards)} games found.")

games_data = []

for card in cards:
    try:
        title_tag = card.find_element(By.TAG_NAME, "h2")
        price_tag = card.find_element(By.CLASS_NAME, "W990N")
        link_tag = card.find_element(By.TAG_NAME, "a")
        thumbnail_tag = card.find_element(By.TAG_NAME, "img")
        release_date_tag = card.find_element(By.CLASS_NAME, "k9MOS")

        title = title_tag.text.strip()
        price = price_tag.text.strip()
        link = link_tag.get_attribute("href")
        thumbnail = thumbnail_tag.get_attribute("src")
        release_date = release_date_tag.text.strip()

        games_data.append({
            "title": title,
            "price": price,
            "link": link,
            "thumbnail": thumbnail,
            "release_date": release_date
        })

    except Exception as e:
        print("Error parsing card:", e)

print(f"{len(games_data)} games collected.")

list_driver.quit()  # Done with main driver!

# Function to visit each game's page
def fetch_and_insert(game):
    try:
        detail_driver = webdriver.Chrome(options=get_chrome_options())
        detail_driver.get(game["link"])
        time.sleep(2)

        try:
            desc_parent_container = WebDriverWait(detail_driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kGKNts"))
            )
            description_tag = desc_parent_container.find_element(By.TAG_NAME, "p")
            description = description_tag.text.strip()
        except Exception as e:
            print(f"Error fetching description for {game['title']}: {e}")
            description = "No description available."

        print(f"{game['title']:<60} | {game['price']:<10} | {game['release_date']:<15}")
        insert_game(
            game['title'],
            game['price'],
            game['release_date'],
            game['thumbnail'],
            description
        )

    except Exception as e:
        print(f"Error processing game {game['title']}: {e}")
    finally:
        detail_driver.quit()

# Use ThreadPoolExecutor to speed up detail fetching
max_threads = 5  # 5 simultaneous game scrapers
with ThreadPoolExecutor(max_threads) as executor:
    futures = [executor.submit(fetch_and_insert, game) for game in games_data]

    for future in as_completed(futures):
        pass  # just wait for all threads to complete

print("Done scraping all games!")