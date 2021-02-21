"""
    Map retrieval and uploading with multiprocessing pools and SQLalchemy
"""
import datetime
import multiprocessing
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter

from scrape import ArticleScraper
from cluster import ClusterObj, ClusterHandler, TFidfModel
from crawler.crawl import ArticleCrawler
from dbmaintenance import DBMaintanance

from timer import Timer
import time

from modals import Base, Article, Entity, ArticleEntity, EntityFrequency, Cluster, ClusterArticle
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

class Uploader():
    def __init__(self):
        db_url = "mysql://root:Hunter1?23@localhost/newsapp?charset=utf8mb4"

        engine = create_engine(db_url, echo=False)

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        self.article_scraper = ArticleScraper()
        self.article_crawler = ArticleCrawler()
        self.db_maintain = DBMaintanance()
        
        self.timer = Timer()
        
    def run(self):
        self.timer.start("Article Retrieval")
        print("getting articles...")
        articles = self.article_crawler.get_articles()
        print("article retrival done, returned {} articles\n".format(len(articles)))
        self.timer.end()

        # remove articles that already exist
        
        self.timer.start("Article filtering")
        print("filtering out existing articles...")
        new_articles = []
        for a in articles:
            matching_articles = self.session.query(Article.id).filter(Article.title == a.title).all()
            if len(matching_articles) == 0:
                new_articles.append(a)
        print("articles filtered, {} remaining articles\n".format(len(new_articles)))
        self.timer.end()
        
        
        # process articles using pools
        # SCRAPE
        self.timer.start("Article Scraping")
        new_articles = self.article_scraper.pool_articles(new_articles)
        self.timer.end()
        
        # UPLOAD
        
        self.timer.start("Article Upload")
        print("uploading articles...")
        for article in new_articles:
            if article:
                article_db_instance = article.get_db_instance()
                self.session.add(article_db_instance)
                self.session.flush()
                article.db_id = article_db_instance.id

                # check if entity already exists, if it does add to total occurencues
                # if not create new entity
                for entity in article.entities:
                    entity_name = entity.encode('utf-8')
                    entity_score = article.entities[entity]

                    matching_entity = self.session.query(Entity).filter(Entity.name == entity_name).all()
                    if len(matching_entity) > 0:
                        db_entity = matching_entity[0]
                        db_entity.total_occurences += 1
                    else:
                        db_entity = Entity(name=entity_name)
                        self.session.add(db_entity)
                        self.session.flush()

                    self.session.add(ArticleEntity(article_id=article.db_id,
                                            entity_id=db_entity.id, score=entity_score))
                    self.session.add(EntityFrequency(entity_id=db_entity.id, date_added=datetime.datetime.utcnow()))
                    self.session.flush()

        self.session.commit()
        self.timer.end()
       
        
        self.timer.start("Article Clustering")
        print("clustering...")

        current_time_utc = datetime.datetime.now(datetime.timezone.utc)

        tfidfModel = TFidfModel()
        cluster_handler = ClusterHandler(tfidfModel)

        clusters = self.session.query(Cluster).all()
        cluster_objects = []

        # build local representation of existing clusters
        # TODO: Only store centroid vector for existing articles to minimize memory usage
        # NOTE: May need to implement local db and batching once db size is too large

        if len(clusters) > 0:
            # vectorize all existing article texts in advance for speed advantage
            print("building existing clusters")
            all_article_texts = []
            for c in clusters:
                all_article_texts.extend([a.cleaned_content for a in c.articles])
                
            all_article_vectors = cluster_handler.infer_vectors(all_article_texts)
                
            # build cluster representation and calculate centroids
            article_index = 0
            for cluster_i, cluster in enumerate(clusters):
                cluster_obj = ClusterObj(cluster.id, cluster_handler, last_updated_date=cluster.last_updated, date_created=cluster.date_created)
                
                
                for vector in all_article_vectors[article_index:article_index+len(cluster.articles)]:
                    cluster_obj.add_vector(vector)
                cluster_obj.calculate_centroid()
                article_index += len(cluster.articles)

                cluster_objects.append(cluster_obj)
        else:
            print("No existing clusters")

        new_articles = [a for a in new_articles if a]

        # compute vectors for new articles in advance for performance optimization
        article_vectors = cluster_handler.infer_vectors([a.cleaned_text for a in new_articles])
        
        print("clustering new articles")
        # loop through all new articles
        for article_index, article in enumerate(new_articles):
            if article:
                cluster_vectors = [c.centroid for c in cluster_objects]
                cluster_dates = [c.date_created for c in cluster_objects]

                article_vector = article_vectors[article_index]

                # calcute article similarities to clusters
                similarities = []
                if len(cluster_vectors) > 0:
                    
                    similarities = cluster_handler.calculate_similarity(cluster_vectors, [article_vector], cluster_dates, [article.pubDate])
                    similarities = [(i, sim[0]) for i, sim in enumerate(similarities)]
                    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

                if len(similarities) > 0 and similarities[0][1] > 0.57:
                    print("found matching article with similarity: " + str(similarities[0][1]))
                    cluster = cluster_objects[similarities[0][0]]
                    print(f"existing cluster id: {cluster.db_id}")
                    print(f"article id: {article.db_id}")
                    self.session.query(Cluster).get(cluster.db_id).last_updated = current_time_utc
                    self.session.add(ClusterArticle(cluster_id=cluster.db_id, article_id=article.db_id))
                    cluster.add_vector(article_vector, calculate_centroid=True)
                else:
                    print("new cluster")
                    new_cluster = Cluster(last_updated=current_time_utc, date_created=article.pubDate)
                    self.session.add(new_cluster)
                    self.session.flush()
                    self.session.add(ClusterArticle(cluster_id=new_cluster.id, article_id=article.db_id))

                    cluster_obj = ClusterObj(new_cluster.id, cluster_handler, last_updated_date=current_time_utc, date_created=article.pubDate)
                    cluster_obj.add_vector(article_vector, calculate_centroid=True)
                    cluster_objects.append(cluster_obj)


        print("clustering finished")
        self.timer.end()
        
        self.session.commit()
        
        
        self.timer.start("DB Maintain")
        print("Performing DB Maintanance Tasks")
        self.db_maintain.run_tasks(self.session)
        self.timer.end()

if __name__ == '__main__':    
    uploader = Uploader()
    uploader.run()
