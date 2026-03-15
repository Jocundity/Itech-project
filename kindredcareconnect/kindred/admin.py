from django.contrib import admin
from .models import Activity, UserProfile, EmergencyContact

# Register your models here.

admin.site.register(Activity)
admin.site.register(UserProfile)
admin.site.register(EmergencyContact)
