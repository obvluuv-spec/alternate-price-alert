import time
from scraper import data, i, complete_scrape_alternate, compare_scrape_alternate
e = 1

time_sleep_boolean = False

while True: 
        if time_sleep_boolean:
                time.sleep(8400)
        else:
                time.sleep(3600)
        print("Round =", e)
        time_sleep_boolean = compare_scrape_alternate(data, i, None)
        e += 1
