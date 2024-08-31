from typing import Generator
from bs4 import BeautifulSoup
import requests
from functools import reduce
from functions import extract_page_urls, get_titles_and_audios

BASE_URL = "https://love-live.fandom.com"

r = requests.get(f"{BASE_URL}/wiki/Songs_BPM_List")

titles_urls = extract_page_urls(BeautifulSoup(r.text, features="html.parser"))


print("Beginning scraping !")
print(f"There are {len(titles_urls)} titles to scrap !")
titles_and_audios: Generator[tuple[str, str, str], None, None] = get_titles_and_audios(BASE_URL, titles_urls)
print("Writing to csv")

with open("output.csv", 'w') as f:
    f.write("title,audio_url,link\n")
    for ta in titles_and_audios:
        f.write(f'"{ta[0]}","{ta[1]}","{ta[2]}"\n')
