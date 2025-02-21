from django.urls import path
from .views import PostListView

from .views import PostDetailView

urlpatterns=[
    path('post/',PostListView.as_view(),name='post-list'),
    path('post/<slug>/',PostDetailView.as_view(),name='post-detail'),
]