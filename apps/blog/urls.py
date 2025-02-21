from django.urls import path



from .views import PostDetailView,PostListView,PostHeadingView

urlpatterns=[
    path('posts/',PostListView.as_view(),name='post-list'),
    path('posts/<slug>/',PostDetailView.as_view(),name='post-detail'),
    path('posts/<slug>/headings/',PostHeadingView.as_view(),name='post-heading'),
]