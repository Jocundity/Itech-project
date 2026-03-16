from django.urls import path
from django.contrib.auth import views as auth_views

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
    path('delete-emergency-contact/<int:contact_id>/', views.delete_emergency_contact, name='delete_emergency_contact'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='kindred:index'), name='logout'),
    path('post-activity/', views.post_activity, name='post_activity'),
    path('approve-match/<int:match_id>/', views.approve_match, name='approve_match'),
    path('redact-activity/<int:activity_id>/', views.redact_activity, name='redact_activity'),
    path('join-activity/<int:activity_id>/', views.join_activity, name='join_activity'),
    path('remove-match/<int:match_id>/', views.remove_match, name='remove_match'),
    path('complete-activity/<int:match_id>/', views.complete_activity, name='complete_activity'),
    path('edit-activity/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('notifications/clear-history/', views.clear_notification_history, name='clear_history'),
    path('profile/clear-history/', views.clear_activity_history, name='clear_activity_history'),
    path('api/user-profile/<int:user_id>/', views.get_user_profile_json, name='user_profile_json'),
    path('withdraw-application/<int:match_id>/', views.withdraw_application, name='withdraw_application'),
    path('withdraw-by-activity/<int:activity_id>/', views.withdraw_by_activity, name='withdraw_by_activity'),
    
]