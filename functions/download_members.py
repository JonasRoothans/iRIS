import requests
from bs4 import BeautifulSoup
from getVotes import calculate_agreement, setup_driver, teardown_driver
from classes.member import Member


def scrape(driver):
    # Step 1: Send a request to the website's main page
    url = 'https://raadsinformatie.eindhoven.nl/leden'  # Replace with the actual URL
    print(f"Scraping: {url}")
    response = requests.get(url)
    response.raise_for_status()  # Check that the request was successful

    # Step 2: Parse the HTML content of the main page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Step 3: Find the section with the list of political parties and their members
    # The actual selector will depend on the website's structure
    party_sections = soup.find_all('div', class_='box leden_lijst')

    # Initialize a list to hold all member page URLs
    members_dict = {}

    counter =0 
    # Step 4: Extract party member URLs
    for section in party_sections:

        party_name = section.find('h2').get_text()
        
        # Assuming each party section has a list of members with links
        member_links = section.find_all('a')
        for member_link in member_links:
            counter += 1

            #make a member object
            new_member = Member()
            
            
            member_url = member_link.get('href')
            member_name = member_link.find('span',class_='naam').get_text()
            member_function = member_link.find('span',class_='functie').get_text()
            member_agreement, member_id = calculate_agreement(driver,member_url)
            
            if member_url:
                new_member.speaker_id = member_id
                new_member.name = member_name
                new_member.role = member_function[1:-1] #get rid of ( )
                new_member.party = party_name
                new_member.url = member_url

                #Save member
                new_member.save()
                members_dict[member_id] = new_member
                
                

            
                
    return members_dict

def download_members():
    driver = setup_driver()
    try:
        members= scrape(driver)


        # Sort the list from high to low based on the 'agreement' key
        sorted_agreements = sorted(members, key=lambda x: x['agreement'], reverse=True)

        # Print the names and agreements
        for member in sorted_agreements:
            print(f"Name: {member['name']}, Agreement: {member['agreement']:.2f}%")
            
    finally:
        teardown_driver(driver)





if __name__ == "__main__":
    main()
        
    
