from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Activity, UserProfile, EmergencyContact,Match,Notification
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import EmergencyContactForm
import json


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
    # Updated: Only exclude activities that have a match that is officially APPROVED and INCOMPLETE
    activities = Activity.objects.filter(status='open').exclude(
    match__approval_status='approved',
    match__completion_status='incomplete' 
    ).distinct()
    
    activity_list = []

    for act in activities:

        active_applied_users = list(act.match_set.filter(
            approval_status='pending',
            completion_status='incomplete' # This excludes 'cancelled' matches
        ).values_list('volunteer_id', flat=True))
        
        activity_list.append({
            'id': act.id,
            'activity_name': act.activity_name,
            'category': act.get_category_display(), 
            'council_area': act.get_council_area_display(),
            'date': str(act.date),
            'time': str(act.time),
            'requester_id': act.requester.id,
            'requester_username': act.requester.username,
            'additional_details': act.additional_details, 
            'applied_volunteer_ids': active_applied_users,
            'additional_details': act.additional_details
        })
        
    return JsonResponse(activity_list, safe=False)

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
    
    from django.db.models import Q 

    # Get user profile 
    user_profile = get_object_or_404(UserProfile, user=request.user)

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

    # 1. Truly Open Requests (Senior/Care Home perspective)
    # Updated: Keep the activity in "Open Requests" until someone is actually APPROVED
    my_open_requests = Activity.objects.filter(
        requester=request.user, 
        status='open'
    ).exclude(
        match__approval_status='approved', 
        match__completion_status='incomplete' 
    ).distinct()

    # 2. Base Query for Matches (Pending, Confirmed, History)
    base_matches = Match.objects.filter(
        Q(activity__requester=request.user) | Q(volunteer=request.user)
    ).select_related('activity', 'volunteer', 'activity__requester')

    # 3. Pending Activities: This will now correctly show BOTH Aasim and Aayan
    pending = base_matches.filter(
        approval_status='pending',
        completion_status='incomplete'
    )

    # 4. Confirmed Activities
    confirmed = base_matches.filter(
        approval_status='approved', 
        completion_status='incomplete'
    )

    # Inside the profile function in views.py

    if user_profile.usertype == 'volunteer':
        # Volunteers see everything they applied for that is now finished
        history_filter = Q(volunteer=request.user) & Q(hidden_by_volunteer=False)
    else:
        # Seniors/Care Homes ONLY see activities where they actually approved a volunteer
        # This filters out the "auto-rejected" volunteer applications from their history
        history_filter = Q(activity__requester=request.user) & Q(hidden_by_requester=False) & Q(approval_status='approved')

    # Apply the filter to fetch the history
    history = Match.objects.filter(
        history_filter,
        completion_status__in=['completed', 'cancelled']
    ).select_related('activity', 'volunteer', 'activity__requester').order_by('-id')[:5]

    is_busy = False
    if user_profile.usertype == 'volunteer':
        is_busy = Match.objects.filter(
            volunteer=request.user, 
            approval_status='approved', 
            completion_status='incomplete'
        ).exists()
    
    context_dict = {
        'profile': user_profile,
        'emergency_contacts': emergency_contacts,
        'form': form,
        'my_open_requests': my_open_requests,
        'pending': pending,
        'confirmed': confirmed,
        'history': history,
        'is_busy': is_busy,
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

@login_required
def post_activity(request):
    if request.method == 'POST':
        # Get data from the modal form
        activity_name = request.POST.get('activity_name')
        category = request.POST.get('category')
        date = request.POST.get('date')
        time = request.POST.get('time')
        council_area = request.POST.get('council_area')
        additional_details = request.POST.get('additional_details')

        # Create the activity in the database
        Activity.objects.create(
            requester=request.user, # The Senior/Care Home who is logged in
            activity_name=activity_name,
            category=category,
            date=date,
            time=time,
            council_area=council_area,
            additional_details=additional_details
        )
        
        # Send them back to the activities page to see their new post
        return redirect('kindred:activities')
    
    return redirect('kindred:activities')

@login_required
@require_POST
def approve_match(request, match_id):
    # 1. Find the match and the original activity
    match = get_object_or_404(Match, id=match_id, activity__requester=request.user)

    # NEW: Check if the volunteer being approved is already busy elsewhere
    if Match.objects.filter(volunteer=match.volunteer, approval_status='approved', completion_status='incomplete').exists():
        messages.error(request, f"{match.volunteer.username} is already confirmed for another activity and is no longer available.")
        # Optionally, you could auto-decline this match here
        return redirect('kindred:profile')
    
    old_activity = match.activity

    # 1. ARCHIVE THE OLD ACTIVITY
    # Changing status to something other than 'open' hides it from the feed.
    old_activity.status = 'closed' 
    old_activity.save()

    # 2. CREATE A FRESH INSTANCE for the confirmed plan
    # This generates a brand new ID so the feed resets completely.
    new_activity = Activity.objects.create(
        requester=old_activity.requester,
        activity_name=old_activity.activity_name,
        category=old_activity.category,
        date=old_activity.date,
        time=old_activity.time,
        council_area=old_activity.council_area,
        additional_details=old_activity.additional_details,
        status='open'
    )

    # 3. TRANSFER and APPROVE the match
    # Move the winner to the NEW activity so they survive the deletion of the old one.
    match.activity = new_activity
    match.approval_status = 'approved'
    match.save()

    # 4. AUTO-REJECT: Move other volunteers for the OLD activity to history
    other_pending_matches = Match.objects.filter(
        activity=old_activity, 
        approval_status='pending'
    ).exclude(id=match_id)

    for other in other_pending_matches:
        other.completion_status = 'cancelled'
        other.cancellation_reason = "Another volunteer was selected for this session."
        # Transfer them to the new activity so their history record remains valid
        other.activity = new_activity
        other.save()
        
        Notification.objects.create(
            user=other.volunteer,
            message=f"Update: A volunteer has been selected for '{new_activity.activity_name}'.",
            activity=new_activity
        )

    # 5. AUTO-WITHDRAW: Withdraw the approved volunteer from their other pending apps
    volunteer_other_apps = Match.objects.filter(
        volunteer=match.volunteer, 
        approval_status='pending'
    ).exclude(id=match_id)

    for app in volunteer_other_apps:
        Notification.objects.create(
            user=app.activity.requester,
            message=f"Volunteer {match.volunteer.username} is no longer available for '{app.activity.activity_name}'.",
            activity=app.activity
        )
        app.delete()

    # 6. DELETE THE OLD ACTIVITY
    # This wipes the 'approved' tie from the original ID, fixing the vanishing bug.
    # old_activity.delete()

    # 7. Final Notification for the winner
    Notification.objects.create(
        user=match.volunteer,
        message=f"Your request for {new_activity.activity_name} was approved!",
        activity=new_activity
    )
    
    messages.success(request, f'You have successfully approved {match.volunteer.username}!')
    return redirect('kindred:profile')

@login_required
@require_POST
def redact_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, requester=request.user)
    
    try:
        data = json.loads(request.body)
        # Use the provided reason, or fall back to a default if empty
        custom_reason = data.get('reason', "").strip() or f"Withdrawn by {request.user.username}."
    except (json.JSONDecodeError, TypeError):
        custom_reason = f"Withdrawn by {request.user.username}."


    # Use the logged-in user's username for the message
    withdrawer_name = request.user.username
    
    # 1. Find all pending volunteers who applied for this specific activity
    pending_matches = Match.objects.filter(activity=activity, approval_status='pending')
    
    # 2. Notify them and move the record to their history as 'cancelled'
    for match in pending_matches:
        Notification.objects.create(
            user=match.volunteer,
            # UPDATE: Dynamic name for the volunteer's notification
            message=f"The activity '{activity.activity_name}' has been withdrawn by {withdrawer_name}.",
            activity=activity
        )
        
        match.completion_status = 'cancelled'
        # UPDATE: Link the cancellation to the user for the "Withdrawn by you" logic
        match.cancelled_by = request.user
        match.cancellation_reason = custom_reason
        match.save()

    # 3. Archive the activity rather than deleting it immediately
    activity.status = 'closed'
    activity.save()

    return JsonResponse({
        'status': 'success', 
        'message': f'Activity withdrawn by {withdrawer_name} and volunteers notified.'
    })

@login_required
@require_POST
def join_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    # NEW: Check if this volunteer already has a confirmed, unfinished activity
    has_active_confirmed_match = Match.objects.filter(
        volunteer=request.user, 
        approval_status='approved', 
        completion_status='incomplete'
    ).exists()

    if has_active_confirmed_match:
        return JsonResponse({
            'status': 'error', 
            'message': 'You already have a confirmed activity. Please complete it before applying for another.'
        })
    
    # Check if there is an existing ACTIVE match
    # We must exclude BOTH 'cancelled' and 'completed' so volunteers can re-apply
    existing_match = Match.objects.filter(
        activity=activity, 
        volunteer=request.user
    ).exclude(completion_status__in=['cancelled', 'completed']).exists()

    if not existing_match:
        # Create a new match if no active one exists
        Match.objects.create(
            activity=activity,
            volunteer=request.user,
            approval_status='pending',
            completion_status='incomplete' # Ensure it starts as incomplete
        )

        Notification.objects.create(
            user=activity.requester,
            message=f"Volunteer {request.user.username} applied for {activity.activity_name}!",
            activity=activity
        )   
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def remove_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    old_activity = match.activity
    reason = request.POST.get('reason', 'No reason provided.')
    
    if request.user == old_activity.requester or request.user == match.volunteer:
        recipient = match.volunteer if request.user == old_activity.requester else old_activity.requester
        
        # 1. ARCHIVE THE OLD ACTIVITY
        # Instead of deleting, we change status so it stays in history but leaves the feed.
        old_activity.status = 'closed'
        old_activity.save()

        # 2. CREATE A BRAND NEW FRESH INSTANCE
        # This resets the browse feed for new volunteers with a new ID.
        Activity.objects.create(
            requester=old_activity.requester,
            activity_name=old_activity.activity_name,
            category=old_activity.category,
            date=old_activity.date,
            time=old_activity.time,
            council_area=old_activity.council_area,
            additional_details=old_activity.additional_details,
            status='open'
        )

        # 3. Update Match details
        # We keep it tied to the 'closed' old_activity so history is accurate.
        match.completion_status = 'cancelled'
        match.cancelled_by = request.user
        match.cancellation_reason = reason
        match.save()
        
        # 4. Create the notification
        Notification.objects.create(
            user=recipient,
            message=f"The plan for '{old_activity.activity_name}' has been cancelled by {request.user.username}."
        )
        
        messages.info(request, "Plan cancelled. A fresh request has been re-posted.")
    
    return redirect('kindred:profile')

@login_required
@require_POST
def complete_activity(request, match_id):
    from django.db.models import Q
    # 1. Find the match for either user
    match = get_object_or_404(
        Match, 
        Q(id=match_id) & (Q(activity__requester=request.user) | Q(volunteer=request.user))
    )

    feedback = request.POST.get('feedback', '')
    activity = match.activity 
    
    # 2. ARCHIVE THE ACTIVITY
    # Status 'closed' keeps the record but hides it from the browse feed
    activity.status = 'closed'
    activity.save()

    # --- STEP 3 (REMOVED): Activity.objects.create logic deleted to stop duplicates ---

    # 4. Update the match details for history
    match.completion_status = 'completed'
    match.cancellation_reason = feedback 
    match.save()

    # 5. Notify the other party
    recipient = match.volunteer if request.user == activity.requester else activity.requester
    Notification.objects.create(
        user=recipient,
        message=f"'{activity.activity_name}' has been marked as completed by {request.user.username}.",
        activity=activity
    )
    
    messages.success(request, "Session completed!")
    return redirect('kindred:profile')

@login_required
def edit_activity(request, activity_id):
    # Ensure only the requester who posted it can edit it
    activity = get_object_or_404(Activity, id=activity_id, requester=request.user)
    
    if request.method == 'POST':
        # Update fields from the form
        activity.activity_name = request.POST.get('activity_name')
        activity.category = request.POST.get('category')
        activity.council_area = request.POST.get('council_area')
        activity.date = request.POST.get('date')
        activity.time = request.POST.get('time')
        activity.additional_details = request.POST.get('additional_details')
        activity.save()
        
        # Security logic: Reset all matches to pending because time/location changed
        Match.objects.filter(activity=activity).update(approval_status='pending')

        # 2. TRIGGER NOTIFICATIONS
        # Notify every volunteer who was matched with this activity
        volunteers = User.objects.filter(matches__activity=activity)
        for volunteer in volunteers:
            Notification.objects.create(
                user=volunteer,
                message=f"The activity '{activity.activity_name}' has been updated. Please check the new details.",
                activity=activity
            )
        
        messages.success(request, "Activity updated! Any existing volunteers must be re-approved.")
        return redirect('kindred:activities')
    
@login_required
@require_POST
def clear_notification_history(request):
    # Deletes all notification records for the current user
    request.user.notifications.all().delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def clear_activity_history(request):
    # Instead of deleting, just hide it for the person who clicked 'Clear'
    Match.objects.filter(activity__requester=request.user).update(hidden_by_requester=True)
    Match.objects.filter(volunteer=request.user).update(hidden_by_volunteer=True)
    
    messages.success(request, "Activity history cleared.")
    return redirect('kindred:profile')

from django.db.models import Q

@login_required
def get_user_profile_json(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_profile = target_user.userprofile
    
    # Privacy Check: Are these users "Matched" in an approved or completed state?
    is_matched = Match.objects.filter(
        (Q(activity__requester=request.user) & Q(volunteer=target_user)) |
        (Q(activity__requester=target_user) & Q(volunteer=request.user))
    ).filter(completion_status__in=['incomplete', 'completed']).exists()

    data = {
        'full_name': f"{target_profile.first_name} {target_profile.last_name}",
        'usertype': target_profile.usertype,
        'council_area': target_profile.get_council_area_display(),
        'profile_picture_url': target_profile.profile_picture.url if target_profile.profile_picture else None,
        'joined': "Jan 2025", # Or use target_user.date_joined
        'bio': "I love helping out in my community!", # Add bio field to model later if desired
    }

    # Only share sensitive details if they are matched or if it's a Care Home
    if is_matched or target_profile.usertype == 'care_home':
        data['email'] = target_user.email
        if target_profile.usertype == 'care_home':
            data['address'] = target_profile.address
            
    return JsonResponse(data)



# Updated views.py

@login_required
@require_POST
def withdraw_application(request, match_id):
    """Handles withdrawal from the Profile Page using a Match ID."""
    match = get_object_or_404(Match, id=match_id, volunteer=request.user, approval_status='pending')
    activity = match.activity

    try:
        data = json.loads(request.body)
        custom_reason = data.get('reason', "").strip() or "Volunteer withdrew application."
    except (json.JSONDecodeError, TypeError):
        custom_reason = "Volunteer withdrew application."    
    
    # 1. Notify the Senior/Care Home
    Notification.objects.create(
        user=activity.requester,
        message=f"Volunteer {request.user.username} has withdrawn their application for '{activity.activity_name}'.",
        activity=activity
    )
    
    # 2. Persist the record in history instead of deleting
    match.completion_status = 'cancelled'
    match.cancelled_by = request.user
    match.cancellation_reason = custom_reason
    match.save()
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def withdraw_by_activity(request, activity_id):
    """Handles withdrawal from the Browse Page using the Activity ID."""
    # Add approval_status='pending' to ensure we only get the active application
    match = get_object_or_404(
        Match, 
        activity_id=activity_id, 
        volunteer=request.user, 
        approval_status='pending', # CRITICAL: Only target the live application
        completion_status='incomplete' # Also ensure it hasn't been finished
    )
    
    # Notify the requester
    Notification.objects.create(
        user=match.activity.requester,
        message=f"Volunteer {request.user.username} has withdrawn their application for '{match.activity.activity_name}'.",
        activity=match.activity
    )
    
    # Parse the reason from JSON
    try:
        data = json.loads(request.body)
        custom_reason = data.get('reason', "").strip() or "Volunteer withdrew application."
    except (json.JSONDecodeError, TypeError):
        custom_reason = "Volunteer withdrew application."

    # Move to history
    match.completion_status = 'cancelled'
    match.cancelled_by = request.user
    match.cancellation_reason = custom_reason
    match.save()
    
    return JsonResponse({'status': 'success'})