from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Activity
from django.contrib.auth.decorators import login_required
from .models import Activity, UserProfile, EmergencyContact

# Create your views here.
def index(request):
    context_dict = {}

    return render(request, "index.html", context=context_dict)

def about(request):
    context_dict = {}

    return render(request, "about.html", context=context_dict)

def activities(request):
    context_dict = {}
    return render(request, 'activities.html', context=context_dict)

def activity_list_json(request):
    # Fetching all activities from the database
    activities = Activity.objects.all().values(
        'id', 'activity_name', 'category', 'council_area', 'date', 'time'
    )
    # Returning data as JSON for JavaScript to fetch
    return JsonResponse(list(activities), safe=False)

@login_required
def profile(request):
    # 1.Get user profile 
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    # 2.Get emergency contact if user is senior
    emergency_contact = None
    if user_profile and user_profile.usertype == 'senior':
        emergency_contact = EmergencyContact.objects.filter(user=request.user).first()

    my_matches = []
    # 3. Get activity history (corresponding to myMatches in React) [cite: 331]
    # Here we demonstrate fetching all activities the user has participated in
    context_dict = {
        'profile': user_profile,
        'emergency_contact': emergency_contact,
        'my_matches': my_matches,
    }
    
    return render(request, 'kindred/profile.html', context=context_dict)