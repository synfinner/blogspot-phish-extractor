#!/usr/bin/env python3

'''Python script to extract blog links from a blogspot profile.'''

import requests
from bs4 import BeautifulSoup
import sys
from time import sleep
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
    def resolve(url):
        """
        Get the window.location value from the page (redirect URL).
        :param url: The url to get the redirect from
        :return: The redirect url
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', string=lambda s: s and 'window.location' in s)
        if script:
            match = RedirectResolver.WINDOW_LOCATION_REGEX.search(script.string)
            if match:
                return match.group(1)
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract and follow blog links from a Blogspot profile.")
    parser.add_argument("-p", "--profile-url", required=True, help="The URL of the Blogspot profile to extract links from.")
    parser.add_argument("--sleep", type=float, default=0.25, dest="sleep_seconds",
                        help="Seconds to sleep between requests (default: 0.25)")
    args = parser.parse_args()

    profile_url = args.profile_url
    sleep_seconds = args.sleep_seconds

    # Create a BlogspotProfile instance and fetch blog links
    profile = BlogspotProfile(profile_url)
    links = profile.fetch_blog_links()

    unique_links = set()
    for link in links:
        redirect_link = RedirectResolver.resolve(link)
        print(f"{link} -> {redirect_link}")
        if redirect_link:
            unique_links.add(redirect_link)
        sleep(sleep_seconds)

    print("\nUnique Redirecting Links:")
    for link in unique_links:
        print(link)