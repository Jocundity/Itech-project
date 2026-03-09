from django.urls import path

from . import views

app_name = "kindred"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path('activities/', views.activities, name='activities'),
    path('api/activities/', views.activity_list_json, name='activity_list_json'),
    path('signup/', views.signup, name='signup'),
    path('check-username-exists/', views.check_username_exists, name='check_username_exists'),
    path('signin/', views.signin, name='signin'),
    path('profile/', views.profile, name='profile'),
]