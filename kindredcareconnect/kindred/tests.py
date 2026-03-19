from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, EmergencyContact, Activity, Match, Notification
from datetime import date, time
from django.utils import timezone
from .forms import EmergencyContactForm
from django.urls import reverse

""" Model Tests """
class TestUserProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.user_profile = UserProfile.objects.create(user=self.user, 
                                   usertype="volunteer",
                                   first_name="John",
                                   last_name="Smith",
                                   gender="male",
                                   council_area="aberdeen_city"
                                   )

    def test_userprofile_creation(self):
        self.assertEqual(self.user_profile.user.username, "johnsmith")

    def test_userprofile_fields(self):
        self.assertEqual(self.user_profile.usertype, "volunteer")
        self.assertEqual(self.user_profile.first_name, "John")
        self.assertEqual(self.user_profile.last_name, "Smith")
        self.assertEqual(self.user_profile.council_area,"aberdeen_city")

    def test_userprofile_str(self):
        self.assertEqual(str(self.user_profile), "johnsmith (volunteer)")

class TestEmergencyContactModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.emergency_contact = EmergencyContact.objects.create(user=self.user,
                                                                 name="Mary",
                                                                 mobile="07712345678",
                                                                 relationship="Spouse")
        
    def test_emergencycontact_creation(self):
        self.assertEqual(self.emergency_contact.user.username, "johnsmith")

    def test_emergencycontact_fields(self):
        self.assertEqual(self.emergency_contact.name, "Mary")
        self.assertEqual(self.emergency_contact.mobile, "07712345678")
        self.assertEqual(self.emergency_contact.relationship, "Spouse")

    def test_emergencycontact_str(self):
        self.assertEqual(str(self.emergency_contact), "johnsmith - Mary")

class TestActivityModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.activity = Activity.objects.create(requester=self.user,
                                                category="Outdoors",
                                                activity_name="Morning walk",
                                                council_area="aberdeen_city",
                                                date=date(2026, 3, 16),
                                                time=time(9, 0))
       
    def test_activity_creation(self):
        self.assertEqual(self.activity.requester.username, "johnsmith")

    def test_activity_fields(self):
        self.assertEqual(self.activity.category, "Outdoors")
        self.assertEqual(self.activity.activity_name, "Morning walk")
        self.assertEqual(self.activity.council_area, "aberdeen_city")
        self.assertEqual(self.activity.date, date(2026, 3, 16))
        self.assertEqual(self.activity.time, time(9, 0))
        self.assertEqual(self.activity.status, "open") # default value

    def test_activity_str(self):
        self.assertEqual(str(self.activity), "Morning walk (Outdoors)")

class TestMatchModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.activity = Activity.objects.create(requester=self.user,
                                                category="Outdoors",
                                                activity_name="Morning walk",
                                                council_area="aberdeen_city",
                                                date=date(2026, 3, 16),
                                                time=time(9, 0))
        
        self.match = Match.objects.create(activity=self.activity,
                                          volunteer=self.user,
                                          )

    def test_match_creation(self):
        self.assertEqual(self.match.activity.activity_name, "Morning walk")
        self.assertEqual(self.match.volunteer.username, "johnsmith")
        
    def test_match_fields(self):
        # Default values:
        self.assertEqual(self.match.approval_status, "pending")
        self.assertEqual(self.match.completion_status, "incomplete")
        self.assertFalse(self.match.hidden_by_requester)
        self.assertFalse(self.match.hidden_by_volunteer)

class NotficationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.notification = Notification.objects.create(user=self.user,
                                                       message="message"
                                                       )
    
    def test_notification_creation(self):
        self.assertEqual(self.notification.user.username, "johnsmith")

    def test_notification_fields(self):
        self.assertEqual(self.notification.message, "message")
        self.assertFalse(self.notification.is_read) # default value

    def test_notification_creation_time(self):
        now = timezone.now()
        diff = now - self.notification.created_at
        # Test that notifcation was created within the last 5 seconds
        self.assertLess(diff.total_seconds(), 5)

""" Form Tests """
class TestEmergencyContactForm(TestCase):
    def test_emergency_contact_form_valid(self):
        form_data = {
            "name": "Mary",
            "mobile": "07712345678",
            "relationship": "Spouse"
        }

        form = EmergencyContactForm(data=form_data)
        self.assertTrue(form.is_valid())

""" View Tests """
class TestIndexView(TestCase):
    def test_index_view(self):     
        response = self.client.get(reverse("kindred:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

class TestProfileView(TestCase):
    def test_profile_view_not_logged_in(self):
        # Test that users cannot view profile page without being logged in
        response= self.client.get(reverse("kindred:profile"))
        self.assertNotEqual(response.status_code, 200)

    def test_profile_view_logged_in(self):
        self.user = User.objects.create_user(username="johnsmith",
                                  email="johnsmith@gmail.com",
                                  password="Sm1th_1234"
                                )
        
        self.user_profile = UserProfile.objects.create(user=self.user, 
                                   usertype="volunteer",
                                   first_name="John",
                                   last_name="Smith",
                                   gender="male",
                                   council_area="aberdeen_city"
                                   )
        self.client.login(username="johnsmith", password="Sm1th_1234")
        response= self.client.get(reverse("kindred:profile"))
        self.assertEqual(response.status_code, 200)





