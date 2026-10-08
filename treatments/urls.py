from django.urls import path
from . import views

app_name = 'treatments'

urlpatterns = [
    path('', views.treatment_list, name='treatment_list'),
    path('category/<slug:category_slug>/', views.treatment_list, name='category_detail'),
    path('offers/', views.offer_list, name='offer_list'),
    path('<slug:slug>/', views.treatment_detail, name='treatment_detail'),
]
