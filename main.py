import os
import importlib

def import_all_functions_from(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"functions.{module_name}")
            globals().update({name: obj for name, obj in module.__dict__.items() if callable(obj)})
            print(f"Imported: {module_name}")







if __name__ == "__main__":
    # Import all functions from the functions directory
    import_all_functions_from("functions")

    #----DOWNLOAD MEMBERS---#
    members = download_members()
    for member in members:
        print(member)

    #----DOWNLOAD VOTES----#
    votes = get_votes()
    for vote in votes:
        print(vote)


        
"""notes to navigate the api:

organisation_id
Eindhoven: 686


gremia_ids
Raadsvergadering: 1011
raadsavond: 12330sdf


Search events:
https://api.notubiz.nl/events?organisation_id=686&gremia_ids[]=1011&date_from=2024-01-01%2000:00:00&date_to=2024-03-31%2023:59:59&version=1.10.8&page=1

Raadsvergaderingen: https://api.notubiz.nl/events/meetings/1147888
sprekers etc op een avond: https://api.notubiz.nl/events/1146933

Ondertiteling: https://api.notubiz.nl/media/subtitles?folder=Eindhoven&file=S_16_01_24_NC_EINDHOVEN_RAA.srt
"""
