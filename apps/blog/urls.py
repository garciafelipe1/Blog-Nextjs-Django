from django.urls import path



from .views import PostDetailView,PostListView,PostHeadingView,IncrementPostView

urlpatterns=[
    path('posts/',PostListView.as_view(),name='post-list'),
    path('post/',PostDetailView.as_view(),name='post-detail'),
    path('posts/headings/',PostHeadingView.as_view(),name='post-headings'),
    path('post/increment_clicks/',IncrementPostView.as_view(),name='increment-post-clicks'),
    
]