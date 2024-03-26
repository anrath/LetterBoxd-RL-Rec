access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZDE5Nzg2YTZmMzM5M2U1NWFmYzNkOGI3Yjg1NjYzZiIsInN1YiI6IjY1ZmMxODExN2Y2YzhkMDE2MzZjMWY2ZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.6eQ5wlK_vJ1uB8wrYd5i2S1zYin__5JMaBg80OW1eOQ"

import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from tqdm.asyncio import tqdm_asyncio

async def make_request(session, url, access_token):
    """
    Asynchronously send a GET request to the specified URL with an Authorization header.

    :param session: aiohttp ClientSession for making HTTP requests
    :param url: URL to which the GET request is sent
    :param access_token: Authorization token for API access
    :return: JSON response from the server
    """
    async with session.get(url, headers={"Authorization": f"Bearer {access_token}"}) as response:
        return await response.json()

async def fetch_movies_for_range(session, start_date, end_date, access_token):
    """
    Asynchronously fetch movies from the API within the specified date range.

    :param session: aiohttp ClientSession for making HTTP requests
    :param start_date: Start date in YYYY-MM-DD format
    :param end_date: End date in YYYY-MM-DD format
    :param access_token: Authorization token for API access
    :return: List of movie results
    """
    base_url = "https://api.themoviedb.org/3/discover/movie"
    url = f"{base_url}?page=1&sort_by=popularity.desc&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}"
    response = await make_request(session, url, access_token)
    total_pages = response["total_pages"]
    results = response["results"]

    if total_pages > 500:
        mid_date = (datetime.fromisoformat(start_date) + (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)) / 2).date()
        left_results = await fetch_movies_for_range(session, start_date, str(mid_date), access_token)
        right_results = await fetch_movies_for_range(session, str(mid_date + timedelta(days=1)), end_date, access_token)
        results = left_results + right_results
    else:
        tasks = [
            asyncio.create_task(make_request(session, f"{base_url}?page={page}&sort_by=popularity.desc&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}", access_token))
            for page in range(2, total_pages + 1)
        ]
        for task in tqdm_asyncio(asyncio.as_completed(tasks), total=len(tasks), desc=f"Fetching movies for {start_date} through {end_date}"):
            page_results = await task
            results.extend(page_results["results"])

    return results

async def fetch_movies_by_year(session, year, access_token):
    """
    Asynchronously fetch movies for each month of the specified year and handle pagination.

    :param session: aiohttp ClientSession for making HTTP requests
    :param year: Year for which to fetch movies
    :param access_token: Authorization token for API access
    """
    tasks = [
        fetch_movies_for_range(session, f"{year}-{month:02d}-01", f"{year}-{month:02d}-{(datetime(year, month + 1, 1) - timedelta(days=1)).day:02d}", access_token)
        for month in range(1, 13)
    ]
    results = []
    for task in asyncio.as_completed(tasks):
        month_results = await task
        results.extend(month_results)

    # Save results to a JSON file
    with open(f"data/movies_{year}.json", "w") as f:
        f.write(json.dumps(results, indent=4))

async def main(access_token):
    async with aiohttp.ClientSession() as session:
        # for year in [2022, 2023, 2024]:
        for year in [2023, 2024]:
            print(f"Fetching movies for year {year}")
            await fetch_movies_by_year(session, year, access_token)

asyncio.run(main(access_token))
