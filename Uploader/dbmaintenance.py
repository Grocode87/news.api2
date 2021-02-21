import datetime
import time
from modals import Cluster as ClusterModel
from modals import EntityFrequency, ClusterArticle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DBMaintanance():
    def __init__(self):
        pass
    
    def run_tasks(self, session):
        self.run_cluster_calculations(session)
        self.maintain_entity_freqs(session)
        self.calculate_top_cluster(session)
    

    def run_cluster_calculations(self, session):
        """
        Calculate rank and overall category of each cluster
        """
        # Select every cluster that was updated in the last 24 hours
        all_clusters = session.query(ClusterModel).filter(
            ClusterModel.last_updated > (datetime.datetime.now() - datetime.timedelta(hours=24))).all()

        for cluster in all_clusters:
            articles = cluster.articles

            # find the top category
            all_categories = [a.category for a in articles]
            top_category = max(set(all_categories), key=all_categories.count)

            # calculate rank based on when the cluster's articles where posted
            curr_date = datetime.datetime.now()
            rank = 0
            for article in articles:
                rank += 1
                last_date = article.date_created
                time_between = curr_date - last_date
                hours_between = (time_between.days * 24) + \
                    (time_between.seconds / 3600)
                rank -= (hours_between / 24)
                if rank < 0:
                    rank = 0

            # update the cluster's database entry
            cluster.category = top_category.strip()
            cluster.rank = rank
            
        session.commit()


    def maintain_entity_freqs(self, session):
        """
        Remove entity frequency entries older than 30 days
        """
        freqs = session.query(EntityFrequency).filter(
            EntityFrequency.date_added < (datetime.datetime.now() - datetime.timedelta(days=30))).all()
        for f in freqs:
            f.delete()

        session.commit()

    def calculate_top_cluster(self, session):
        """
        Use combination of time, title length, and title information to determine top article
        for each story cluster, and rank the stories in cluster
        """
        clusters = session.query(ClusterModel).all()

        for cluster in clusters:
            articles = cluster.articles
            article_titles = [a.title for a in articles]
            
            # count vectorize article texts for average sim calculation
            vectorizer = CountVectorizer()
            article_vectors = vectorizer.fit_transform(article_titles)
            
            # calculate max and min word counts for normalization
            word_counts = [len(t) for t in article_titles]
            max_word_count = max(word_counts)
            min_word_count = min(word_counts)

            # calculate max and min article ages for normalization
            articles_ages = [(cluster.last_updated - a.date_created).total_seconds() / 3600 for a in articles]
            max_article_age = max(articles_ages)
            min_article_age = min(articles_ages)

            article_scores = []

            for i, article in enumerate(articles):
                score = 0

                if len(articles) > 2:
                    # calculate normalized article age
                    article_age = (articles_ages[i] - min_article_age) / (max_article_age - min_article_age)
                    
                    #calculate avg article similarity to all other articles
                    sims = cosine_similarity(article_vectors[i], article_vectors)[0]
                    avg_sim = sum(sims) / len(sims)

                    # calculate normalized word count
                    word_count = (word_counts[i] - min_word_count) / (max_word_count - min_word_count)
                    
                    # calculate cumulative score
                    # .5 word count weight
                    # 1 average sim weight
                    # 1 article age weight
                    score = ((1 - word_count) * .5) + avg_sim + (1 - article_age)
                
                article_scores.append((article.id, score))
                
                # update each article in cluster with rank
                cluster_article = session.query(ClusterArticle).filter(ClusterArticle.cluster_id==cluster.id, ClusterArticle.article_id==article.id).all()[0]
                cluster_article.rank = score

            # get top score, set as top article in cluster
            article_scores.sort(key=lambda x: x[1], reverse=True)
            top_article_id = article_scores[0][0]
            cluster.top_article_id = top_article_id

        session.commit()