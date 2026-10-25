import logging
import threading

from django.contrib.auth import logout
from django.http import HttpResponsePermanentRedirect

logger = logging.getLogger(__name__)


class AutoMigrateMiddleware:
    """Apply any pending database migrations once per server process.

    Prevents 500 errors caused by deploying new code (with new model fields)
    without running `python manage.py migrate` on the server.
    """
    _done = False
    _lock = threading.Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not AutoMigrateMiddleware._done:
            with AutoMigrateMiddleware._lock:
                if not AutoMigrateMiddleware._done:
                    self._migrate_if_needed()
                    AutoMigrateMiddleware._done = True
        return self.get_response(request)

    @staticmethod
    def _migrate_if_needed():
        try:
            from django.db import connection
            from django.db.migrations.executor import MigrationExecutor
            from django.core.management import call_command

            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if plan:
                logger.warning("Applying %d pending migration(s) automatically...", len(plan))
                call_command('migrate', interactive=False, verbosity=0)
                logger.warning("Pending migrations applied.")
        except Exception:
            logger.exception("Automatic migration failed")


class AdminLogoutMiddleware:
    """Log out any authenticated user when they access the admin URLs.
    This forces the admin login page to appear on every visit.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the request is for the admin site and the user is logged in, log them out
        # If the request is for the admin site and the user is logged in but not staff, log them out
        if request.path.startswith('/khkhkhkhk/') and request.user.is_authenticated and not request.user.is_staff:
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

