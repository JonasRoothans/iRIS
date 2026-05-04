# test_access.py
from functions.download import web

driver = web.setup_driver()
try:
    driver.get("https://raadsinformatie.eindhoven.nl")
    print("SUCCESS:", driver.title)
except Exception as e:
    print("FAILED:", e)
finally:
    web.teardown_driver(driver)