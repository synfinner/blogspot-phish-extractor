#!/usr/bin/env python3

'''Python script to extract blog links from a blogspot profile.'''

import requests
from bs4 import BeautifulSoup
import sys
from time import sleep

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
        # Extract the string after window.location
        script_str = script.string.split('window.location')[1].split(';')[0].strip()
        # clean the string so it is only the url
        script_str = script_str.replace('=',' ').replace('"',' ').strip()
        return script_str
    return None

if __name__ == '__main__':
    # get the blogspot profile url from user via arg 
    profile_url = sys.argv[1]
    # get the blogspot user's blog links
    links = get_blogspot_links(profile_url)
    # set to store unique links
    unique_links = set()
    for link in links:
        # print the initial link and redirecting link
        print(f"{link} -> {pull_redirects(link)}")
        # add the redirecting link to the set
        unique_links.add(pull_redirects(link))
        # sleep for 1.25 seconds between requests
        sleep(1.25)
    # print the unique redirecting links
    print("\nUnique Redirecting Links:")
    for link in unique_links:
        print(link)
    
    