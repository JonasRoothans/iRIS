from bs4 import BeautifulSoup
from classes.vote import Vote
from classes.member import Member
from classes.module import Module
from functions.download import web
import json
import os
import re
def get_module_from_meeting_url(meeting_url,vote_title,vote_id):
    #remove newline characters:
    vote_title = vote_title.replace('\n', '').replace('\r', '')
    soup_meeting = web.visitPage('https://raadsinformatie.eindhoven.nl'+meeting_url)

    # Find all `li` elements with the class `module_item`
    for module_item in soup_meeting.find_all('li', class_='module_item'):
        # Check if this item has the target vote title in the `data-title` attribute
        if module_item.find('a').text.replace('\n', '').replace('\r', '') == vote_title:
            # Extract the required data
            m = Module(module_item['data-module_item_id'])
            if m.url is None:
                m.url  = module_item.find('a')['href']
            if m.type is None:
                m.type =  module_item.find('span', class_='module_item_type').text.strip().split()[0]
                #-- Some rules to overpower "raadvoorstel"
                if 'initiatiefvoorstel' in vote_title.lower():
                    m.type = 'Initiatiefvoorstel'
                if 'ordevoorstel' in vote_title.lower():
                    m.type = 'Ordevoorstel'
            break

    if 'm' not in vars():
        if 'amendement' in vote_title.lower():
            m = Module(f'a_{vote_id}')
            if m.type is None:
                m.type = 'Amendement'
        if 'ordevoorstel' in vote_title.lower():
            m = Module(f'o_{vote_id}')
            if m.type is None:
                m.type = 'Ordevoorstel'
        elif 'raadsvoorstel' in vote_title.lower():
            m = Module(f'r_{vote_id}')
            if m.type is None:
                m.type = 'Raadsvoorstellen'
        elif 'initiatiefvoorstel' in vote_title.lower():
            m = Module(f'i_{vote_id}')
            if m.type is None:
                m.type = 'Initiatiefvoorstel'
        elif 'motie' in vote_title.lower():
            m = Module(f'm_{vote_id}')
            if m.type is None:
                m.type = 'Moties'

        else:
            print(f"Module for vote with title '{vote_title}' not found.")
            m = Module('x')
        if m.url is None:
            m.url = meeting_url
    m.title = vote_title
    m.vote_id = vote_id
    m.save()
    return m



def update_vote_per_member(driver, url):


    # Initialize counters
    total_votes_count = 0
    corresponding_votes_count = 0
    other_count = 0

    try:
        soup = web.visitPageWithDriver(driver,url)

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
                    if v.module_id is None:
                        # -- get module
                        try:
                            m = get_module_from_meeting_url(vote_data['url'], vote_data['title'], int(vote_id))
                        except Exception as e:
                            print(f"Error loading module {vote_data['url']}:{e}")
                            m = Module()
                        v.module_id = m.module_id
                    if v.description is None:
                        v.description = vote_data['title']
                    if v.result is None:
                        v.result = vote_data['result']
                    if v.url is None:
                        v.url = vote_data['url']
                    if v.date is None:
                        v.date = vote_data['date']['date'][0:10]
                    v.add_membervote(int(member_id), vote)

                    if v.date < "2022-01-01":
                        print('reached time horizon')
                        break


                # Calculate the percentage of corresponding votes
                percentage_corresponding_votes = (
                                                             corresponding_votes_count / total_votes_count) * 100 if total_votes_count > 0 else 0
            else:
                percentage_corresponding_votes = 0

            return percentage_corresponding_votes, member_id
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def download_votes(driver):
    #--get all members
    folder_path = './json/members/speaker'
    member_ids = os.listdir(folder_path)
    for member_id in member_ids:
        member = Member(member_id)
        print(member.name)
        update_vote_per_member(driver, member.url)



    #-- loop over members

