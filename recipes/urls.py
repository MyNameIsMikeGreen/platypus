from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.static import serve

from . import views
from .sitemap import RecipePageSitemap, SupportPageSitemap

app_name = 'recipes'

sitemaps = {
    'recipe_pages': RecipePageSitemap,
    'support_pages': SupportPageSitemap
}

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('planner/', views.planner, name='planner'),
    path('<int:recipe_id>/<str:slug>/', views.detail, name='detail_with_slug'),
    path('<int:recipe_id>/', views.detail, name='detail'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
