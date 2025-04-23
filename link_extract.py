#!/usr/bin/env python3

'''Python script to extract blog links from a blogspot profile.'''

import requests
from bs4 import BeautifulSoup
import sys
from time import sleep
import re
import argparse

WINDOW_LOCATION_REGEX = re.compile(r'window\.location\s*=\s*["\"]([^"\"]+)["\"]')

def get_blogspot_links(profile_url):
    """
    Get all blog links from the blogspot profile.

    This function will return a list of all blogs in the profile.

    :param profile_url: The url of the blogspot profile
    :return: A list of blog urls
    """
    response = requests.get(profile_url)
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
    return urls


def pull_redirects(url):
    """
    Get the window.location value from the page.

    This function will return the url that the page redirects to.

    :param url: The url to get the redirect from
    :return: The redirect url
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    script = soup.find('script', string=lambda s: s and 'window.location' in s)
    if script:
        # Use precompiled regex to extract the URL from window.location assignment
        match = WINDOW_LOCATION_REGEX.search(script.string)
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

    # get the blogspot user's blog links
    links = get_blogspot_links(profile_url)
    # set to store unique links
    unique_links = set()
    for link in links:
        redirect_link = pull_redirects(link)
        # print the initial link and redirecting link
        print(f"{link} -> {redirect_link}")
        # add the redirecting link to the set (if it exists)
        if redirect_link:
            unique_links.add(redirect_link)
        # sleep for the configured seconds between requests
        sleep(sleep_seconds)
    # print the unique redirecting links
    print("\nUnique Redirecting Links:")
    for link in unique_links:
        print(link)