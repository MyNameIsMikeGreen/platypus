from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("offline/", views.offline, name="offline"),
    path("planner/", views.planner, name="planner"),
    path("search-results/", views.search_results, name="search-results"),
    path("site.webmanifest", views.manifest, name="manifest"),
    path("sw.js", views.service_worker, name="service-worker"),
    path("<int:recipe_id>/<slug:slug>/", views.detail, name="detail"),
]
