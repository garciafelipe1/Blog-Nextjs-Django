from django.db import models
from django.utils import timezone
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils.html import format_html

from apps.media.models import Media
from apps.media.serializers import MediaSerializer

def blog_thumbnail_directory(instance, filename):
    sanitized_title=slugify.instance.title.replace(" ","-")
    return "thumbnails/blog/{0}/{1}".format(sanitized_title,filename)

    
def category_thumbnail_directory(instance, filename):
    sanitized_name=slugify.instance.name.replace(" ","-")
    return "thumbnails/blog_categories/{0}/{1}".format(sanitized_name,filename)




class Category(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    parent=models.ForeignKey('self',related_name='children',on_delete=models.CASCADE,null=True,blank=True)
        
    name=models.CharField(max_length=255)
    title=models.CharField(max_length=255,blank=True,null=True)
    description=models.TextField(blank=True,null=True)
    thumbnail=(models.ImageField(upload_to=category_thumbnail_directory,blank=True,null=True))
    slug=models.CharField(max_length=128)
    
    def __str__(self):
        return self.name
    

class Post(models.Model):
    
    class PostObjects(models.Manager):
        def get_queryset(self):

            return super().get_queryset().filter(status='published')
    
    status_options = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    ) 
    
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    content =RichTextField()
    thumbnail = models.ForeignKey(Media,on_delete=models.SET_NULL,null=True,blank=True,related_name='post_thumbnails')
    
    keywords = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    
    category=models.ForeignKey(Category,on_delete=models.PROTECT)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    

    status = models.CharField(max_length=10, choices=status_options, default='draft')
   
    objects = models.Manager() # defaultmanager
    postobjects = PostObjects() #custom manager
    
    class Meta:
        ordering = ("status","-created_at")
        
    def __str__(self):
        return self.title
    
    def thubnail_preview(self):
        if self.thumbnail:
            try:
                serializers = MediaSerializer(instance=self.thumbnail)
                data = serializers.data
                print(f"Serializers data: {data}")  # Agrega esto
                url = data.get('url')
                print(f"URL: {url}")  # Agrega esto
                if url:
                    return format_html('<img src="{url}" style="width: 100px; height: auto;" />', url=url)
                else:
                    return 'URL no encontrada'
            except Exception as e:
                print(f"Error: {e}")  # Agrega esto
                return f'Error: {e}'
        return 'Sin miniatura'            


class PostView(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_views')
    ip_adress=models.GenericIPAddressField()
    timestap=models.DateTimeField(auto_now=True)
    
    
class PostAnalytics(models.Model):
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_analytics')
    views=models.PositiveIntegerField(default=0)
    impressions=models.PositiveIntegerField(default=0)
    clicks=models.PositiveIntegerField(default=0)
    click_through_rate=models.FloatField(default=0)
    avg_time_on_page=models.FloatField(default=0)
    
    
    def _update_click_through_rate(self):
        if self.impressions > 0:
            self.click_through_rate = (self.clicks / self.impressions) * 100
        else: 
            self.click_through_rate=0
        self.save()
    
    def increment_click(self):
        self.clicks += 1
        self.save()
        self._update_click_through_rate()
    
    
    
    def increment_impressions(self):
        self.impressions +=1
        self.save()
        self._update_click_through_rate()
        
    def increment_view(self,ip_adress):
        if not PostView.objects.filter(post=self.post,ip_adress=ip_adress).exists():
            PostView.objects.create(post=self.post,ip_adress=ip_adress)
            
            self.views += 1
            self.save()
        
    
          

class Heading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='headings')
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    level = models.IntegerField(choices=[
        (1, "H1"),
        (2, "H2"),
        (3, "H3"),
        (4, "H4"),
        (5, "H5"),
        (6, "H6"),
    ])
    order = models.PositiveIntegerField()

    class Meta:  
        ordering = ("order",)  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



@receiver(post_save, sender=Post)
def create_post_analytics(sender, instance,created, **kwargs):
    
    if created:
        PostAnalytics.objects.create(post=instance)
        

