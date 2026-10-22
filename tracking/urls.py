from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tracking/', views.tracking, name='tracking'),
    path('tracking.html', views.tracking, name='tracking_html'),
    path('tracking', views.tracking),
    path('api/track/<str:tracking_id>/', views.api_shipment_live, name='api_shipment_live'),
    path('api/update-coordinates/', views.api_update_coordinates, name='api_update_coordinates'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/change-password/', views.change_password, name='change_password'),
    path('dashboard/create/', views.create_shipment, name='create_shipment'),
    path('dashboard/update/', views.update_status, name='update_status'),
]
