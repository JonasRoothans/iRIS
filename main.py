from functions.download import download_subtitles, download_votes, download_members, download_moties, download_raadsvoorstellen, download_amendementen,download_pdf, web
import json
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def get_settings():
    settings_path = f'{os.getcwd()}/json/settings.json'
    if os.path.exists(settings_path):
        return json.load(settings_path)
    else:
        settings = {}
        settings['last_update_votes'] = '2020-04-01'
        settings['last_update_moties'] = '2020-04-01'
        settings['last_update_raadsvoorstellen'] = '2020-04-01'
        settings['last_update_amendementen'] = '2020-04-01'
        settings['buffer_months'] = 3
        return settings

def save_settings(settings):
    settings_path = f'{os.getcwd()}/json/settings.json'
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
    print('settings updated')

def get_startDate(settings,method):
    date_obj = datetime.strptime(settings[method], "%Y-%m-%d")

    # Subtract 'buffer' months using relativedelta
    return date_obj - relativedelta(months=settings['buffer_months'])


if __name__ == "__main__":
    #--start up chrome driver
    driver = web.setup_driver()
    settings = get_settings()

    #----DOWNLOAD MEMBERS---#
    #download_members.main(driver)

    # ----DOWNLOAD VOTES and make module placeholders---#
    #download_votes.download_votes(driver, get_startDate(settings,'last_update_votes'))
    #settings['last_update_votes'] = date.today().strftime('%Y-%m-%d')

    # --- DOWNLOAD moties --- #
    #download_moties.download_moties(driver, get_startDate(settings,'last_update_moties'))
    #settings['last_update_moties'] = date.today().strftime('%Y-%m-%d')
    #web.teardown_driver(driver)

    #driver = web.setup_driver()
    #download_raadsvoorstellen.download_raadsvoorstellen(driver,get_startDate(settings,'last_update_raadsvoorstellen'))
    #settings['last_update_raadsvoorstellen'] = date.today().strftime('%Y-%m-%d')
    #web.teardown_driver(driver)

    #driver = web.setup_driver()
    #download_amendementen.download_amendementen(driver)
    #web.teardown_driver(driver)

    download_pdf.download_pdf()

    #---DOWNLOAD SUBTITLES----#
    #download_subtitles.download_subtitles()

    #--Tear down driver



        
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

document:https://api.notubiz.nl/document/13701962/2  laatste getal is definitie versie. eerdere versies vereisen een token

motie gegevens: https://raadsinformatie.eindhoven.nl/modules/6/moties_en_toezeggingen/955625

"""
