from functools import reduce
from tqdm import tqdm
from typing import Generator

import requests
from bs4 import BeautifulSoup


def get_titles_and_audios(url: str) -> Generator[tuple[str, str, str], None, None]:
    """get_titles_and_audios
    -----
    Fetch the titles and the audio source of a song in its page
    Params:
        url (str): The url of the song
    Returns:
        urls_and_sources (Generator[tuple[str,str,str], None, None])
    """

    try:
        title_page = requests.get(url)
        tables = BeautifulSoup(title_page.text, features="html.parser").find_all("table", class_="article-table")
        tables_rows = extract_rows(tables)
        for i, j in zip(extract_titles(tables_rows), extract_audio_urls(tables_rows)):
            yield i.strip(), str(j).strip(), url.strip()
        
    except Exception as e:
        raise Exception



def extract_rows(tables: list) -> list:
    """extract_rows
    -----
    Extracts the rows of the scraped table
    Params:
        tables (list): The HTML tables
    Returns:
        tables_rows (list): The scraped HTML table rows
    """
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
    """extract_titles
    -----
    Extract the titles
    Params:
        tables_rows (list): The list of the extracted tables
    Returns:
        titles (list): The titles
    """
    titles = [title.text for title in tables_rows][1::4]
    return titles

def extract_audio_urls(tables_rows: list) -> list:
    """extract_audio_urls
    -----
    Extract the audio source urls
    Params:
        tables_rows (list): The list of the extracted tables
    Returns:
        audio_urls (list): The audio source urls
    """
    audios_urls = []
    for audio in tables_rows[3::4]:
        if audio.find('audio') is not None:
            audios_urls.append(audio.find('audio').get('src'))
        else:
            audios_urls.append(None)
    return audios_urls

def extract_page_urls(soup: BeautifulSoup) -> list:
    """extract_page_urls
    -----
    Scrapes the page by its url
    Params:
        soup (BeautifulSoup): The soup of the page
    Returns:
        titles_urls (list): The urls of the titles
    """
    tables = soup.find_all("table")

    table_rows = [table.find_all('tr') for table in tables]
    table_rows = reduce(lambda x,y: x+y, table_rows)
    table_cells = [table.find('td') for table in table_rows]
    table_hrefs = [table.find('a') for table in table_cells if table is not None]
    titles_urls = [table.get('href') for table in table_hrefs]

    return titles_urls
