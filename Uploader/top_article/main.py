from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import Counter

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
sys.path.append('..')
from modals import Base, Article, Cluster

db_url = "mysql://root:Hunter1?23@localhost/newsapp?charset=utf8&use_unicode=0"

engine = create_engine(db_url, echo=False)

#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

stop_words = set(stopwords.words('english'))

clusters = session.query(Cluster).all()
for cluster in clusters:
    articles = cluster.articles
    article_titles = [a.title for a in articles]
    
    vectorizer = CountVectorizer()
    article_vectors = vectorizer.fit_transform(article_titles)
    
    word_counts = [len(t) for t in article_titles]
    max_word_count = max(word_counts)
    min_word_count = min(word_counts)

    articles_ages = [(cluster.last_updated - a.date_created).total_seconds() / 3600 for a in articles]
    max_article_age = max(articles_ages)
    min_article_age = min(articles_ages)

    if len(articles) > 2:
        for i, article in enumerate(articles):
            # calculate normalized article age
            article_age = (articles_ages[i] - min_article_age) / (max_article_age - min_article_age)
            print(1 - article_age)
            #print("Time Difference: " + str(time_difference))
            
            # get similarity between article and other articles
            
            sims = cosine_similarity(article_vectors[i], article_vectors)[0]
            avg_sim = sum(sims) / len(sims)
            #print("avg sim: " + str(avg_sim))

            # calculate normalized word count
            word_count = (word_counts[i] - min_word_count) / (max_word_count - min_word_count)
            #print("word count: " + str(word_count))
            
            score = ((1 - word_count) * .5) + avg_sim + (1 - article_age)

            print(f"{article.title}: {score}")
            # Kool - calculus, physics
            # SIDES - french
        print("\n")
    """
    articles = cluster.articles
    if len(articles) > 2:
        titles = []
        for a in articles:
            titles.append(a.title.decode('utf-8').lower())
            
        word_tokens = word_tokenize(' '.join(titles))

        filtered_words = [w for w in word_tokens if not w in stop_words and len(w)>2]

        c = Counter(filtered_words)
        ordered_words = c.most_common()
        
        for a in articles:
            title_text = a.title.decode('utf8').lower()
            score = 0
            for w, f in ordered_words:
                score += title_text.count(w) * (f - 1)
            score = score / (len(title_text.split()) / 2)
            print(str(a.title) + " - " + str(score))
                
        #for word, freq in ordered_words:
        #    print(word)
        
        
        
        print("\n\n")
       """ 
# get top keywords from all titles
# number of keywords included / # of words in title


