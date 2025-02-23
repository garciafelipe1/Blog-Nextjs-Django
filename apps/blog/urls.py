from django.urls import path



from .views import PostDetailView,PostListView,PostHeadingView,IncrementPostView

urlpatterns=[
    path('posts/',PostListView.as_view(),name='post-list'),
    path('posts/<slug>/',PostDetailView.as_view(),name='post-detail'),
    path('post/<slug>/headings/',PostHeadingView.as_view(),name='post-heading'),
    path('post/increment_clicks/',IncrementPostView.as_view(),name='increment-post-clicks'),
    
]