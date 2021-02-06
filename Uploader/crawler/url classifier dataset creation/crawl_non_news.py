import multiprocessing
import time
import requests
from urllib.request import urlparse, urljoin
import re
import random
import tldextract
import os
import langdetect

from bs4 import BeautifulSoup

MAX_URLS_PER_SITE = 20
SITES_PER_SOURCE = 50
SOURCES_PER_SOURCE = 5
SITES_PER_FILE = 2000


def is_source_valid(old_source, source):
    # validate source url existance
    if not source or not old_source:
        return False

    if source == old_source:
        return False
    # validate source url extension
    parsed_source = tldextract.extract(source)
    #parsed_old_source = tldextract.extract(old_source)

    # if parsed_source.domain == parsed_old_source.domain:
    #    return False

    accepted_suffi = ["com", "ca", 'org']
    if not parsed_source.suffix in accepted_suffi:
        return False

    r = requests.get(source)

    # ensure page source is english
    soup = BeautifulSoup(r.content, features="html.parser")
    text = ' '.join(soup.find_all(text=True))
    lang = langdetect.detect(text)
    print(lang)
    if not lang == 'en':
        return False

    # ensure acceptance number of urls in source
    links = []

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if (not href == "") and (not href is None):
            links.append(href)

    if len(links) < 20:
        return False

    return True


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def crawler(in_queue, out_queue, result_queue, sources_queue):
    while True:
        if result_queue.qsize() < SITES_PER_SOURCE:
            # get new url to scrape
            url = in_queue.get()
            print(url)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, features="html.parser")

            text = soup.find_all(text=True)
            output = ''
            blacklist = [
                '[document]',
                'noscript',
                'header',
                'html',
                'meta',
                'head',
                'input',
                'script',
                'style'
                # there may be more elements you don't want, such as "style", etc.
            ]

            for t in text:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)

            result_queue.put(output)

            urls = []
            domain_name = urlparse(url).netloc

            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    # href empty tag
                    continue
                # join the URL if it's relative (not absolute link)
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                # remove URL GET parameters, URL fragments, etc.
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                site_url = parsed_href.scheme + "://" + parsed_href.netloc
                if not is_valid(href):
                    # not a valid URL
                    continue
                if domain_name not in href:
                    sources_queue.put(site_url)
                    continue
                else:
                    if not href in urls:
                        urls.append(href)

            if len(urls) > MAX_URLS_PER_SITE:
                urls = random.sample(urls, MAX_URLS_PER_SITE)

            for u in urls:
                out_queue.put(u)


def handler(in_queue, out_queue, result_queue, sources_queue):
    """
    Controls the crawlers
    - gives crawlers new urls to crawl
    - ensures urls are not crawled twice
    - switches sources after enough urls are crawled from source
    """
    # get current file
    file_index = len(os.listdir('site_data')) - 1

    lines_in_file = 0

    if file_index >= 0:
        with open(f"site_data/{file_index}.txt", encoding='utf-8') as f:
            lines_in_file = sum(1 for line in f)

    if file_index < 0:
        file_index = 0

    sources_cache = []
    crawled_sources = set()
    source_url = "https://ca.indeed.com/"

    while(True):
        print(f"Scraping urls from {source_url}")
        in_queue.put(source_url)

        # Keep crawlers going until sites goal reached
        # take url from out queue, make sure it is not already scraped, add to in queue
        crawled_urls = set()
        while result_queue.qsize() < SITES_PER_SOURCE:
            new_url = out_queue.get()
            if result_queue.qsize() % 10 == 0:
                print(result_queue.qsize())

            if not new_url in crawled_urls:
                crawled_urls.add(new_url)
                in_queue.put(new_url)

        # empty the in queue to stop crawlers
        while not in_queue.empty():
            in_queue.get()

        # add source to memory so it does not get crawled again
        crawled_sources.add(source_url)

        # get every site scraped by crawlers
        # add site content to text file
        # limit file size to 2000 lines
        source_sites = []
        while not result_queue.empty():
            result = str(result_queue.get())
            result = ' '.join(w.strip() for w in result.split())
            source_sites.append(result)

            if lines_in_file > SITES_PER_FILE:
                file_index += 1
                lines_in_file = 0
            with open(f"site_data/{file_index}.txt", 'a', encoding='utf-8') as f:
                f.write(f"{result}\n")
                lines_in_file += 1

        # empty sources queue
        new_sources = []
        while not sources_queue.empty():
            s = sources_queue.get()

            if not s in new_sources:
                if not s in crawled_sources:
                    new_sources.append(s)

        # pick up to 10 new sources and add them to the cache
        sources_found = 0
        while sources_found < SOURCES_PER_SOURCE and len(new_sources) > 0:
            s = random.choice(new_sources)
            if (not s in crawled_sources) and (not s in sources_cache):
                if is_source_valid(source_url, s):
                    sources_found += 1
                    sources_cache.append(s)
                    print("found source")
            new_sources.remove(s)

        print(f"\n\n{len(source_sites)} urls scraped from {source_url}")
        print(f"length of sources cache: {len(sources_cache)}")
        print(f"number of sites scraped: {len(crawled_sources)}")

        # pick random new source to crawl
        source_url = random.choice(sources_cache)
        sources_cache.remove(source_url)

        # ensure the crawler output queue is empty
        while not out_queue.empty():
            out_queue.get()
        print(in_queue.qsize())
        print(out_queue.qsize())


if __name__ == '__main__':
    in_queue = multiprocessing.Queue()  # Crawler input urls
    out_queue = multiprocessing.Queue()  # Crawler output urls
    result_queue = multiprocessing.Queue()  # Scraped sites from crawler
    source_queue = multiprocessing.Queue()  # Possible crawl urls

    crawl_manager = multiprocessing.Process(target=handler, args=(
        in_queue, out_queue, result_queue, source_queue))
    crawlers = []

    for i in range(5):
        #crawlers.append(Crawler("process-" + str(i), url_queue, url_cache, test_source['name']))
        crawlers.append(multiprocessing.Process(target=crawler, args=(
            in_queue, out_queue, result_queue, source_queue)))

    crawl_manager.start()
    for c in crawlers:
        c.start()

    crawl_manager.join()
    for c in crawlers:
        c.join()
