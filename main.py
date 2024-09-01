from typing import Generator
from bs4 import BeautifulSoup
import requests
import os
from functions import extract_page_urls, get_titles_and_audios
from multiprocessing import Pool

BASE_URL = "https://love-live.fandom.com"

r = requests.get(f"{BASE_URL}/wiki/Songs_BPM_List")
titles_urls = extract_page_urls(BeautifulSoup(r.text, features="html.parser"))

print("Beginning scraping !")
print(f"There are {len(titles_urls)} titles to scrap !")

output = open("output.csv", "w")
output.write("title,audio_url,link\n")
output.close()

print("Writing to csv")
def run_multi(title_url: str):


    titles_and_audios: Generator[tuple[str, str, str], None, None] = get_titles_and_audios(f"{BASE_URL}/{title_url}")

    with open("output.csv", 'a') as f:
        for ta in titles_and_audios:
            f.write(f'"{ta[0]}","{ta[1]}","{ta[2]}"\n')

with Pool(os.cpu_count()) as p:
    p.map(run_multi, titles_urls)
