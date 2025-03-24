import os
import time
import concurrent.futures
import json
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from scraper import get_opinion_articles, extract_article_data, translate_titles_rapidapi, analyze_headers

os.environ["PYTHONIOENCODING"] = "utf-8"
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Loading .env file from: {env_path}")
load_dotenv(env_path, override=True) 

BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")

def load_browserstack_config():
    try:
        with open("browserstack.yml", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        # print("Loaded browserstack.yml:", config)
        return config
    except Exception as e:
        print(f"Failed to load browserstack.yml: {e}")
        raise

def setup_browserstack_driver(config):
    options = Options()
    # Base capabilities structure similar to desired_cap
    capabilities = {
        "browserName": config.get("browserName", "Chrome"),  # Default to Chrome if not specified
        'bstack:options': {
            "userName": BROWSERSTACK_USERNAME,
            "accessKey": BROWSERSTACK_ACCESS_KEY,
            "local": "false",
            "seleniumVersion": "4.29.0",
            "buildName": f"Opinion Scraper Build - {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "consoleLogs": "verbose",  # Align with your previous setting
            # "visual": True,
            "networkLogs": True,  # Enable network logs
        }
    }

    # Update with config from browserstack.yml
    bstack_options = capabilities['bstack:options']
    if 'os' in config:
        bstack_options["os"] = config["os"]
        bstack_options["osVersion"] = config["osVersion"]
    if 'deviceName' in config:
        bstack_options["deviceName"] = config["deviceName"]
        bstack_options["osVersion"] = config["osVersion"]
        bstack_options["deviceOrientation"] = config.get("deviceOrientation", "portrait")
    bstack_options["browserVersion"] = config.get("browserVersion", "latest")

    # print("Capabilities:", capabilities)
    options.set_capability('bstack:options', capabilities['bstack:options'])

    bs_url = "https://hub-cloud.browserstack.com/wd/hub"
    try:
        driver = webdriver.Remote(command_executor=bs_url, options=options)
        print("BrowserStack driver initialized successfully.")
        return driver
    except Exception as e:
        print(f"Failed to initialize BrowserStack driver: {e}")
        raise

def set_session_name(driver, name):
    executor_object = {'action': 'setSessionName', 'arguments': {'name': name}}
    driver.execute_script(f"browserstack_executor: {json.dumps(executor_object)}")
    print(f"Set session name to: {name}")

def set_session_status(driver, status, reason):
    executor_object = {'action': 'setSessionStatus', 'arguments': {'status': status, 'reason': reason}}
    driver.execute_script(f"browserstack_executor: {json.dumps(executor_object)}")
    print(f"Set session status to {status}: {reason}")

def run_test(config, config_id):
    driver = setup_browserstack_driver(config)
    try:
        is_desktop = 'os' in config
        if is_desktop:
            test_name = f"Opinion Scraper - {config['browserName']} on {config['os']} {config['osVersion']}"
            print(f"[+] Running test configuration {config_id}: {config['browserName']}")
        else:
            device_name = config['deviceName']
            test_name = f"Opinion Scraper - {config['browserName']} on {device_name}"
            print(f"[+] Running test configuration {config_id}: {config['browserName']} - {device_name}")

        set_session_name(driver, test_name)

        print(f"[Config {config_id}] Navigating to target site...")
        article_links = get_opinion_articles(driver)
        print(f"[Config {config_id}] Found {len(article_links)} article links: {article_links}")
        articles_data = []

        for i, url in enumerate(article_links):
            print(f"[Config {config_id}] Scraping article {i+1}: {url}")
            data = extract_article_data(driver, url)
            articles_data.append(data)
            print(f"[Config {config_id}] Article {i+1} (ES): {data['title']}")
            print(f"[Config {config_id}] Content Snippet: {data['content'][:200]}...")
            if data['image_path']:
                print(f"[Config {config_id}] Image saved at: {data['image_path']}")

        titles_es = [a['title'] for a in articles_data]
        print(f"[Config {config_id}] Titles (ES): {titles_es}")
        titles_en = translate_titles_rapidapi(titles_es)

        print(f"[Config {config_id}] Translated Titles (EN):")
        for title in titles_en:
            print(f"- {title}")

        repeated_words = analyze_headers(titles_en)
        if repeated_words:
            print(f"[Config {config_id}] Repeated Words (more than twice):")
            for word, count in repeated_words.items():
                print(f"'{word}': {count}")
        else:
            print(f"[Config {config_id}] No repeated words found.")

        set_session_status(driver, "passed", "Test completed successfully")

    except Exception as e:
        set_session_status(driver, "failed", f"Test failed due to: {str(e)}")
        print(f"[X] Error in configuration {config_id}: {str(e)}")
        raise

    finally:
        driver.quit()
        print(f"[Done] Configuration {config_id} test completed.")

def run_parallel_tests():
    config = load_browserstack_config()
    configurations = config['platforms']
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(configurations)) as executor:
        futures = [executor.submit(run_test, platform, idx + 1) for idx, platform in enumerate(configurations)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    try:
        run_parallel_tests()
    except Exception as e:
        print(f"Script failed: {e}")
        sys.exit(1)