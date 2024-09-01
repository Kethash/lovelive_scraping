from functools import reduce
from tqdm import tqdm
from typing import Generator

import requests
from bs4 import BeautifulSoup


def get_titles_and_audios(base_url: str, title_url: str) -> Generator[tuple[str, str, str], None, None]:

    try:
        full_url: str = f"{base_url}/{title_url}"
        title_page = requests.get(full_url)
        tables = BeautifulSoup(title_page.text, features="html.parser").find_all("table", class_="article-table")
        tables_rows = extract_rows(tables)
        for i, j in zip(extract_titles(tables_rows), extract_audio_urls(tables_rows)):
            yield i.strip(), str(j).strip(), full_url.strip()
        
    except Exception as e:
        raise Exception



def extract_rows(tables: list) -> list:
    tables_rows = [table.find_all('td') for table in tables]
    tables_rows = reduce(lambda x, y: x + y, tables_rows)
    idx = 0
    for i, e in enumerate(tables_rows):
        if e.text == "01\n":
            idx = i
            break
    tables_rows = tables_rows[idx:]
    tables_rows = [t for t in tables_rows if not any('spotify' in iframe.get('src', '') for iframe in t.find_all('iframe'))]
    return tables_rows

def extract_titles(tables_rows: list) -> list:
    titles = [title.text for title in tables_rows][1::4]
    return titles

def extract_audio_urls(tables_rows: list) -> list:
    audios_urls = []
    for audio in tables_rows[3::4]:
        if audio.find('audio') is not None:
            audios_urls.append(audio.find('audio').get('src'))
        else:
            audios_urls.append(None)
    return audios_urls

def extract_page_urls(soup: BeautifulSoup) -> list:
    tables = soup.find_all("table")

    table_rows = [table.find_all('tr') for table in tables]
    table_rows = reduce(lambda x,y: x+y, table_rows)
    table_cells = [table.find('td') for table in table_rows]
    table_hrefs = [table.find('a') for table in table_cells if table is not None]
    titles_urls = [table.get('href') for table in table_hrefs]

    return titles_urls
