"""
News article retrieval and basic article scraping
"""
from article import Article
import json

TEMP_ARTICLES_INDEX = 5

class ArticleFinder():
    def __init__(self):
        self._retrieval_url = "https://newsapi.org/v2/everything?language={0}&pageSize={1}&apiKey={2}&sources=".format( # pylint: disable=line-too-long
            "en", '100', '65cf3ce545bf41b0a3c5e2811cb7a04f')

    def get_articles_temp(self):
        """
        Quick way to get list of articles for testing, returns articles from text file
        """
        file_path = "temp_data/articles/articles-{0}.json".format(TEMP_ARTICLES_INDEX)
        with open(file_path, 'r') as f:
            articles = []
            for article in json.load(f):
                articles.append(Article(title=article['title'],
                                        desc=article['description'],
                                        source=article['source']['name'],
                                        text=article['content'],
                                        url=article['url'],
                                        img_url=article['urlToImage']))
        return articles
    def get_articles():
        """
        Scrape the internet for articles and return them
        """
        pass


