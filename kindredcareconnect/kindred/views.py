from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse

from .models import Activity, UserProfile, EmergencyContact
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        usertype = request.POST.get('usertype')
        care_home_name = request.POST.get('care_home_name')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        council_area = request.POST.get('council_area')
        address = request.POST.get('address')


        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match"})
        
        try:
            user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        except IntegrityError:
            return render(request, "signup.html", {"error": "Username is already taken"})
        

        UserProfile.objects.create(
            user=user,
            usertype=usertype,
            care_home_name=care_home_name,
            first_name=first_name,
            last_name=last_name,
            gender = gender,
            council_area = council_area,
            address = address
        )

        return redirect("kindred:login")


    return render(request, "signup.html")

def check_username_exists(request):
    username = request.GET.get("username")

    if User.objects.filter(username=username).exists():
        return JsonResponse({"available": False})
    else:
        return JsonResponse({"available": True})

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("kindred:activities")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "signin.html")

    return render(request, "signin.html")
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
