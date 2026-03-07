from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Activity

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