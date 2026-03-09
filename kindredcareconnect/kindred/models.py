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

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=255, blank=True) 
    last_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    council_area = models.CharField(max_length=255, blank=True)
    # living_situation = models.CharField(max_length=20, blank=True)
    care_home_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.usertype})"

# --- 2. Emergency Contact ---
class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    relationship = models.CharField(max_length=20)

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

    def __str__(self):
        return f"{self.activity_name} ({self.category})"

# --- 4. Match Results ---
class Match(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches')
    approval_status = models.CharField(max_length=20, default='pending')
    completion_status = models.CharField(max_length=20, default='incomplete')

