"""
Representation of an article to be scraped and added to the database
"""

from modals import Article as ArticleModel
from modals import Entity as EntityModel
import datetime

class Article():
    def __init__(self, title="", desc="", source="", text="", url="", img_url="", pubDate=None):
        self.db_id = -1
        self.title = self.fallback_value(title, "")
        self.desc = self.fallback_value(desc, "")
        self.source = self.fallback_value(source, "")
        self.text = self.fallback_value(text, "")
        self.cleaned_text = ""
        self.url = self.fallback_value(url, "")
        self.img_url = self.fallback_value(img_url, "")
        self.entities = []
        self.category = ""
        self.pubDate = self.fallback_value(pubDate, datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return str({
            'title': self.title,
            'desc': self.desc,
            'source': self.source,
            'text': self.text,
            'url': self.url,
            'img_url': self.img_url,
            'category': self.category
        })

    def get_db_instance(self):
        """
        Return a DB Model of the article
        """
        return ArticleModel(
            title = self.title,
            description = self.desc,
            source = self.source,
            content = self.text,
            cleaned_content = self.cleaned_text,
            url = self.url,
            image_url = self.img_url,
            category = self.category,
            date_created = self.pubDate
        )

    def fallback_value(self, value, fallback):
        if value is None:
            return fallback
        return value
