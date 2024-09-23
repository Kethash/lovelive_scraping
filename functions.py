from functools import reduce
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
        image_src, image_alt = extract_image(url)
        for i, j in zip(extract_titles(tables_rows), extract_audio_urls(tables_rows)):
            yield i.strip(), str(j).strip(), url.strip(), image_src.strip(), image_alt.strip()
        
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

def extract_page_urls(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """extract_page_urls
    -----
    Scrapes the page by its url
    Params:
        soup (BeautifulSoup): The soup of the page
    Returns:
        titles_urls (list[tuple[str, str]]): The group name and the urls of the titles
    """
    group_list = soup.find('div', class_="mw-parser-output")

    song_tables = group_list.find_all(['h2','table'])

    attempt = song_tables[1:]
    artists = [artist.find('a').text.strip() for artist in attempt[0::2]][:-1]
    artists.append("Collaboration") # This one wasn't scraped, consider adding it manually
    title_url_list = attempt[1::2]
    result = []

    for artist, title_urls in zip(artists, title_url_list):
        for title_url in title_urls.find_all('a'):
            result.append((artist, title_url.get('href').strip()))

    return result

def extract_image(url: str) -> tuple[str, str]:
    """extract_image
    -----
    Extract the song image and alt
    Params:
        url (str): the url of the song page
    Returns:
        image_infos (tuple[str, str]): The image url and the alt of the image
    """
    title_page = requests.get(url)
    image = BeautifulSoup(title_page.text, features="html.parser").find("img", class_="pi-image-thumbnail")
    source = image['src']
    alt = image['alt']

    return source, alt
