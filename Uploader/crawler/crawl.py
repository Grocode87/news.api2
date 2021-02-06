import multiprocessing
import time
import fasttext
import langdetect
import requests
import datetime
from urllib.request import urlparse, urljoin
from dateutil import parser
import re
import sys
import os
import html
import pytz

from bs4 import BeautifulSoup, CData
#sys.path.append(os.path.abspath('../'))
from article import Article

class ArticleCrawler():
    """handler for article crawler"""
    def __init__(self):
        article = Article()

    def get_articles(self):
        """
        start searching through sitemaps, return articles
        """
        with open('crawler/sitemap-data/sitemaps-base.txt', "r") as f:
            sitemaps = f.readlines()[:10]
            articles = []
            for i, s in enumerate(sitemaps):
                new_articles = self.read_sitemap(s.strip())
                articles.extend(new_articles)
                print("scraped source #" + str(i))
                print("total articles = " + str(len(articles)))
            return articles

    def parse_cdata(self, text):
        if "CDATA" in text:
            text = html.unescape(text.replace("<![CDATA[", "").replace("]]>", ""))
        return text
                
                
    def read_sitemap(self, sitemap):
        articles_found = []
        r = requests.get(sitemap)
        xml = r.content

        soup = BeautifulSoup(xml, 'xml')
        if soup.find("urlset"):
            articles = soup.findAll("url")
            langCheck = False
            for a in articles[:100]:
                url = a.loc.string
                
                if a.find("news:news"):
                    pubName = self.parse_cdata(a.find("news:name").text)
                    pubDate = self.parse_cdata(a.find("news:publication_date").text)
                    lang = self.parse_cdata(a.find("news:language").text)
                    title = self.parse_cdata(a.find("news:title").text)

                    if pubName and lang and title:
                        if not langCheck:
                            lang = 'en'
                            langCheck = True
                            if not lang == 'en':
                                continue
                        if pubDate:
                            pubDate = parser.parse(pubDate)
                            
                            if not pubDate.tzinfo:
                                pubDate = pytz.timezone("UTC").localize(pubDate)
                            else:
                                pubDate = pubDate.astimezone(pytz.timezone('UTC'))
                    
                        article = Article(title=title.strip(), source=pubName.strip(), url=url.strip(), pubDate=pubDate)
                        articles_found.append(article)
                            
        return articles_found
                

if __name__ == '__main__':
    a = ArticleCrawler()
    a.get_articles()
