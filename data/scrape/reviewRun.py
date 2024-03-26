import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp
from multiprocessing import Pool, cpu_count
from datetime import datetime

def get_pages(username):
    url = f"https://letterboxd.com/{username}/films/reviews/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {username}")
        return -1
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_='paginate-pages')
    return int(pagination.find_all('a')[-1].text) if pagination else -1

async def fetch_page(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to retrieve the webpage: {url}")
            return None
        return await response.text()

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
    
async def scrape_user_data(username):
    page_index = get_pages(username)
    if page_index <= 0:
        return
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, f"https://letterboxd.com/{username}/films/reviews/page/{page}/") for page in range(1, page_index + 1)]
        pages = await asyncio.gather(*tasks)
        data = [extract_reviews_data(page) for page in pages if page]
    with open(f'review/{username}.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def process_user(username):
    asyncio.run(scrape_user_data(username.strip()))

def main():
    with open('users.txt') as file:
        users = file.readlines()

    # Determine the number of processes to use
    num_processes = 8

    with Pool(processes=num_processes) as pool:
        pool.map(process_user, users)

if __name__ == "__main__":
    main()