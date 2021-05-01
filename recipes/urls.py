from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemap import RecipeSitemap

app_name = 'recipes'

sitemaps = {'dynamic': RecipeSitemap}

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('planner/', views.planner, name='planner'),
    path('<int:recipe_id>/<str:slug>/', views.detail, name='detail_with_slug'),
    path('<int:recipe_id>/', views.detail, name='detail'),
    path('sitemap.xml', sitemap,
         {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]
