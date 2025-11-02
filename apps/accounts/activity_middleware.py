from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class ActivityTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity for online status
    """
    
    def process_request(self, request):
        """Update last activity for authenticated users"""
        if request.user.is_authenticated:
            # Only update if user is support agent or admin (for chat availability)
            if request.user.role in ['support_agent', 'admin']:
                # Only update if last activity is more than 1 minute ago to avoid too many DB writes
                if (not request.user.last_activity or 
                    timezone.now() - request.user.last_activity > timezone.timedelta(minutes=1)):
                    request.user.update_activity()
        
        return None