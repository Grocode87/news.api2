"""
Crawl the internet for sites with news sitemaps
"""
# news-sitemap.xml
# google-news.xml
# news-sitemap/
# news-sitemap.xml
# googlenews.xml
# new-sitemap-(topic).xml
# sitemap-news.xml
# sitemap-news
# sitemap_news.xml
# sitemaps/news.xml
# news.xml
# sitemap/news/index.xml (leads to https://www.businessinsider.com/sitemap/news/2020-09.xml)
# sitemaps/news/index.xml (leads to https://www.phonearena.com/sitemaps/news/2020/11/index.xml)
# feed/google-latest-news/sitemap-google-news
# sitemap_google_news.xml/
# FROM INDEX - sitemap-main-news.xml -- LEADS TO LIST OF NEWS SITEMAPS BY PAGES
# https://www.digitaltrends.com/sitemaps/news-sitemap/2020/11.xml
# sitemaps/google-news/1.xml
# mw_news_sitemap.xml
# google-news-sitemap.xml
# sitemaps/google_news
# feed/googlenews/articles.xml
# xml-sitemap/news.xml
# news-sitemap_index_US_en-US.xml.gz
# sitemaps/news-sitemap_googlenewsindex_US_en-US.xml.gz
# http: // news.bitauto.com/news_google_sitemap.xml
# https://hothardware.com/newsmap.ashx
# sitemaps/new/news.xml.gz
# sitemap-news-https.xml
# https://www.nydailynews.com/arcio/sitemap-index/ INSIDE ---- https://www.nydailynews.com/arcio/news-sitemap/
# latest-newssitemap.xml
# yoast-news-sitemap.xml
#https: // www.themanual.com/sitemaps/news-sitemap/index.xml


# new-sitemap-(topic).xml
# sitemap/news/index.xml (leads to https://www.businessinsider.com/sitemap/news/2020-09.xml)
# sitemaps/news/index.xml (leads to https://www.phonearena.com/sitemaps/news/2020/11/index.xml)
# FROM INDEX - sitemap-main-news.xml -- LEADS TO LIST OF NEWS SITEMAPS BY PAGES
# https://www.digitaltrends.com/sitemaps/news-sitemap/2020/11.xml
# news-sitemap_index_US_en-US.xml.gz
# sitemaps/news-sitemap_googlenewsindex_US_en-US.xml.gz
# http: // news.bitauto.com/news_google_sitemap.xml
# https://hothardware.com/newsmap.ashx
# sitemaps/new/news.xml.gz
# https://www.nydailynews.com/arcio/sitemap-index/ INSIDE ---- https://www.nydailynews.com/arcio/news-sitemap/
# latest-newssitemap.xml
#https: // www.themanual.com/sitemaps/news-sitemap/index.xml



# news-sitemap.xml
# news_sitemap.xml
# news_sitemap
#newssitemap.xml

# sitemap-news.xml
# sitemap_news.xml
# sitemap_news
# sitemap-news
# sitemapnews

# news.xml
# articles.xml

# google_news
# googlenews
# google-news
# google_news.xml
# googlenews.xml
# google-news.xml

# news_google_sitemap.xml
# sitemap-news-https.xml

# googlenews.xml
from usp.tree import sitemap_tree_for_homepage
import multiprocessing
import requests
import langdetect
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
from itertools import chain

# Create whitelist for detecting news sitmaps
# for each value, seperate by -,_, and nothing
# add a .xml varient to each
ending_whitelist = ["news sitemap", 'sitemap news',
                    "news", "articles", "google news"]

new_whitelist = []
for e in ending_whitelist:
    s = e.split()
    if len(s) > 1:
        new_whitelist.append("{}-{}".format(s[0], s[1]))
        new_whitelist.append("{}_{}".format(s[0], s[1]))
        new_whitelist.append("{}{}".format(s[0], s[1]))
    else:
        new_whitelist.append(e)
ending_whitelist = new_whitelist

ending_whitelist = list(
    chain(*([e, e+'.xml', e+'.xml/', e+"/"] for e in new_whitelist)))

# add other random endings
ending_whitelist.extend(["news_google_sitemap.xml", "sitemap-news-https.xml"])
print(ending_whitelist)

def get_site_text(soup):
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
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    return ' '.join(output.splitlines())

def get_external_urls(source):
    try:
        r = requests.get(source)
    except:
        return []
    
    soup = BeautifulSoup(r.content, features="html.parser")
    
    external_urls = []
    domain_name = urlparse(source).netloc
    
    #text = get_site_text(soup)
    lang = 'en'
    
    if lang == 'en':
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(source, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            site_url = parsed_href.scheme + "://" + parsed_href.netloc
            
            # Make sure new url is balid
            parsed = urlparse(href)
            is_valid = bool(parsed.netloc) and bool(parsed.scheme)
            if "mailto" in href:
                continue
            if not is_valid:
                # not a valid URL
                continue
            if domain_name not in href:
                external_urls.append(site_url)
                continue
    return external_urls


def find_feeds(site):
    """Search for rss feeds on site

    Args:
        site ([String]): [site url to scrape]

    Returns:
        [List]: [list of possible feeds]
    """
    raw = requests.get(site).text
    
    possible_feeds = []
    html = BeautifulSoup(raw, features='html.parser')
    feed_urls = html.findAll("link", rel="alternate")
    
    if len(feed_urls) > 1:
        for f in feed_urls:
            t = f.get("type", None)
            if t:
                if "rss" in t or "xml" in t:
                    href = f.get("href", None)
                    if href:
                        possible_feeds.append(href)
    parsed_url = urlparse(site)
    base = parsed_url.scheme+"://"+parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href", None)
        if href:
            if "xml" in href or "rss" in href or "feed" in href:
                possible_feeds.append(base+href)
    return possible_feeds
        
def find_robots_txt(url):
    """
    Given a base url, find the robots.txt file for website
    
    Returns None if no robots.txt file is found
    """
    try:
        r = requests.get(url + "/robots.txt")
        return r.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return None
    
def find_news_sitemaps(robots_content):
    """ Given a robots.txt url for a website, return the found news sitemaps

    Args:
        robots_url ([String]): [url to website robots.txt]
    """
    sitemaps = []
    for line in robots_content.splitlines():
        if line.startswith("Sitemap") and line.endswith(tuple(ending_whitelist)):
            sitemap_url = line.split("Sitemap:")[1].strip()

# news-sitemap.xml
# news_sitemap.xml
# news_sitemap
#newssitemap.xml

# sitemap-news.xml
# sitemap_news.xml
# sitemap_news
# sitemap-news
# sitemapnews

# news.xml
# articles.xml

# google_news
# googlenews
# google-news
# google_news.xml
# googlenews.xml
# google-news.xml

# news_google_sitemap.xml
            
        
            if "news" in sitemap_url:
                sitemaps.append(sitemap_url)
    return sitemaps
        

def crawler(in_queue, out_queue, sitemap_queue):
    sites_crawled = 0
    while True:
        sites_crawled += 1
        
        url = in_queue.get()
        
        for new_url in get_external_urls(url):
            out_queue.put(new_url)
        
        # processing for url
        robots_txt = find_robots_txt(url)
        if not robots_txt:
            continue
        
        sitemaps = find_news_sitemaps(robots_txt)
        for s in sitemaps:
            sitemap_queue.put(s)
            print("new sitemap found: " + s)
            
        #feeds = find_feeds(url)
        #for f in feeds:
        #    sitemap_queue.put(f)
        #    print("new feed found: " + f)
        
                
def crawler_manager(in_queue, out_queue, sitemap_queue):
    url_cache = set()
    sites_crawled = 0
    # in_queue - not yet processed urls
    # out_queue- new urls to process
    # sites-crawled = number of sites submitted to crawlers
    # out_queue
    while True:
        url = out_queue.get()
        sites_crawled += 1

        if not url in url_cache:
            in_queue.put(url)
            url_cache.add(url)
            
        while not sitemap_queue.empty():
            s = sitemap_queue.get()
            
            exists = False
            with open("sitemap-data/sitemaps-2.txt", 'r') as f:
                if s in f.read():
                   exists = True 
            if not exists:
                with open("sitemap-data/sitemaps-2.txt", 'a') as f:
                    f.write(s + "\n")

        print("sites crawled: " + str(sites_crawled - in_queue.qsize()) , end="\r")
        
if __name__ == '__main__':
    in_queue = multiprocessing.Queue()  # Possible crawl urls
    out_queue = multiprocessing.Queue()  # Possible crawl urls
    sitemap_queue = multiprocessing.Queue()  # Possible crawl urls
    
    in_queue.put("https://nytimes.com")
    
    crawl_manager = multiprocessing.Process(target=crawler_manager, args=(
        in_queue, out_queue, sitemap_queue))
    crawlers = []
    

    for i in range(15):
        crawlers.append(multiprocessing.Process(target=crawler, args=(in_queue, out_queue, sitemap_queue)))

    crawl_manager.start()
    for c in crawlers:
        c.start()

    crawl_manager.join()
    for c in crawlers:
        c.join()
