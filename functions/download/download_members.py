from classes.member import Member
from functions.download import web
import re


def scrape(driver):
    #Send a request to the website's main page
    url = 'https://raadsinformatie.eindhoven.nl/leden'
    soup = web.visitPage(url)

    #Find the section with the list of political parties and their members
    party_sections = soup.find_all('div', class_='box leden_lijst')

    # Init
    members_dict = {}
    counter = 0

    # Extract party member URLs
    for section in party_sections:
        party_name = section.find('h2').get_text()

        # Each party section has a list of members with links
        member_links = section.find_all('a')
        for member_link in member_links:
            counter += 1

            # make a member object
            new_member = Member()
            member_url = member_link.get('href')
            member_name = member_link.find('span', class_='naam').get_text()
            member_function = member_link.find('span', class_='functie').get_text()

            #--load member_url to get the speaker_id
            soup_member  = web.visitPageWithDriver(driver,member_url) #this is needed to get the javascript things
            member_id  = soup_member.find('h2',class_='lid_header')['data-role_id']

            #get the person_id
            try:
                url_to_last_speak = soup_member.find('ul', id='speaking').find('a')['href']
                person_id = re.search( r'person_id=(\d+)',url_to_last_speak).group(1)
            except:
                print(f'{member_name} heeft nog nooit gesproken')


            if member_url:
                new_member.speaker_id = member_id
                new_member.person_id = person_id
                new_member.name = member_name
                new_member.role = member_function[1:-1]  # get rid of ( )
                new_member.party = party_name
                new_member.url = member_url

                # Save member
                new_member.save()
                members_dict[member_id] = new_member

            #----DEBUG
            #print('DEBUG MODE: CONTINUING AFTER FIRST MEMBER')
            #return
            #------

    return members_dict


def download_members(driver):
    members = scrape(driver)
    return members



if __name__ == "__main__":
    print("Nested code only runs in the top-level code environment")



