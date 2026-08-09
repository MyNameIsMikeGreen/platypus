from django.urls import include, path

urlpatterns = [
    path("", include("recipes.urls")),
]

handler404 = "recipes.views.not_found"
