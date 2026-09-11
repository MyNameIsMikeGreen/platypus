from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("planner/", views.planner, name="planner"),
    path("search-results/", views.search_results, name="search-results"),
    path("<int:recipe_id>/<slug:slug>/", views.detail, name="detail"),
]
