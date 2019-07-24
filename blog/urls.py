from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    # path('users/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('new_post/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('search/', views.search, name='search'),
    path('blog/search/', views.blog_search, name='blog_search'),
    path('post/<int:pk>/save_post/', views.save_post, name='save_post'),
    path('post/<int:pk>/un_save_post/', views.un_save_post, name='un_save_post'),
    path('post/<int:pk>/like_comment/', views.like_comment, name='like_comment'),

]
