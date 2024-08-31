from typing import Generator
from bs4 import BeautifulSoup
import requests
from functools import reduce
from functions import get_titles_and_audios

BASE_URL = "https://love-live.fandom.com"

r = requests.get(f"{BASE_URL}/wiki/Songs_BPM_List")

soup = BeautifulSoup(r.text, features="html.parser")

tables = soup.find_all("table")

table_bodies =[table.find('tbody') for table in tables]
table_rows = [table.find_all('tr') for table in tables]
table_rows = reduce(lambda x,y: x+y, table_rows)
table_cells = [table.find('td') for table in table_rows]
table_hrefs = [table.find('a') for table in table_cells if table is not None]
titles_urls = [table.get('href') for table in table_hrefs]

titles_and_audios: Generator[tuple[str, str, str], None, None] = get_titles_and_audios(BASE_URL, titles_urls)


with open("output.csv", 'w') as f:
    f.write("title,audio_url,link\n")
    for ta in titles_and_audios:
        f.write(f'"{ta[0]}","{ta[1]}","{ta[2]}"\n')
