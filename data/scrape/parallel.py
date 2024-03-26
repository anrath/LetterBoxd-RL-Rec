import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp
from multiprocessing import Pool, cpu_count

def get_pages(username):
    url = f"https://letterboxd.com/{username}/films/diary/"
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

async def scrape_user_data(username):
    page_index = get_pages(username)
    if page_index <= 0:
        return
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, f"https://letterboxd.com/{username}/films/diary/page/{page}/") for page in range(1, page_index + 1)]
        pages = await asyncio.gather(*tasks)
        data = [extract_diary_data(page) for page in pages if page]
    with open(f't2/{username}.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def process_user(username):
    asyncio.run(scrape_user_data(username.strip()))

def main():
    with open('users.txt') as file:
        users = file.readlines()

    # Determine the number of processes to use
    num_processes = cpu_count()-4

    with Pool(processes=num_processes) as pool:
        pool.map(process_user, users)

if __name__ == "__main__":
    main()