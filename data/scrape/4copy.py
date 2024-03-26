import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from tqdm import tqdm
import asyncio
import aiohttp

def get_pages(username):
    url = f"https://letterboxd.com/{username}/films/reviews"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {username}")
    soup = BeautifulSoup(response.content, 'html.parser')

    pagination = soup.find('div', class_='paginate-pages')
    if pagination:
        page_index = int(pagination.find_all('a')[-1].text)
    else:
        page_index = -1

    return page_index


async def fetch_page(session, url, key=None):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to retrieve the webpage: {url}")
            return None, url, key
        return await response.text(), url, key

def extract_reviews_data(content):
    extracted_data = []
    # content = content.replace('\n', '')
    # content = content.replace('\t', '')
    soup = BeautifulSoup(content, 'html.parser')

    # Iterate over each row in the table body
    for film in soup.find_all('li', class_='film-detail'):
        
        # Date watched
        try:
            date_watched = film.find('span', class_='date').find(class_='_nobr').text.strip() #06 Feb 2024
            date = datetime.strptime(date_watched, '%d %b %Y').strftime('%Y-%m-%d')  # Formatting the date
        except:
            try:
                date_watched = film.find('span', class_='date').find('time')['datetime']
                date = datetime.strptime(date_watched, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')  # Formatting the date
            except:
                try:
                    date_watched = film.find('span', class_='date').find('time')['datetime']
                    date = datetime.strptime(date_watched, '%Y-%m-%dT%H:%M:%S%fZ').strftime('%Y-%m-%d')  # Formatting the date
                except:
                    date = ''

        # Rating
        try:
            rating_raw = film.find('span', class_='rating').text.strip()
            rating = rating_raw.count('★') + rating_raw.count('½') * 0.5
        except:
            rating = ''

        # Extract the film slug
        film_slug = film.find('div', {'data-film-slug': True}).get('data-film-slug')

        # Review text
        try:
            review_text = film.find('div', class_='body-text').find('p').text.strip()
        except:
            continue

        # Append the extracted data to the list
        extracted_data.append({
            'date': date,
            'film_slug': film_slug,
            'rating': rating,
            'review': review_text
        })

    return extracted_data


async def scrape_user_data(username, page_index):
    async with aiohttp.ClientSession() as session:
        data = []
        tasks = []
        for page in range(1, page_index):
            url = f"https://letterboxd.com/{username}/films/reviews/page/{page}/"
            tasks.append(fetch_page(session, url))
        pages = await asyncio.gather(*tasks)
        for page_content, _, _ in pages:
            if page_content:
                page_data = extract_reviews_data(page_content)
                data.extend(page_data)

    return data

with open('copy4.txt') as file:
    num_lines = sum(1 for _ in file)
    file.seek(0)  # Reset file pointer to the beginning
    for i, user in enumerate(tqdm(file, total=num_lines)):
        username = user.strip()
    
        page_index = get_pages(username)
        tqdm.write(f"Processing: {username}, Page Index: {page_index}")
        if page_index > 0:
            data = asyncio.run(scrape_user_data(username, page_index))
            with open(f'review/{username}.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)

