from classes.sub import Sub
from datetime import datetime
import requests

def download_subtitles():
    #Settings
    starting_date = "2024-09-01"
    ending_date = datetime.today().strftime('%Y-%m-%d')
    organisation = 686
    gremia = 1011
    page = 1
    pages = 1



    while page <= pages:
        api = "https://api.notubiz.nl/events?organisation_id="+str(organisation)+"&gremia_ids[]="+str(gremia)+"&date_from="+starting_date+"%2000:00:00&date_to="+ending_date+"%2023:59:59&version=1.10.8&page="+str(page)+'&format=json'


        #get data
        response = requests.get(api)
        response.raise_for_status()
        data = response.json()

        #check pages
        pages = data['pagination']['total_pages']
        page+=1

        for event in data['events']:
            event_api = 'https://'+event['self']+'?format=json'

            s = Sub()
            s.add_speakers_from_eventAPI(event_api)
            s.save()




        print("done")





if __name__ == "__main__":
    print("Nested code only runs in the top-level code environment")
