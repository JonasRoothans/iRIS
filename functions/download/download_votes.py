from bs4 import BeautifulSoup
from classes.vote import Vote
from classes.member import Member
from classes.module import Module
from functions.download import web
import json
import os
import re
from datetime import datetime
from functions.support import cwdpath

def clean(s):
    return s.replace('\n', '').replace('\r', '').strip()

def reallyGoodClean(s):
    #verwijder BP of bestemmingsplan, want die worden nog al eens verwisseld
    s = s.replace(' BP','').replace('bestemmingsplan', '')

    if ':' in s:
        s = s.split(':')[1].strip()
    if ' - ' in s:
        s = s.split(' - ')[-1].strip()
    s = re.sub(r'\([^)]*\)', '', s).strip().replace(' ', '')
    s = s[0:50].lower() #lang zat
    return s


def get_module_from_meeting_url(meeting_url,vote_title,vote_id):

    soup_meeting = web.visitPage('https://raadsinformatie.eindhoven.nl' + meeting_url)

    vote_title = clean(vote_title)
    vote_title_short = reallyGoodClean(vote_title)


    # Find all `li` elements with the class `module_item`
    for module_item in soup_meeting.find_all('li', class_='module_item'):
        if vote_title_short in reallyGoodClean(module_item['data-title']):
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
        elif 'ordevoorstel' in vote_title.lower():
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
    m.meeting_url = meeting_url
    m.title = vote_title
    m.vote_id = vote_id
    m.save()
    return m



def update_vote_per_member(driver, url,fromDate):
    print(url)
    try:
        soup = web.visitPageWithDriver(driver,url)
    except:
        print(f'could not load {url}')
        return

    if soup is None:
        print(f'could not load {url}')
        return

    # Find the ID
    member_id = url.split('/lid/')[1].split('/')[0]


    # Extract the JSON data from the script tag
    script_tag = soup.find('script', id='vote_data')
    if script_tag:
        json_data = script_tag.string
        data = json.loads(json_data)

        # Iterate over recent votes
        recent_votes = data['recent_votes']
        if recent_votes:
            for vote_id, vote_data in recent_votes.items():

                #check if vote is within timeframe:
                date = datetime.strptime(vote_data['date']['date'][0:10],'%Y-%m-%d')
                if date < fromDate:
                    break

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
                v.add_membervote(int(member_id), vote_data['vote'])


                # pair with module module
                if v.module_id is None:
                    try:
                        m = get_module_from_meeting_url(vote_data['url'], vote_data['title'], int(vote_id))
                    except Exception as e:
                        print(f"Error loading module {vote_data['url']}:{e}")
                        m = Module()
                    v.module_id = m.module_id
                elif isinstance(v.module_id, str) and len(v.module_id) < 1 and v.module_id[1] == '_':
                    try:
                        m = get_module_from_meeting_url(vote_data['url'], vote_data['title'], int(vote_id))
                    except Exception as e:
                        print(f"Error loading module {vote_data['url']}:{e}")
                        m = Module()
                    v.module_id = m.module_id
                else:
                    m = Module(v.module_id)

                #sync data.
                m.date = v.date
                m.result = v.result
                m.meeting_url = v.url
                m.title = v.description
                m.vote_id = v.vote_id
                m.connectToMeeting()
                m.save()
        return



def download_votes(driver,fromDate):
    #--get all members
    folder_path = cwdpath(os.path.join('json','members','speaker'))
    member_ids = os.listdir(folder_path)

    #loop over all files
    for member_id in member_ids:
        member = Member(member_id)
        print(member.name)
        if member.url:
            update_vote_per_member(driver, member.url,fromDate)

