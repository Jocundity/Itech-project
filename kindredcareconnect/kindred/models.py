from django.db import models
from django.contrib.auth.models import User

# --- 1. UserProfile ---
class UserProfile (models.Model):
    USER_TYPE_CHOICES = (
        ('volunteer', 'Volunteer'),
        ('senior', 'Senior'),
        ('care_home', 'Care Home'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to Say'),
    )

    COUNCIL_AREA_CHOICES = (
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
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=255, blank=True) 
    last_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    council_area = models.CharField(max_length=255, choices=COUNCIL_AREA_CHOICES,blank=True)
    # living_situation = models.CharField(max_length=20, blank=True)
    care_home_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.usertype})"

# --- 2. Emergency Contact ---
class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=11)
    relationship = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

# --- 3. Activity ---
class Activity(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_requested')
    category = models.CharField(max_length=255)
    activity_name = models.CharField(max_length=255)
    council_area = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    gender_preference = models.CharField(max_length=20, blank=True)
    additional_details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, default='open')

    def __str__(self):
        return f"{self.activity_name} ({self.category})"

# --- 4. Match Results ---
class Match(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches')
    approval_status = models.CharField(max_length=20, default='pending')
    completion_status = models.CharField(max_length=20, default='incomplete')
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_matches')
    hidden_by_requester = models.BooleanField(default=False)
    hidden_by_volunteer = models.BooleanField(default=False)
    cancellation_reason = models.TextField(max_length=500, blank=True, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # Optional: link to the activity so clicking the notification takes you there
    activity = models.ForeignKey('Activity', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
