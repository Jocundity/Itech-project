from .models import Notification

def notification_processor(request):
    if request.user.is_authenticated:
        # Get last 5 notifications and total unread count
        unread_notifications = request.user.notifications.filter(is_read=False)
        return {
            'recent_notifications': request.user.notifications.all()[:5],
            'unread_count': unread_notifications.count()
        }
    return {}