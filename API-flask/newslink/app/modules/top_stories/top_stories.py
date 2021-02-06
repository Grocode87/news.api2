from app.models import Article, Cluster

def get_top_stories():
    clusters = Cluster.query.order_by(Cluster.rank.desc()).limit(10).all()
    
    return [c.serialize() for c in clusters]
        
    
