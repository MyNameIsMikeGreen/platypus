from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('planner/', views.planner, name='planner'),
    path('planner/<int:recipe_count>/', views.planner_results, name='planner_results'),
    path('<int:recipe_id>/', views.detail, name='detail'),
]
