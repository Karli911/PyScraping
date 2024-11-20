import requests
from bs4 import BeautifulSoup
import csv
import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(filename='logs/scraping.log', level=logging.INFO)

# Configuration
USE_SELENIUM = True  # Set to False if the site content is static and not dynamically loaded
BASE_URL = input("Enter the target URL:")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
START_PAGE = 1
DELAY = 7

def scrape_with_requests(url):
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status code for {url}: {response.status_code}")  # Debugging statement
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for {url}: {e}")
        return None

def scrape_with_selenium(url):
    try:
        options = Options()
        options.headless = True
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Wait for a specific element to load, if needed
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        logging.error(f"Selenium error for {url}: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {
        'title': soup.title.string if soup.title else 'No title',
        'meta_description': soup.find('meta', attrs={'name': 'description'}).get('content', 'No description') if soup.find('meta', attrs={'name': 'description'}) else 'No description',
        'headings': {
            'h1': [h1.get_text() for h1 in soup.find_all('h1')],
            'h2': [h2.get_text() for h2 in soup.find_all('h2')],
            'h3': [h3.get_text() for h3 in soup.find_all('h3')],
        },
        'links': [a.get('href') for a in soup.find_all('a')],
        'images': [img.get('src') for img in soup.find_all('img')],
        'text': soup.get_text()
    }
    return data

def save_data(data, filename='data/scraped_data.json'):
    try:
        print("Data to be saved:", data)
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4, ensure_ascii=False)
        logging.info(f'Data saved to {filename}')
    except IOError as e:
        logging.error(f"File error: {e}")

def save_csv(data, filename='data/scraped_data.csv'):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Type', 'Content'])
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                writer.writerow([key, value])
        logging.info(f'Data saved to {filename}')
    except IOError as e:
        logging.error(f"File error: {e}")

def scrape_page(url):
    if USE_SELENIUM:
        html = scrape_with_selenium(url)
    else:
        html = scrape_with_requests(url)

    if html:
        data = parse_html(html)
        save_data(data)
        save_csv(data)
    else:
        logging.error(f"Failed to retrieve or parse the page: {url}")

def scrape_pages():
    url = BASE_URL  # Starting URL
    print(f"Scraping URL {url}...")
    scrape_page(url)

if __name__ == "__main__":
    scrape_pages()