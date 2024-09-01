import time
import random
import json
import sys
from urllib.parse import quote
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

USERNAME = "yabada_djkVV"
PASSWORD = "yuhimR42_yabada"
ENDPOINT = "pr.oxylabs.io:7777"
TARGET_ITEMS = 170  # Set the target number of items to collect

def chrome_proxy(user: str, password: str, endpoint: str) -> dict:
    wire_options = {
        "proxy": {
            "http": f"http://{user}:{password}@{endpoint}",
            "https": f"https://{user}:{password}@{endpoint}",
        }
    }
    return wire_options

def load_existing_data(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data_to_json(filepath, search_term, location, new_items):
    data = load_existing_data(filepath)
    search_term = search_term.capitalize()
    location = location.capitalize()

    if search_term not in data:
        data[search_term] = {}

    if location not in data[search_term]:
        data[search_term][location] = []

    data[search_term][location].extend(new_items)

    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def scroll_and_collect_items(driver, target_items):
    items = []
    initial_items = 12  # Initial items loaded without scroll
    items_per_scroll = 6  # New items per scroll

    # Calculate number of scrolls required to reach or exceed target items
    if target_items > initial_items:
        scrolls_needed = (target_items - initial_items + items_per_scroll - 1) // items_per_scroll
    else:
        scrolls_needed = 0

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
    main_div = driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')

    for _ in range(scrolls_needed):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(0.8, 1.2))  # Mimicking human scrolling behavior

    # Collect all items at once after scrolling
    current_items = main_div.find_elements(By.TAG_NAME, 'a')
    for a_tag in current_items[:target_items]:  # Ensure not to exceed target_items
        item_info = {
            'link': a_tag.get_attribute('href'),
            'title': a_tag.find_element(By.TAG_NAME, 'img').get_attribute('alt'),
            'image_url': a_tag.find_element(By.TAG_NAME, 'img').get_attribute('src')
        }
        items.append(item_info)

    return items

def launch_facebook_marketplace(location: str, search_term: str, filepath):
    manage_driver = Service(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    user_data_dir = 'C://Users//user//AppData//Local//Google//Chrome//User Data'
    profile_directory = 'Profile 2'
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(f"profile-directory={profile_directory}")

    proxies = chrome_proxy(USERNAME, PASSWORD, ENDPOINT)
    driver = webdriver.Chrome(service=manage_driver, options=options, seleniumwire_options=proxies)

    try:
        encoded_search_term = quote(search_term)
        url = f'https://www.facebook.com/marketplace/{location}/search?radius=805&deliveryMethod=all&query={encoded_search_term}'
        driver.get(url)
        WebDriverWait(driver, 20).until(lambda x: driver.execute_script('return document.readyState') == 'complete')
        items_collected = scroll_and_collect_items(driver, TARGET_ITEMS)
        save_data_to_json(filepath, search_term, location, items_collected)
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script_name.py [location] [search_term]")
        sys.exit(1)
    location_input = sys.argv[1]
    search_term_input = sys.argv[2]
    file_path = 'fb_local_items.json'
    launch_facebook_marketplace(location_input, search_term_input, file_path)
