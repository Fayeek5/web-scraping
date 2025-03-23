import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from scraper import get_opinion_articles, extract_article_data, translate_titles_rapidapi, analyze_headers

load_dotenv()

# BrowserStack credentials
BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")

# BrowserStack configurations for parallel testing
CONFIGURATIONS = [
    # Desktop configurations
    {
        'browserName': 'Chrome',
        'os': 'Windows',
        'osVersion': '10',
        'browserVersion': 'latest'
    },
    {
        'browserName': 'Firefox',
        'os': 'OS X',
        'osVersion': 'Monterey',
        'browserVersion': 'latest'
    },
    # Mobile configurations
    {
        'browserName': 'Safari',
        'deviceName': 'iPhone 13',
        'osVersion': '15'
    },
    {
        'browserName': 'Chrome',
        'deviceName': 'Samsung Galaxy S22',
        'osVersion': '12.0'
    },
    {
        'browserName': 'Safari',
        'deviceName': 'iPad Pro 12.9 2021',
        'osVersion': '15'
    }
]

# Setup BrowserStack driver
def setup_browserstack_driver(config):
    options = Options()
    capabilities = {
        'bstack:options': {
            'userName': BROWSERSTACK_USERNAME,
            'accessKey': BROWSERSTACK_ACCESS_KEY,
            'local': 'false',
            'seleniumVersion': '3.141.59'
        }
    }

    capabilities.update(config)
    options.add_experimental_option('prefs', capabilities)

    bs_url = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

    # Initialize the WebDriver with BrowserStack's URL and options
    driver = webdriver.Remote(
        command_executor=bs_url,
        options=options  # Pass the configured options object
    )

    return driver

# Run test for a single configuration
def run_test(config, config_id):
    driver = setup_browserstack_driver(config)
    try:
        is_desktop = 'os' in config
        # print("OS VERSION", is_desktop, config)
        if is_desktop:
            print(f"\n🔵 Running test configuration {config_id}: {config['browserName']}")
        else:
            device_name = config['deviceName'] 
            print(f"\n🔵 Running test configuration {config_id}: {config['browserName']} - {device_name}")

        # Scrape articles
        article_links = get_opinion_articles(driver)
        articles_data = []

        for i, url in enumerate(article_links):
            data = extract_article_data(driver, url)
            articles_data.append(data)
            print(f"[Config {config_id}] Article {i+1} (ES): {data['title']}")

        # Translate titles
        titles_es = [a['title'] for a in articles_data]
        titles_en = translate_titles_rapidapi(titles_es)

        print(f"\n[Config {config_id}] Translated Titles (EN):")
        for title in titles_en:
            print(f"- {title}")

        # Analyze headers for repeated words
        repeated_words = analyze_headers(titles_en)
        if repeated_words:
            print(f"\n[Config {config_id}] Repeated Words (more than twice):")
            for word, count in repeated_words.items():
                print(f"'{word}': {count}")
        else:
            print(f"\n[Config {config_id}] No repeated words found.")

    except Exception as e:
        print(f"❌ Error in configuration {config_id}: {e}")

    finally:
        driver.quit()
        print(f"🟢 Configuration {config_id} test completed.")

# Main function to run all tests in parallel
def run_parallel_tests():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(run_test, config, idx + 1)
            for idx, config in enumerate(CONFIGURATIONS)
        ]

        concurrent.futures.wait(futures)

if __name__ == "__main__":
    run_parallel_tests()
