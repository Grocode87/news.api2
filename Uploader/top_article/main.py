from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import Counter

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import sys
sys.path.append('..')
from modals import Base, Article, Cluster

db_url = "mysql://root:@localhost/newsapp?charset=utf8&use_unicode=0"

engine = create_engine(db_url, echo=False)

#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

stop_words = set(stopwords.words('english'))

clusters = session.query(Cluster).all()
for cluster in clusters:
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
        
# get top keywords from all titles
# number of keywords included / # of words in title


