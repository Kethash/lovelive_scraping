from functools import reduce
from typing import Generator
from bs4 import BeautifulSoup
import requests
import os
from functions import extract_page_urls, get_titles_and_audios
from multiprocessing import Pool

BASE_URL = "https://love-live.fandom.com"

r = requests.get(f"{BASE_URL}/wiki/Songs_BPM_List")

print("Fetching songs urls")

group_name_and_page_urls: list[tuple[str, str]] = extract_page_urls(BeautifulSoup(r.text, features="html.parser"))

print("Beginning scraping !")
print(f"There are {len(group_name_and_page_urls)} titles to scrap !")

output = open("output.csv", "w")
output.write("group,title,audio_url,link,image_link,image_alt\n")
output.close()

print("Writing to csv")
def run_multi(group_name_and_page_url: str):
    """run_multi
    -----
    Run scraping into multiple processes
    Params:
        title_url (str): The url of the song
    """

    # Fetching audios sources in the song page
    titles_and_audios: Generator[tuple[str, str, str], None, None] = get_titles_and_audios(f"{BASE_URL}/{group_name_and_page_url[1]}")

    # Writing the outputs in csv
    with open("output.csv", 'a') as f:
        for ta in titles_and_audios:
            f.write(f'"{group_name_and_page_url[0]}","{ta[0]}","{ta[1]}","{ta[2]}","{ta[3]}","{ta[4]}"\n')

# Running in a pool with the size of the number of cpus inside the machine
with Pool(os.cpu_count()) as p:
    p.map(run_multi, group_name_and_page_urls)

print("Done ! Written in output.csv")
