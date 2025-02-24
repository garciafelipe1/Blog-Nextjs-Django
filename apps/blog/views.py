from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.views import APIView
from rest_framework_api.views import StandardAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from rest_framework import permissions,status


import redis

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache 
from .models import Post,Heading,PostAnalytics
from .serializers import PostListSerializer,PostSerializer,HeadingSerializer,PostView
from .utils import get_client_ip
from core.permissions import HasValidAPIKey
from .tasks import  increment_post_views_tasks



redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)




class PostListView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def get(self, request, *args, **kwargs):
        try:
            cached_posts = cache.get("post_list")
            if cached_posts:
                for post in cached_posts:  # cached_posts es una lista de diccionarios
                    redis_client.incr(f"post: impressions:{post['id']}")  # Accede como diccionario
                return self.paginate(request,cached_posts)

            posts = Post.postobjects.all()

            if not posts.exists():
                raise NotFound(detail="Post does not exist")

            serializer_post = PostListSerializer(posts, many=True).data

            cache.set("post_list", serializer_post, timeout=60 * 5)

            for post in posts:
                redis_client.incr(f"post: impressions:{post.id}")  # Aquí sí son objetos Post

        except Post.DoesNotExist:
            raise NotFound(detail="No post found")
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

        return self.paginate(request,serializer_post)


class PostDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    # @method_decorator(cache_page(60 * 1))
    def get(self, request):
        ip_address = get_client_ip(request)
        
        slug=request.query_params.get("slug")
        try:
            cached_post = cache.get(f"post:{slug}")

            # Incrementar vistas del post si está en caché
            if cached_post:
                increment_post_views_tasks.delay(cached_post['slug'], ip_address)
                return self.response(cached_post)

            # Si no está en caché, obtener el post de la base de datos
            post = Post.postobjects.get(slug=slug)
            serializer_post = PostSerializer(post).data

            # Almacenar en caché
            cache.set(f"post:{slug}", serializer_post, timeout=60 * 5)

            # Incrementar vistas en segundo plano
            increment_post_views_tasks.delay(slug, ip_address)

        except Post.DoesNotExist:
            raise NotFound(detail="Post does not exist")
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

        return self.response(serializer_post)


class PostHeadingView(StandardAPIView):
    permission_classes = [HasValidAPIKey]
    
    def get(self, request):
        post_slug=request.query_params.get("slug")
        heading_objects=Heading.objects.filter(post__slug=post_slug)
        serialized_data=HeadingSerializer(heading_objects,many=True).data
        return self.response(serialized_data)
    # serializer_class = HeadingSerializer

    # def get_queryset(self):
    #     post_slug = self.kwargs.get("slug")
    #     return Heading.objects.filter(post__slug=post_slug)


class IncrementPostView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def post(self, request):
        data = request.data
        try:
            post = Post.postobjects.get(slug=data['slug'])
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post does not exist")

        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_click()
        except Exception as e:
            raise APIException(detail=f"An error occurred while updating post analytics: {str(e)}")

        return self.response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })
