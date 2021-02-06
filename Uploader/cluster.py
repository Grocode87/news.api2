from gensim.models.doc2vec import Doc2Vec
import scipy
import numpy as np
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity

import math
import datetime
import pickle

class TFidfModel():
    def __init__(self):
        self.vectorizer = pickle.load(open("cluster/tfidf/tfidf-140.p", "rb"))
        self.svd = pickle.load(open("cluster/tfidf/svd-140.p", "rb"))
    def infer_vector(self, text):
        vectors = self.vectorizer.transform([text])
        vectors = self.svd.transform(vectors)

        return vectors
    def infer_vectors(self, texts):
        vectors = self.vectorizer.transform(texts)
        vectors = self.svd.transform(vectors)

        return vectors

class D2VModel():
    def __init__(self):
        self.model = Doc2Vec.load("cluster/d2v_3.model")
    def infer_vector(self, text):
        self.model.infer_vector(text)

class ClusterHandler():
    """
    Handler of clustering functions
    """
    CLUSTER_THRESHOLD = 0.55

    def __init__(self, model):
        self.model = model
    
    def process_text(self, text):
        """
        Preprocess text for model, tokenize and lowercase
        """
        return text.lower()

    def infer_vector(self, text):
        """
        Get vector for text from model
        """
        return self.model.infer_vector(self.process_text(text))[0]

    def infer_vectors(self, texts):
        """
        Get vector for text from model
        """
        return self.model.infer_vectors(texts)

    def calculate_time_decay(self, d1, d2, max_decay=0.2):
        """
        Calculate time decay based on absolute distance between d1 and d2

        Exponential or [linear]
        """
        t_distance = abs((d2 - d1).days)
        decay = 1
        if t_distance < 14:
            #decay = .3 * (1.5**(t_distance-7)) # Somewhat exponential - very low on the first few days
            decay = .35 * (1/7) * t_distance # linear - 7 days = .35
    
        return decay
        

    def calculate_similarity(self, v1, v2, d1=None, d2=None):
        """
        Calculate similarit(ies) between two vector lists

        Need to get article representation for each vector
        """
        sims = cosine_similarity(v1, v2)
        if d1 and d2:
            for sim1_index in range(len(sims)):
                for sim2_index in range(len(sims[sim1_index])):
                    time_decay = self.calculate_time_decay(d1[sim1_index], d2[sim2_index])
                    sims[sim1_index][sim2_index] -= time_decay
        
        return sims

class ClusterObj:
    """
    Represents cluster vertices and centroid for clustering
    """

    def __init__(self, db_id, cluster_handler, articles=[], last_updated_date=None, date_created=None):
        self.db_id = db_id
        self.article_vectors = []
        self.centroid = None
        self.last_updated_date = last_updated_date
        self.date_created = date_created
        
        self.cluster_handler = cluster_handler

        if articles:
            for article in articles:
                self.add_article(article.cleaned_content)
            self.calculate_centroid()


    def add_article(self, article_text, calculate_centroid=False):
        self.article_vectors.append(self.cluster_handler.infer_vector(article_text))

        if calculate_centroid:
            self.calculate_centroid()

    def add_vector(self, article_vector, calculate_centroid=False):
        self.article_vectors.append(article_vector)

        if calculate_centroid:
            self.calculate_centroid()

    def calculate_centroid(self):
        """
        Calculate average of article vectors
        """
        self.centroid = np.average(self.article_vectors, axis=0)
        

    def calculate_similarity(self, text):
        """
        calculate text similarity to cluster centroid

        """
        if self.centroid.any() == None:
            print("ERROR: centroid calculation not done")
            return None
        text_vector = self.cluster_handler.infer_vector(text)
        sim = self.cluster_handler.calculate_similarity(text_vector, self.centroid)

        return sim
        

"""

 # cluster stories
        # CLUSTER
        
        class ClusterRep():
            def __init__(self, db_id):
                self.db_id = db_id
                self.article_vectors = []
                self.centroid = None
                self.text_range = ()
                    
            def compute_centroid(self):
                self.centroid = np.mean(np.array(self.article_vectors), axis=0)
            
            def add_article_vector(self, vector, compute_centroid=False):
                self.article_vectors.append(vector)
                
                if compute_centroid:
                    self.compute_centroid()

            def add_article_vectors(self, vectors):
                for v in vectors:
                    self.add_article_vector(v)
                
        new_articles = [a for a in new_articles if a]
        
# NEED
        # new article - all data
        texts = []
        cluster_objects = []
        
        # add all new article texts to texts list that will be vectorized
        self.timer.start("get new article texts")
        for article in new_articles:
            texts.append(article.text)
        self.timer.end()
        
        # loop through all existing clusters
        # create representation of clusters locally
        self.timer.start("building existing clusters representation")
        clusters = self.session.query(Cluster).all()
        for i, cluster in enumerate(clusters):
            rep = ClusterRep(cluster.id)
            
            for article in cluster.articles:
                texts.append(article.content)
            rep.text_range = (len(texts)-len(cluster.articles), len(texts))
            cluster_objects.append(rep)
        self.timer.end()
        
        # calculate tf-idf for each text
        self.timer.start("calculate text vectors")
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(texts)
        self.timer.end()

        # using calculated vectors, calculate centroid for each cluster vector
        self.timer.start("Calculate cluster centroids")
        centroids = []
        for i, cluster in enumerate(cluster_objects):
            text_range = cluster.text_range
            article_vectors = vectors[text_range[0], text_range[1]]
            article_vectors = [a.toarray() for a in article_vectors]
            cluster.add_article_vectors(article_vectors)
            cluster.compute_centroid()
            
            centroids.append(cluster.centroid)
        self.timer.end()
        
        self.timer.start("Looping through new articles and clustering")
        # loop through new article vectors
        print(len(new_articles))
        for i, article in enumerate(new_articles):
            article_vector = vectors[i].toarray()
            matching_cluster = False
            if len(centroids) > 0:
                similarities = []
                for i, c in enumerate(centroids):
                    similarities.append((i, cosine_similarity(article_vector, c)))
                
                top_sim_index = max(similarities, key=itemgetter(1))[0]
                print(similarities[top_sim_index][1])
                if similarities[top_sim_index][1] > 0.5:
                    matching_cluster = True
                    
            if matching_cluster:
                cluster_obj = cluster_objects[top_sim_index]

                self.session.query(Cluster).get(cluster_obj.db_id).last_updated = datetime.datetime.now()
                self.session.add(ClusterArticle(cluster_id=cluster_obj.db_id, article_id=article.db_id))
                
                cluster_obj.add_article_vector(article_vector, compute_centroid=True)
                centroids.append(cluster_obj.centroid)
                cluster_objects.append(cluster_obj)
            else:
                # No clusters found
                # create new cluster and calculate centroid\
                new_cluster = Cluster(last_updated=datetime.datetime.now())
                self.session.add(new_cluster)
                self.session.flush()
                self.session.add(ClusterArticle(cluster_id=new_cluster.id, article_id=article.db_id))

                cluster_obj = ClusterRep(new_cluster.id)
                cluster_obj.add_article_vector(article_vector, compute_centroid=True)
                centroids.append(cluster_obj.centroid)
                cluster_objects.append(cluster_obj)
        self.timer.end()
        
        
        self.session.commit()
"""