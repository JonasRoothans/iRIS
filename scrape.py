from functions.download.download_updates import download_updates
from functions.download.download_pdf import download_pdf
import keywordAnalysis
from functions.download.download_meetings import download_meetings
from functions.download.download_moties import download_moties
from functions.download.download_vragen import download_vragen
from functions.download.download_votes import download_votes
from functions.download.download_raadsvoorstellen import download_raadsvoorstellen
from functions.download.download_amendementen import download_amendementen
from functions.download.download_brieven import download_brieven
from functions.download import web
from datetime import date, datetime, time


#prepare
driver = web.setup_driver()
start_date = datetime.strptime('01-01-2022', '%d-%m-%Y')


#stemmen
download_votes(driver, start_date)

#meetings
download_meetings(start_date)

#moties
download_moties(driver, start_date)

#raadsvoorstellen
web.teardown_driver(driver)
driver = web.setup_driver()
download_raadsvoorstellen(driver, start_date)


#amendementen
web.teardown_driver(driver)
driver = web.setup_driver()
download_amendementen(driver, start_date)


#brieven
download_brieven(driver, start_date)


#vragen
web.teardown_driver(driver)
driver = web.setup_driver()
download_vragen(driver, start_date)

#bijlages
download_pdf(start_date)

#updates

web.teardown_driver(driver)
driver = web.setup_driver()
download_updates(driver, start_date)


#keywords
keywordAnalysis.keywordAnalysis()


