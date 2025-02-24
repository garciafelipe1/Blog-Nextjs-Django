from celery import shared_task

import logging

import redis
from django.conf import settings
from .models import PostAnalytics,Post

logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)



@shared_task #incrementa las impresiones del post asociado
def increments_post_impressions(post_id):
   
   try:
       analytics,created=PostAnalytics.objects.get_or_create(post__id=post_id)
       analytics.increment_impressions()
   except Exception as e:
       logger.info(f"error incrementing impressions for post id{post_id}:{str(e)}")


@shared_task()
def increment_post_views_tasks(slug,ip_adress):
    
    try:
        post = Post.objects.get(slug=slug)
        post_analytics = PostAnalytics.objects.get_or_create(post=post)
        post_analytics.increment_view(ip_adress)
    except Exception as e:
        logger.info(f"error incrementing views for post slug{slug}:{str(e)}")
@shared_task
def sync_impressions_to_db():

    keys=redis_client.keys("post: impressions:*")

    for key in keys:
        try:
            post_id=key.decode("utf-8").split(":")[-1]
            impressions=int(redis_client.get(key))
            
            analytics,_=PostAnalytics.objects.get_or_create(post__id=post_id)
            analytics.impressions += impressions
            analytics.save()
            
            
            analytics._update_click_through_rate()
            
            redis_client.delete(key)
            
        except Exception as e:
            print(f"error syncing impressions fot {key}:{str(e)}")
            



    
    