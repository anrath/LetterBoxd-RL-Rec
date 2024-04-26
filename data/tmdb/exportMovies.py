access_token = ""

import requests
import json
from datetime import datetime, timedelta
from tqdm import tqdm

def make_request(url, access_token):
    """
    Send a GET request to the specified URL with an Authorization header.

    :param url: URL to which the GET request is sent
    :param access_token: Authorization token for API access
    :return: JSON response from the server
    """
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    return response.json()

def fetch_movies_for_range(start_date, end_date, access_token):
    """
    Fetch movies from the API within the specified date range.

    :param start_date: Start date in YYYY-MM-DD format
    :param end_date: End date in YYYY-MM-DD format
    :param access_token: Authorization token for API access
    :return: List of movie results
    """
    base_url = "https://api.themoviedb.org/3/discover/movie"
    url = f"{base_url}?page=1&sort_by=popularity.desc&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}"
    response = make_request(url, access_token)
    total_pages = response["total_pages"]
    results = response["results"]

    # Recursively split the date range if total_pages exceeds 500
    if total_pages > 500:
        mid_date = (datetime.fromisoformat(start_date) + (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)) / 2).date()
        results = fetch_movies_for_range(start_date, str(mid_date), access_token) + fetch_movies_for_range(str(mid_date + timedelta(days=1)), end_date, access_token)
    else:
        for page in tqdm(range(2, total_pages + 1), desc=f"Fetching movies for {start_date} through {end_date}"):
            url = f"{base_url}?page={page}&sort_by=popularity.desc&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}"
            response = make_request(url, access_token)
            results.extend(response["results"])

    return results

def fetch_movies_by_year(year, access_token):
    """
    Fetch movies for each month of the specified year and handle pagination.

    :param year: Year for which to fetch movies
    :param access_token: Authorization token for API access
    :return: Dictionary of results keyed by year
    """
    results = []
    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        next_month = month + 1 if month < 12 else 1
        next_year = year + 1 if month == 12 else year
        end_date = f"{year}-{month:02d}-{(datetime(next_year, next_month, 1) - timedelta(days=1)).day:02d}"
        results.extend(fetch_movies_for_range(start_date, end_date, access_token))

    # Save results to a JSON file
    with open(f"data/movies_{year}.json", "w") as f:
        f.write(json.dumps(results, indent=4))

# Example usage
# years = [2022, 2023, 2024]
years = [2023, 2024]
for year in years:
    print(f"Fetching movies for year {year}")
    fetch_movies_by_year(year, access_token)
