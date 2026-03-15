from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse

from .models import Activity, UserProfile, EmergencyContact
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import EmergencyContactForm


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

        return redirect("kindred:signin")


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
            
            # Check if there is a 'next' parameter in the URL 
            # (this is to let user navigate to the page they were trying to access instead of default activities before signing in)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Default fallback if no 'next' is found
            return redirect("kindred:activities")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "signin.html")

    return render(request, "signin.html")
    

# Profile view (login required -- by default sends to sign in page)
@login_required
def profile(request):
    # Get user profile 
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    # Handle submission for emergency contact form
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)

        if form.is_valid():
            # To create a new contact
            EmergencyContact.objects.create(
                user=request.user,
                name=form.cleaned_data['name'],
                mobile=form.cleaned_data['mobile'],
                relationship=form.cleaned_data['relationship']
            )

            return redirect("kindred:profile") 
    else:
        form = EmergencyContactForm()

    # Get emergency contacts if user is senior
    emergency_contacts = []
    if user_profile and user_profile.usertype == 'senior':
        emergency_contacts = EmergencyContact.objects.filter(user=request.user)

    my_matches = []
    # Get activity history
    # Here we demonstrate fetching all activities the user has participated in
    context_dict = {
        'profile': user_profile,
        'emergency_contacts': emergency_contacts,
        'my_matches': my_matches,
        'form': form
    }
    
    return render(request, 'profile.html', context=context_dict)

@login_required
def delete_emergency_contact(request, contact_id):
    emergency_contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)
    emergency_contact.delete()
    return redirect("kindred:profile")

@login_required
def edit_profile(request):
    user = request.user
    profile = user.userprofile

    COUNCIL_AREA_CHOICES = [
        ("aberdeen_city", "Aberdeen City"),
        ("aberdeenshire", "Aberdeenshire"),
        ("angus", "Angus"),
        ("argyll_and_bute", "Argyll and Bute"),
        ("clackmannanshire", "Clackmannanshire"),
        ("dumfries_and_galloway", "Dumfries and Galloway"),
        ("dundee_city", "Dundee City"),
        ("east_ayrshire", "East Ayrshire"),
        ("east_dunbartonshire", "East Dunbartonshire"),
        ("east_lothian", "East Lothian"),
        ("east_renfrewshire", "East Renfrewshire"),
        ("city_of_edinburgh", "City of Edinburgh"),
        ("falkirk", "Falkirk"),
        ("fife", "Fife"),
        ("glasgow_city", "Glasgow City"),
        ("highland", "Highland"),
        ("inverclyde", "Inverclyde"),
        ("midlothian", "Midlothian"),
        ("moray", "Moray"),
        ("na_h-eileanan_siar_(western_isles)", "Na h-Eileanan Siar (Western Isles)"),
        ("north_ayrshire", "North Ayrshire"),
        ("north_lanarkshire", "North Lanarkshire"),
        ("orkney", "Orkney"),
        ("perth_and_kinross", "Perth and Kinross"),
        ("renfrewshire", "Renfrewshire"),
        ("scottish_borders", "Scottish Borders"),
        ("shetland_islands", "Shetland Islands"),
        ("south_ayrshire", "South Ayrshire"),
        ("south_lanarkshire", "South Lanarkshire"),
        ("stirling", "Stirling"),
        ("west_dunbartonshire", "West Dunbartonshire"),
        ("west_lothian", "West Lothian"),
    ]

    # Change user profile data based on form inputs
    if request.method == "POST":
        # Get data from form
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        care_home_name = request.POST.get('care_home_name')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        council_area = request.POST.get('council_area')
        address = request.POST.get('address')

        # Update data
        user.email = email
        password_changed = False

        if password:
            if password != confirm_password:
                return render(request, "edit-profile.html", {
                    "error": "Passwords do not match", 
                    "user": user, 
                    "profile": profile,
                    "council_area_choices": COUNCIL_AREA_CHOICES
                    })
            user.set_password(password)
            password_changed = True
        user.save()

        if password_changed:
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully!")
        else:
            messages.success(request, "Profile updated successfully!")
            
        if profile.usertype == "care_home":
            profile.care_home_name = care_home_name
            profile.address = address
        else:
            profile.first_name = first_name
            profile.last_name = last_name
            profile.gender = gender

        profile.council_area = council_area

        # Get profile picture
        new_picture = request.FILES.get("profile_picture")

        if new_picture:
            profile.profile_picture = new_picture

        profile.save()

        return redirect("kindred:profile")

    # If GET request, load pre-filled form
    else:
        return render(request, 'edit-profile.html', {
            "user": user, 
            "profile": profile,
            "council_area_choices": COUNCIL_AREA_CHOICES
            })
