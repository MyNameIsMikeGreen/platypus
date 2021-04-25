from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .models import Recipe

app_name = 'recipes'

info_dict = {
    'queryset': Recipe.objects.all(),
    'date_field': 'published_date',
}

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('planner/', views.planner, name='planner'),
    path('<int:recipe_id>/<str:slug>/', views.detail, name='detail_with_slug'),
    path('<int:recipe_id>/', views.detail, name='detail'),
    path('sitemap.xml', sitemap,
         {'sitemaps': {'blog': GenericSitemap(info_dict, changefreq="monthly", protocol="https")}},
         name='django.contrib.sitemaps.views.sitemap'),
]
