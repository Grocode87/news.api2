from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import FLOAT

Base = declarative_base()

# Articles
# Clusters
# Entities
# Entity Frequency

# Article_Details
# Entity_Details


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(512), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    cleaned_content = Column(Text, nullable=True)
    url = Column(String(512), nullable=False)
    image_url = Column(String(512), nullable=False)
    date_created = Column(DateTime, nullable=False)
    category = Column(String(100), nullable=False)

    entities = relationship("Entity", secondary="article_entity")
    

    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)

class Cluster(Base):
    __tablename__ = 'cluster'

    id = Column(Integer, primary_key=True, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False)
    category = Column(String(100))
    rank = Column(Float, default=0)
    top_article_id = Column(Integer, ForeignKey('article.id'))

    articles = relationship('Article', secondary='cluster_article')
    top_article = relationship(Article)
    
    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)

class Entity(Base):
    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(512), nullable=False, index=True)
    total_occurences = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)

class EntityFrequency(Base):
    __tablename__ = 'entity_frequency'

    id = Column(Integer, primary_key=True, nullable=False)
    entity_id = Column(Integer, ForeignKey('entity.id'))
    date_added = Column(DateTime, nullable=False)

    entity = relationship(Entity)
    
    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)

class ClusterArticle(Base):
    __tablename__ = 'cluster_article'
    id = Column(Integer, primary_key=True, nullable=False)
    cluster_id = Column(Integer, ForeignKey('cluster.id'))
    article_id = Column(Integer, ForeignKey('article.id'))
    rank = Column(Float, default=0)

    cluster = relationship(Cluster, backref=backref("cluster_article"))
    article = relationship(Article, backref=backref("cluster_article"))
    
    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)

class ArticleEntity(Base):
    __tablename__ = 'article_entity'
    id = Column(Integer, primary_key=True, nullable=False)
    article_id = Column(Integer, ForeignKey('article.id'))
    entity_id = Column(Integer, ForeignKey('entity.id'))
    score = Column(Integer, nullable=False)
    
    def __repr__(self):
        return '<UserModel model {}>'.format(self.id)
