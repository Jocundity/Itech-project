from django.urls import path

from . import views

app_name = "kindred"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path('activities/', views.activities, name='activities'),
    path('api/activities/', views.activity_list_json, name='activity_list_json'),
    path('profile/', views.profile, name='profile'),
]