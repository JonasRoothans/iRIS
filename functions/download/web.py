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
    response.raise_for_status()  # Check that the request was successful

    #Parse the HTML content of the main page
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def visitPageWithDriver(driver,url):
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def visitPageAndWaitForPolitiekPortaal(driver,url):
    driver.get(url)
    try:
        # Here we wait up to 30 seconds for an element in 'politiek-portaal' to contain the dynamic content
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "politiek-portaal "))
        )

        # Wait for the text 'Hoofddocument' within 'politiek-portaal' for an additional assurance it's loaded
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Hoofddocument')]"))
        )

        print("Page loaded, and 'Hoofddocument' is present")

        # Now that the content is fully loaded, retrieve the page source
        page_source = driver.page_source

        # Use BeautifulSoup to parse the fully rendered HTML content
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except:
        # Wait for the text 'Hoofddocument' within 'politiek-portaal' for an additional assurance it's loaded
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Raadsbesluit')]"))
        )

        print("Page loaded, and 'Raadsbesluit' is present")

        # Now that the content is fully loaded, retrieve the page source
        page_source = driver.page_source

        # Use BeautifulSoup to parse the fully rendered HTML content
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup




