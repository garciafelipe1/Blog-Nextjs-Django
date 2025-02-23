from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from rest_framework import permissions

from .models import Post,Heading,PostAnalytics
from .serializers import PostListSerializer,PostSerializer,HeadingSerializer,PostView
from .utils import get_client_ip
from .tasks import increments_post_impressions

class PostListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            posts = Post.postobjects.all()

            if not posts.exists():
                raise NotFound(detail="Post does not exist")

            serializer_post = PostListSerializer(posts, many=True).data

            for post in posts:
                increments_post_impressions.delay(post.id)

        except Post.DoesNotExist:
            raise NotFound(detail="No post found")
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

        return Response(serializer_post)

# class PostListView(ListAPIView):
#     queryset = Post.postobjects.all() #objetos que queremos mostrar
#     serializer_class = PostListSerializer
    
class PostDetailView(RetrieveAPIView):
    def get(self,request,slug):
        try:
            post=Post.postobjects.get(slug=slug)
        except Post.DoesNotExist:
            raise NotFound(detail="Post does not exist")
        except Exception as e:
            raise APIException(detail=f"an unespected error ocurred :{str(e)}")
        serializer_post=PostSerializer(post).data
        #increment post count   
        try:
            post_analytics=PostAnalytics.objects.get(post=post)
            post_analytics.increment_views(request)
        except PostAnalytics.DoesNotExist:
            raise NotFound(detail="Analytics data for this post does not exist")
        except Exception as e:
            raise APIException(detail=f"an error ocurred while updating post analytics :{str(e)}")
         
        return Response(serializer_post)


class PostHeadingView(ListAPIView):
    serializer_class=HeadingSerializer
    
    def get_queryset(self):
        post_slug=self.kwargs.get("slug")
        return Heading.objects.filter(post__slug=post_slug)


class IncrementPostView(APIView):

    def post(self, request):
        data = request.data
        # Incrementa el contador de vistas basado en sus clicks
        try:
            post = Post.postobjects.get(slug=data['slug'])
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post does not exist")

        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_click()
        except Exception as e:
            raise APIException(detail=f"An error occurred while updating post analytics: {str(e)}")

        return Response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })

