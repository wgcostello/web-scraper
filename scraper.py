import os
import re
import requests
import string
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def create_parse_tree(response):
    return BeautifulSoup(response.content, 'html.parser')


def navigate_pages(url, page_num):
    r = requests.get(url, params={'page': page_num})
    return r.url


def url_to_soup(url, headers):
    response = requests.get(url, headers=headers)
    response_status_code = response.status_code
    if response_status_code == 200:
        return create_parse_tree(response)
    else:
        print(f'The URL returned {response_status_code}!')
        quit()


def article_urls(articles, article_type, hostname):
    article_urls_list = []
    for article in articles:
        if article.find('span', {'data-test': 'article.type'}).span.text == article_type:
            article_urls_list.append(hostname +
                                          article.find('a', {'data-track-action': 'view article'}).get('href'))
    return article_urls_list


def save_content(content, filename):
    with open(filename, 'wb') as file:
        file.write(content)


if __name__ == '__main__':
    page_url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"
    hostname = f'{urlparse(page_url).scheme}://{urlparse(page_url).hostname}'
    english_headers = {'Accept-Language': 'en-US,en;q=0.5'}

    number_of_pages = int(input())
    type_of_articles = input()

    for i in range(1, number_of_pages + 1):
        os.mkdir(f'Page_{i}')

        soup = url_to_soup(navigate_pages(page_url, i), english_headers)
        articles = soup.find_all('article')

        for article_url in article_urls(articles, type_of_articles, hostname):
            article_soup = url_to_soup(article_url, english_headers)
            body = bytes(article_soup.find('div', {'class': re.compile('body')}).text.rstrip(), encoding='utf-8')
            title = article_soup.title.text.rstrip().replace(' ', '_').strip(string.punctuation)
            save_content(body, f'Page_{i}/{title}.txt')
            print(f'Article saved in {title}.txt.')
