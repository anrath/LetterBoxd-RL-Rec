import requests
from bs4 import BeautifulSoup
import datetime
import json
from tqdm import tqdm
import asyncio
import aiohttp

def get_pages(username):
    url = f"https://letterboxd.com/{username}/films/diary"
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

def extract_diary_data(content):
    extracted_data = []
    content = content.replace('\n', '')
    content = content.replace('\t', '')
    soup = BeautifulSoup(content, 'html.parser')

    # Iterate over each row in the table body
    for row in soup.find_all('tr', class_='diary-entry-row'):
        # href="/neahlekan/films/diary/for/2024/03/16/"
        date_href = row.find('td', class_='td-day').find('a')['href']
        date = "-".join(date_href.split('/')[-4:-1])

        # Extract the film slug
        film_slug = row.find('div', {'data-film-slug': True}).get('data-film-slug')

        # Extract the rating
        rating = row.find('td', class_='td-rating').get_text(strip=True)
        rating = rating.count('★') + rating.count('½') * 0.5

        # Determine boolean values for Like, Rewatch, and Review
        like = bool(row.find('td', class_='td-like').find('span', class_='icon-liked'))
        rewatch = bool(row.find('td', class_='td-rewatch').find('span', class_='icon-rewatch'))
        review = bool(row.find('td', class_='td-review').find('a', class_='icon-review'))

        # Append the extracted data to the list
        extracted_data.append({
            'date': date,
            'film_slug': film_slug,
            'rating': rating,
            'like': like,
            'rewatch': rewatch,
            'review': review
        })

    return extracted_data


async def scrape_user_data(username, page_index):
    async with aiohttp.ClientSession() as session:
        data = []
        tasks = []
        for page in range(1, page_index):
            url = f"https://letterboxd.com/{username}/films/diary/page/{page}/"
            tasks.append(fetch_page(session, url))
        pages = await asyncio.gather(*tasks)
        for page_content, _, _ in pages:
            if page_content:
                page_data = extract_diary_data(page_content)
                data.extend(page_data)

    return data

with open('users.txt') as file:
    num_lines = sum(1 for _ in file)
    file.seek(0)  # Reset file pointer to the beginning
    for i, user in enumerate(tqdm(file, total=num_lines)):
        username = user.strip()
    
        page_index = get_pages(username)
        tqdm.write(f"Processing: {username}, Page Index: {page_index}")
        if page_index > 0:
            data = asyncio.run(scrape_user_data(username, page_index))
            with open(f'temp/{username}.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)

