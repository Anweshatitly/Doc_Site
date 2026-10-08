from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('category/<slug:category_slug>/', views.post_list, name='category_detail'),
    path('tag/<slug:tag_slug>/', views.post_list, name='tag_detail'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
