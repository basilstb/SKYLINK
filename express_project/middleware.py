from django.contrib.auth import logout
from django.http import HttpResponsePermanentRedirect

class AdminLogoutMiddleware:
    """Log out any authenticated user when they access the admin URLs.
    This forces the admin login page to appear on every visit.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the request is for the admin site and the user is logged in, log them out
        # If the request is for the admin site and the user is logged in but not staff, log them out
        if request.path.startswith('/admin/') and request.user.is_authenticated and not request.user.is_staff:
            logout(request)
        response = self.get_response(request)
        return response


class DomainRedirectMiddleware:
    """Redirect requests from the old Render domain to the new domain.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host == 'delivery-site-project-1.onrender.com':
            new_url = f"https://express-logistics-1.onrender.com{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)
        response = self.get_response(request)
        return response

