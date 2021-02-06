import datetime
import time
from modals import Cluster as ClusterModel
from modals import EntityFrequency

class DBMaintanance():
    def __init__(self):
        pass
    
    def run_tasks(self, session):
        self.run_cluster_calculations(session)
        self.maintain_entity_freqs(session)
    

    def run_cluster_calculations(self, session):
        """
        Method to calculate cluster rank and category
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
