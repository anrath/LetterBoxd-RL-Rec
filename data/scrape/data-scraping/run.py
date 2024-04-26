import requests
from bs4 import BeautifulSoup
import datetime
import json

def get_pages(base_url):
    # Extracting additional page URLs
    first_page_url = f"{base_url}1/"
    response = requests.get(first_page_url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")

    soup = BeautifulSoup(response.content, 'html.parser')

    pages = [first_page_url]
    pagination = soup.find('div', class_='paginate-pages')
    if pagination:
        for page in pagination.find_all('a'):
            pages.append(base_url + page.get('href').split('/')[-2] + '/')

    return pages

def get_films(pages):
    # Extracting film data
    films = {}
    for page in pages:
        response = requests.get(page)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage: {page}")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for li in soup.select('ul.poster-list li.poster-container'):
            film_slug = li.find('div', class_='film-poster')['data-film-slug']

            metadata = li.find('p', class_='poster-viewingdata')
            rating = metadata.find('span', class_='rating')
            if rating:
                rating = rating.text
                # ★★★★★ = 10
                # ★★★★½ = 9.5
                rating = rating.count('★') + rating.count('½') * 0.5
            else:
                rating = None
            
            like = metadata.find('span', class_='like')
            if like:
                like = True
            else:
                like = False
            
            review = metadata.find('a', class_='review-micro')
            if review:
                review = True
            else:
                review = False
            
            films[film_slug] = {
                'rating': rating,
                'like': like,
                'review': review
            }
    return films

def get_film_data(films):
    for film_slug, value in films.items():
        base_url = f"https://letterboxd.com/{username}/film/{film_slug}"

        if value['review']:
            url = base_url + "/reviews"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve the webpage: {film_slug}")
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('section', class_='viewings-list').find('ul')
            
            # Initialize a list to store extracted data
            table_data = []
            
            # Iterate through each list item in the table
            for li in table.find_all('li', class_='film-detail'):        
                # Extract rating
                rating = li.find('span', class_='rating').text.strip()
                rating = rating.count('★') + rating.count('½') * 0.5

                
                # Extract date
                date = li.find('span', class_='date').find('span').text.strip()
                try:
                    date = datetime.datetime.strptime(date, '%d %b %Y').strftime('%Y-%m-%d')
                except:
                    try:
                        date = li.find('span', class_='date').find('time')['datetime']
                        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                    except:
                        print(f"Failed to parse date: {date} for film {film_slug}")
                
                # Extract review content
                review_content = li.find('div', class_='body-text').text.strip()
                        
                # Append extracted data to the list
                table_data.append({
                    'rating': rating,
                    'date': date,
                    'review_content': review_content,
                })
        else:
            url = base_url + "/activity"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve the webpage: {film_slug}")
            soup = BeautifulSoup(response.content, 'html.parser')

            table_data = []

            # Find the table element
            table = soup.find('div', class_='activity-table')
            if table:
                # Find all sections containing activity rows
                activity_rows = table.find_all('section', class_='activity-row -basic')

                # Extract data from each activity row
                for row in activity_rows:
                    data = {}

                    activity_description = row.find('p', class_='activity-summary')
                    if activity_description:
                        # Type
                        text = activity_description.text
                        data['activity_type'] = []
                        if "liked" in text:
                            data['activity_type'].append("like")
                        if "rated" in text:
                            data['activity_type'].append("rating")
                        if "reviewed" in text:
                            data['activity_type'].append("review")

                        # Link
                        link = activity_description.find('a', class_='target')['href']
                        data['activity_link'] = link

                        # Actions on other users
                        data['social'] = False
                        if username not in link:
                            data['social'] = True

                    time_tag = row.find('time')
                    if time_tag:
                        # '2024-03-08T09:03:24.911Z'}
                        date = datetime.datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                        data['date'] = date

                    table_data.append(data)

        min_date = min([row['date'] for row in table_data])
        value['date'] = min_date
        # aggregating reviews
        if value['review']:
            value["review_content"] = ""
            for row in table_data:
                value["review_content"] += row['review_content'] + "\n\n"

            # remove terminal newlines
            value["review_content"] = value["review_content"].strip()

        value['activity'] = table_data
    
    return films

def get_data(username):
    base_url = f"https://letterboxd.com/{username}/films/page/"
    pages = get_pages(base_url)
    films = get_films(pages)
    films_complete = get_film_data(films)

    return films_complete


with open('users.txt') as file:
    i=0
    for user in file:
        if i > 10:
            break
        i+=1
        username = user.strip()
        data = get_data(username)

        with open(f'/bigtemp/kl5sq/film-data/{username}.json', 'w') as file:
            json.dump(data, file, indent=4)

