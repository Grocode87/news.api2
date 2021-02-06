from app.models import Article, Cluster, ClusterArticle
from sqlalchemy.orm import load_only

def search_stories(query):
     clusters = Cluster.query.filter(Cluster.articles.any(
         Article.title.like('%' + query + '%'))).all()
     
     return [c.serialize() for c in clusters]
