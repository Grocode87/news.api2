from app import app, db

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy import and_

Base = declarative_base()
metadata = Base.metadata

db.reflect()


class Article(db.Model):
    __tablename__ = 'article'

    entities = db.relationship("Entity", secondary="article_entity")
    
    def serialize(self):
        # TODO: FIGURE OUT TOP ENTITIES EFFICIENTLY
        #top_entities = Entity.query.join(ArticleEntity, Entity.id == ArticleEntity.entity_id).add_columns(
        #    ArticleEntity.score).filter(ArticleEntity.article_id == self.id).order_by(ArticleEntity.score.desc()).limit(3).all()
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'image_url': self.image_url,
            'date_created': self.date_created,
            'entities': [e.serialize() for e in self.entities]
        }
    

class Cluster(db.Model):
    __tablename__ = 'cluster'

    articles = db.relationship('Article', secondary='cluster_article')
    
    def serialize(self):
        return {
            'id': self.id,
            'top_article': self.articles[0].serialize(),
            'articles': [a.serialize() for a in self.articles],
            'rank': self.rank,
            'category': self.category
        }
    

class Entity(db.Model):
    __tablename__ = 'entity'
    
    def serialize(self, score=None):
        return {
            'name': self.name,
            'score': score
}
    


class ClusterArticle(db.Model):
    __tablename__ = 'cluster_article'
    
    cluster = db.relationship(Cluster, backref=backref("cluster_article"))
    article = db.relationship(Article, backref=backref("cluster_article"))


class ArticleEntity(db.Model):
    __tablename__ = 'article_entity'
    

class EntityFrequency(db.Model):
    __tablename__ = 'entity_frequency'
    
    entity = db.relationship(Entity)


