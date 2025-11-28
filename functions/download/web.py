from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests


def setup_driver():
    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headless Chrome
    chrome_options.add_argument('--disable-gpu')


    # Specify the path to the ChromeDriver
    chromedriver_path = 'functions/download/chrome/chromedriver'

    # Initialize the WebDriver
    #service = ChromeService(executable_path=chromedriver_path)
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    return driver

def teardown_driver(driver):
    driver.quit()

def visitPage(url):
    #print(f"Scraping: {url}")
    response = requests.get(url)
    if not response.ok:
        print(f"{url}: did not load correctly")

    #Parse the HTML content of the main page
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def visitPageWithDriver(driver,url):
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def visitPageAndWaitForPolitiekPortaal(driver, url):
    driver.get(url)
    try:
        # Wait for the element with the `politiek-portaal` selector to ensure the dynamic content is starting to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "politiek-portaal"))
        )

        # Wait for the text 'Hoofddocument' within 'politiek-portaal' for assurance the content is fully loaded
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Hoofddocument')]"))
        )

        # Wait until the 'loading-text' class is no longer present in the DOM
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "text-loading"))
        )

        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.CLASS_NAME,'modules-public-app-history-documents'))
        )

        #WebDriverWait(driver, 30).until(
        #    EC.presence_of_element_located((By.TAG_NAME, 'shared-timeline'))
        #)

        print("Page loaded, 'Hoofddocument' is present, and 'loading-text' is no longer visible.")

        # Now that the content is fully loaded, retrieve the page source
        page_source = driver.page_source

        # Use BeautifulSoup to parse the fully rendered HTML content
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    except Exception as e:
        print(f"An error occurred: {e}")

        # Wait for the text 'Raadsbesluit' as a fallback
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Raadsbesluit')]"))
        )

        # Wait until the 'loading-text' class is no longer visible (fallback case)
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "loading-text"))
        )

        print("Page loaded, 'Raadsbesluit' is present, and 'loading-text' is no longer visible.")

        # Now retrieve the page source
        page_source = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

def visitPageAndWaitForVraag(driver, url):
    driver.get(url)
    try:

        # Wait until the 'loading-text' class is no longer present in the DOM
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-item"))
        )

        print("Page loaded, 'Vraag' is present")

        # Now that the content is fully loaded, retrieve the page source
        page_source = driver.page_source

        # Use BeautifulSoup to parse the fully rendered HTML content
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    except Exception as e:
        print(f"An error occurred: {e}")

        # Wait until the 'loading-text' class is no longer present in the DOM
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-item"))
        )

        print("Page loaded, 'Raadsbesluit' is present, and 'loading-text' is no longer visible.")

        # Now retrieve the page source
        page_source = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup


def visitPageAndWaitMetaInfo(driver, url):

    try:
        visitPage(url)
    except:
        return None


    driver.get(url)
    try:
        # Wait for the element with the `politiek-portaal` selector to ensure the dynamic content is starting to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "politiek-portaal"))
        )

        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.ID,'module-item-details'))
        )

        # Wait until the 'loading-text' class is no longer present in the DOM
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "text-loading"))
        )



        # Now that the content is fully loaded, retrieve the page source
        page_source = driver.page_source

        # Use BeautifulSoup to parse the fully rendered HTML content
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    except Exception as e:
        print(f"An error occurred: {e}")

        # Wait for the text 'Raadsbesluit' as a fallback
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Raadsbesluit')]"))
        )

        # Wait until the 'loading-text' class is no longer visible (fallback case)
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "loading-text"))
        )

        print("Page loaded, 'Raadsbesluit' is present, and 'loading-text' is no longer visible.")

        # Now retrieve the page source
        page_source = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup




