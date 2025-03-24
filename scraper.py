import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import Counter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Loading .env file from: {env_path}")
load_dotenv(env_path, override=True) 

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# --------------------------
# Scrape article links
# --------------------------
def get_opinion_articles(driver, max_articles=5):
    driver.get("https://elpais.com/")
    
    wait = WebDriverWait(driver, 20)  # Increase timeout for BrowserStack

    # Debug: Print page title to confirm load
    print(f"Loaded page title: {driver.title}")

    # Handle cookie consent popup
    try:
        consent_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(@id, "didomi-notice-agree-button") or contains(., "Aceptar")]')
        ))
        consent_button.click()
        print("Cookie consent popup closed.")
    except Exception as e:
        print(f"No cookie consent button found or error")

    # Navigate to "Opinión" section
    try:
        # More flexible selector: look for any element containing "Opinión"
        opinion_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, "Opinión")
            )
        )
        opinion_link.click()
        print("Navigated to Opinión section.")
    except Exception as e:
        print(f"Error finding Opinión link: {e}")
        return []

    # Wait for article links and scrape
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article h2 a")))
        articles = driver.find_elements(By.CSS_SELECTOR, "article h2 a")[:max_articles]
        article_urls = [a.get_attribute("href") for a in articles if a.get_attribute("href")]
        print(f"Found {len(article_urls)} article URLs: {article_urls}")
        return article_urls
    except Exception as e:
        print(f"Error scraping article links: {e}")
        return []                       

# --------------------------
# Extract article data
# --------------------------
def extract_article_data(driver, url, save_img_dir="images"):
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # Wait for article content to load
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    except Exception as e:
        print(f"Error waiting for article content: {e}")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1").text.strip()
    except AttributeError:
        title = "No Title"

    paragraphs = soup.find_all("p")
    content = "\n".join(p.text for p in paragraphs if p.text)

    try:
        img_tag = soup.find("figure") and soup.find("figure").find("img")
        if img_tag and "src" in img_tag.attrs:
            img_url = img_tag["src"]
            img_name = os.path.join(save_img_dir, os.path.basename(img_url.split("?")[0]))

            if not os.path.exists(save_img_dir):
                os.makedirs(save_img_dir)

            img_data = requests.get(img_url, timeout=10).content
            with open(img_name, 'wb') as handler:
                handler.write(img_data)
            print(f"Image saved at: {img_name}")
        else:
            img_url = None
            img_name = None
    except Exception as e:
        print(f"Error downloading image: {e}")
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
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                print(f"API Response for '{title}': {json_data}")
                translated_text = json_data[0] if json_data else "[Translation Failed]"
                translated_titles.append(translated_text)
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
# Main (for local testing)
# --------------------------
def main():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--lang=es")
    driver = webdriver.Chrome(options=chrome_options)
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

        titles_es = [a['title'] for a in articles_data]
        print("Titles (ES):", titles_es)
        titles_en = translate_titles_rapidapi(titles_es)

        print("\nTranslated Titles:")
        for i, t in enumerate(titles_en):
            print(f"{i+1}. {t}")

        repeated_words = analyze_headers(titles_en)
        if repeated_words:
            print("\nRepeated Words (more than twice):")
            for word, cnt in repeated_words.items():
                print(f"{word}: {cnt}")
        else:
            print("\nNo Repeated Words")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()