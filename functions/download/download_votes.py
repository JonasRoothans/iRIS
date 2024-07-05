from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from classes.vote import Vote
from datetime import datetime
import json




def calculate_agreement(driver, url):
    driver.get(url)

    # Initialize counters
    total_votes_count = 0
    corresponding_votes_count = 0
    other_count = 0

    try:
        # Extract the page source after JavaScript has run
        page_source = driver.page_source

        # Parse the rendered HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the script tag containing the JSON data
        script_tag = soup.find('script', id='vote_data')

        # Find the ID
        member_id = soup.find('h2', class_='lid_header')['data-role_id']

        # Extract the JSON data from the script tag
        if script_tag:
            json_data = script_tag.string

            # Parse the JSON data
            data = json.loads(json_data)

            # Access the specific data you need
            total_votes = data['total_votes']
            # Access the recent votes
            recent_votes = data['recent_votes']

            # Iterate over recent votes
            if recent_votes:
                for vote_id, vote_data in recent_votes.items():
                    total_votes_count += 1
                    vote = vote_data['vote']
                    result = vote_data['result']

                    # Check if vote is 'voor' and result is 'aangenomen'
                    if vote == 'voor' and result == 'aangenomen':
                        corresponding_votes_count += 1
                    elif vote == 'tegen' and result == 'verworpen':
                        corresponding_votes_count += 1
                    else:
                        other_count += 1

                    # Save this information to the Vote Object
                    v = Vote(int(vote_id))
                    if v.description is None:
                        v.description = vote_data['title']
                    if v.result is None:
                        v.result = vote_data['result']
                    if v.url is None:
                        v.url = vote_data['url']
                    if v.date is None:
                        v.date = vote_data['date']['date'][0:10]
                    v.add_membervote(int(member_id), vote)

                # Calculate the percentage of corresponding votes
                percentage_corresponding_votes = (
                                                             corresponding_votes_count / total_votes_count) * 100 if total_votes_count > 0 else 0
            else:
                percentage_corresponding_votes = 0

            return percentage_corresponding_votes, member_id
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

