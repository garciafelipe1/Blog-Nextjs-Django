from celery import shared_task
import logging

from .models import PostAnalytics

logger = logging.getLogger(__name__)


@shared_task #incrementa las impresiones del post asociado
def increments_post_impressions(post_id):
   
   try:
       analytics,created=PostAnalytics.objects.get_or_create(post__id=post_id)
       analytics.increment_impressions()
   except Exception as e:
       logger.info(f"error incrementing impressions for post id{post_id}:{str(e)}")
    
    