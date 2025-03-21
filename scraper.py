import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from collections import Counter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --------------------------
# CONFIGURATION
# --------------------------
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# --------------------------
# Set up Selenium WebDriver
# --------------------------
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--lang=es")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# --------------------------
# Scrape article links
# --------------------------
def get_opinion_articles(driver, max_articles=5):
    driver.get("https://elpais.com/")
    time.sleep(2)

    opinion_link = driver.find_element(By.LINK_TEXT, "Opinión")
    opinion_link.click()
    time.sleep(3)

    articles = driver.find_elements(By.CSS_SELECTOR, "article a")[:max_articles]
    article_urls = [a.get_attribute("href") for a in articles if a.get_attribute("href")]
    return article_urls[:max_articles]

# --------------------------
# Extract article data
# --------------------------
def extract_article_data(driver, url, save_img_dir="images"):
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1").text.strip()
    except:
        title = "No Title"

    paragraphs = soup.find_all("p")
    content = "\n".join(p.text for p in paragraphs if p.text)

    try:
        img_tag = soup.find("figure").find("img")
        img_url = img_tag["src"]
        img_name = os.path.join(save_img_dir, os.path.basename(img_url.split("?")[0]))

        if not os.path.exists(save_img_dir):
            os.makedirs(save_img_dir)

        img_data = requests.get(img_url).content
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
    except Exception:
        img_url = None
        img_name = None

    return {
        "title": title,
        "content": content,
        "image_path": img_name
    }

# --------------------------
# Translate with RapidAPI
# --------------------------
def translate_titles_rapidapi(titles, target_lang='en', source_lang='es'):
    url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }

    translated_titles = []

    for title in titles:
        payload = {
            "from": source_lang,
            "to": target_lang,
            "q": title
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                json_data = response.json()
                print(f"API Response for '{title}': {json_data}")  # Debug print

                # Adjust this depending on API structure
                translated_text = json_data[0]

                if translated_text:
                    translated_titles.append(translated_text)
                else:
                    translated_titles.append("[Translation Failed]")
            else:
                print(f"Translation failed for '{title}' with status code {response.status_code}")
                translated_titles.append("[Translation Failed]")
        except Exception as e:
            print(f"Exception during translation for '{title}': {e}")
            translated_titles.append("[Translation Failed]")

    return translated_titles

# --------------------------
# Analyze repeated words
# --------------------------
def analyze_headers(headers):
    words = []
    for header in headers:
        words.extend(header.lower().split())

    count = Counter(words)
    repeated = {word: cnt for word, cnt in count.items() if cnt > 2}
    return repeated

# --------------------------
# Main
# --------------------------
def main():
    driver = setup_driver()
    try:
        print("Fetching article links...")
        article_links = get_opinion_articles(driver)
        articles_data = []

        print("\nScraping articles...\n")
        for i, url in enumerate(article_links):
            print(f"Article {i+1} URL: {url}")
            data = extract_article_data(driver, url)
            articles_data.append(data)
            print(f"Title (ES): {data['title']}")
            print(f"Content Snippet (ES): {data['content'][:200]}...\n")
            if data['image_path']:
                print(f"Image saved at: {data['image_path']}")
            print("-" * 50)

        # Translate
        titles_es = [a['title'] for a in articles_data]
        print("title es", titles_es)
        titles_en = translate_titles_rapidapi(titles_es)

        print("\nTranslated Titles:")
        for i, t in enumerate(titles_en):
            print(f"{i+1}. {t}")

        # Repeated words
        repeated_words = analyze_headers(titles_en)
        print("\nRepeated Words (more than twice):")
        for word, cnt in repeated_words.items():
            print(f"{word}: {cnt}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
