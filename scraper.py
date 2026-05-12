import sys
from datetime import datetime
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

start_date = datetime.strptime('01-01-2022', '%d-%m-%Y')
step = sys.argv[1] if len(sys.argv) > 1 else "all"

def run_with_driver(fn, *args):
    driver = web.setup_driver()
    try:
        fn(driver, *args)
    finally:
        web.teardown_driver(driver)

steps = {
    "votes":            lambda: run_with_driver(download_votes, start_date),
    "meetings":         lambda: download_meetings(start_date),
    "moties":           lambda: run_with_driver(download_moties, start_date),
    "raadsvoorstellen": lambda: run_with_driver(download_raadsvoorstellen, start_date),
    "amendementen":     lambda: run_with_driver(download_amendementen, start_date),
    "brieven":          lambda: run_with_driver(download_brieven, start_date),
    "vragen":           lambda: run_with_driver(download_vragen, start_date),
    "pdf":              lambda: download_pdf(start_date),
    "updates":          lambda: run_with_driver(download_updates, start_date),
    "keywords":         lambda: keywordAnalysis.keywordAnalysis(),
}

if step == "all":
    for name, fn in steps.items():
        print(f"--- Starting: {name} ---")
        fn()
        print(f"--- Done: {name} ---")
else:
    if step not in steps:
        print(f"Unknown step: {step}")
        print(f"Available steps: {', '.join(steps.keys())}")
        sys.exit(1)
    steps[step]()