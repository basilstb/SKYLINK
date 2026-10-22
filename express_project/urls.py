from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('khkhkhkhk/', admin.site.urls),
    path('', include('tracking.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
