from sqlalchemy.sql.base import Executable
from article import Article
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import LabelEncoder

import pandas as pd

import multiprocessing
import newspaper
import requests
import pickle
import string
import langdetect

# article scraping batch size
BATCH_SIZE = 100

# interval between progress logs for article scraping
LOGGING_INTERVALS = 1

class ArticleScraper():
    def __init__(self):
        #news = pd.read_csv("classifier/training_dataset.csv", names=['id', 'text', 'category'])

        # load the label encoder to decode category numbers
        #self.encoder = LabelEncoder()
        #self.encoder.fit_transform(news['category'])

        # load the text classifer
        #self.text_clf = open("classifier/nb_classifier.pkl", "rb")
        #self.text_clf = pickle.load(self.text_clf)

        self.porter = PorterStemmer()

        # prevents odd nltk error
        # https://stackoverflow.com/questions/27433370/what-would-cause-wordnetcorpusreader-to-have-no-attribute-lazycorpusloader
        wn.ensure_loaded()
        
    
    def pool_articles(self, articles):
        """
        pooled batch processing with accurate progress logging
        """

        print("starting article pooling")
        processed_articles = []

        pool = multiprocessing.Pool(processes=10)
        print("created pool")

        step = 0
        next_logged_percent = LOGGING_INTERVALS

        while (step * BATCH_SIZE) <= len(articles):
            print("starting batch")
            # Get list of articles for batch
            batch_articles = articles[step * BATCH_SIZE : (step * BATCH_SIZE) + BATCH_SIZE]

            for a in batch_articles:
                if not a:
                    print("ERROR: " + a)
            # pool the article processing
            #processed_batch = [self.process_article(articles[0])]
            processed_batch = pool.map(self.process_article, batch_articles)
            processed_articles.extend(processed_batch)

            # calculate the current process
            progress = ((step * BATCH_SIZE) + len(batch_articles)) / len(articles) * 100

            step += 1

            # determine whether to print log info and calculate log percent
            new_log = False
            while progress >= next_logged_percent:
                next_logged_percent += LOGGING_INTERVALS
                new_log = True

            # print log info if LOGGING INTERVAL is passed
            if new_log:
                print("BATCH #" + str(step - 1) + " Complete  (" + str(((step - 1) * BATCH_SIZE) + len(batch_articles)) + "/" + str(len(articles)) + ")")
                print(next_logged_percent - LOGGING_INTERVALS, "% Done")
        
        return processed_articles
    
    def process_article(self, article):
        """Scrape data from news article from url

        Args:
            article ([ArticleObj]): [Article Object to scrape - article.url must not be null]

        Returns:
            [ArticleObj]
        """
        
        print("processing article: " + str(article.title) + " - " + str(article.source))
        
        try:
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
            config = newspaper.Config()
            config.browser_user_agent = user_agent
            
            newspaper_article = newspaper.Article(article.url, language='en', config=config)
            newspaper_article.download()
            newspaper_article.parse()
        except Exception as e:
            # handle any exceptions
            print("Error parsing newspaper article")
            print(e)

        if newspaper_article:
            article.text = self.get_text(newspaper_article).encode('utf-8').decode("utf-8")
            #lang = langdetect.detect(article.text)
            lang = 'en'
            if lang == 'en':
                article.cleaned_text = self.clean_text(article.text)

                if len(article.text.split()) > 60 and article.title != None:
                    #article.entities = self.get_entities(article.text)
                    article.entities = []
                    #article.category = self.get_category(article.cleaned_text)
                    article.category = ""
                    if not article.img_url:
                        article.img_url = self.get_image_url(newspaper_article)
                    
                    article.desc = ' '.join(article.text.split()[:50]) + "..."
                    return article
                    
        
    
    def clean_text(self, text):
        """
        Remove stopwords from, tokenize, and stem the text
        """
        stop = stopwords.words('english') + list(string.punctuation)
        words = word_tokenize(text.lower())
        #words = [w for w in words if not w in stop]
        words = [self.porter.stem(w) for w in words if not w in stop]

        return ' '.join(words)

    def get_text(self, newspaper_article):
        """
        Scrape the article from the url and return the text
        """
        try:
            content = str.join(" ", newspaper_article.text.splitlines())
        except:
            # handle any exceptions
            print("Error occured when getting text")
            content = ""

        return content

    def get_entities(self, text):
        """
        Use wikifier.org to the get the entities from text
        """
        entities = {}
        try:
            data = {
                "userKey": "jzanfsvrolfwraokwpxhxiatovhvyp",
                "text": text, "lang": 'en',
                "pageRankSqThreshold": "%g" % 0.9, "applyPageRankSqThreshold": "true",
                "nTopDfValuesToIgnore": "200",
                "wikiDataClasses": "true", "wikiDataClassIds": "false",
                "support": "true", "ranges": "false",
                "includeCosines": "false", "maxMentionEntropy": "2.1"
            }
            url = "http://www.wikifier.org/annotate-article"

            req = requests.post(url, data=data)
            response = req.json()

            for annotation in response['annotations']:
                entities[annotation['title']] = annotation['pageRank']
        except:
            # handle any exceptions
            print("Error occured when getting entities")
            entities = {}

        return entities

    def get_category(self, text):
        """
        Use the text classifier to get the category of the text
        """
        prediction = self.text_clf.predict([text])
        predicted_category = self.encoder.inverse_transform(prediction)
        
        return predicted_category[0]

    def get_image_url(self, newspaper_article):
        """
        Scrape the images from the url
        """

        return newspaper_article.top_image

            
