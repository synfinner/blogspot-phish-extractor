#!/usr/bin/env python3

'''Python script to extract blog links from a blogspot profile.'''

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import requests
import re
import argparse

class BlogspotProfile:
    WINDOW_LOCATION_REGEX = re.compile(r'window\.location\s*=\s*["\"]([^"\"]+)["\"]')

    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.blog_links = []

    def fetch_blog_links(self):
        """
        Fetch all blog links from the blogspot profile.
        :return: A list of blog urls
        """
        response = requests.get(self.profile_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        urls = []
        div = soup.find('div', class_='contents-after-sidebar')
        if div:
            h2 = div.find('h2', string='My blogs')
            if h2:
                ul = h2.find_next_sibling('ul')
                if ul:
                    for li in ul.find_all('li'):
                        a = li.find('a', href=True)
                        if a:
                            urls.append(a['href'])
        self.blog_links = urls
        return urls

class RedirectResolver:
    WINDOW_LOCATION_REGEX = re.compile(r'window\.location\s*=\s*["\"]([^"\"]+)["\"]')

    @staticmethod
    async def resolve(session, url):
        """
        Asynchronously get the window.location value from the page (redirect URL).
        :param session: aiohttp ClientSession
        :param url: The url to get the redirect from
        :return: The redirect url
        """
        try:
            async with session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                script = soup.find('script', string=lambda s: s and 'window.location' in s)
                if script:
                    match = RedirectResolver.WINDOW_LOCATION_REGEX.search(script.string)
                    if match:
                        return match.group(1)
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

async def main():
    parser = argparse.ArgumentParser(description="Extract and follow blog links from a Blogspot profile.")
    parser.add_argument("-p", "--profile-url", required=True, help="The URL of the Blogspot profile to extract links from.")
    parser.add_argument("--sleep", type=float, default=0.25, dest="sleep_seconds",
                        help="Seconds to sleep between requests (default: 0.25)")
    parser.add_argument("-c","--concurrency", type=int, default=10, dest="concurrency",
                        help="Maximum number of concurrent requests (default: 10)")
    args = parser.parse_args()

    profile_url = args.profile_url
    sleep_seconds = args.sleep_seconds
    concurrency = args.concurrency

    profile = BlogspotProfile(profile_url)
    links = profile.fetch_blog_links()
    unique_links = set()

    # Use a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency)

    async def resolve_with_semaphore(session, link):
        async with semaphore:
            result = await RedirectResolver.resolve(session, link)
            return link, result

    async with aiohttp.ClientSession() as session:
        queue = asyncio.Queue()
        unique_links = set()

        async def producer():
            for i, link in enumerate(links):
                if i > 0:
                    await asyncio.sleep(sleep_seconds)
                asyncio.create_task(consumer_task(link))

        async def consumer_task(link):
            result = await RedirectResolver.resolve(session, link)
            await queue.put((link, result))

        async def consumer():
            completed = 0
            total = len(links)
            while completed < total:
                link, redirect_link = await queue.get()
                print(f"{link} -> {redirect_link}")
                sys.stdout.flush()
                if redirect_link:
                    unique_links.add(redirect_link)
                completed += 1

        await asyncio.gather(producer(), consumer())

    print("\nUnique Redirecting Links:")
    for link in unique_links:
        print(link)

if __name__ == '__main__':
    asyncio.run(main())