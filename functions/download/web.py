from selenium import webdriver
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
    chromedriver_path = 'chrome/chromedriver'

    # Initialize the WebDriver
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
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
