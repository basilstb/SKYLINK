from django.db import models
from django.utils import timezone
from django.conf import settings

class Shipment(models.Model):
    tracking_number = models.CharField(max_length=50, primary_key=True)
    
    # Sender Details
    sender_name = models.CharField(max_length=255)
    sender_country = models.CharField(max_length=100)
    sender_city = models.CharField(max_length=100)
    
    # Receiver Details
    receiver_name = models.CharField(max_length=255)
    receiver_address = models.TextField()
    receiver_phone = models.CharField(max_length=50)
    
    # Dates
    registered_date = models.DateField(default=timezone.now)
    departure_date = models.DateField(null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True)
    
    # Current Status
    STATUS_CHOICES = [
        ('label_created', 'Label Created'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('delivered', 'Delivered'),
        ('exception', 'Exception'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='label_created')
    
    # Real-Time GPS & Live Tracking Coordinates
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    current_location_name = models.CharField(max_length=255, null=True, blank=True)
    origin_latitude = models.FloatField(null=True, blank=True)
    origin_longitude = models.FloatField(null=True, blank=True)
    destination_latitude = models.FloatField(null=True, blank=True)
    destination_longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.tracking_number

    def get_origin_coords(self):
        if self.origin_latitude is not None and self.origin_longitude is not None:
            return (self.origin_latitude, self.origin_longitude)
        from .geocoding import resolve_coordinates
        return resolve_coordinates(f"{self.sender_city}, {self.sender_country}")

    def get_destination_coords(self):
        if self.destination_latitude is not None and self.destination_longitude is not None:
            return (self.destination_latitude, self.destination_longitude)
        from .geocoding import resolve_coordinates
        return resolve_coordinates(self.receiver_address)

    def get_current_coords(self):
        # 1. If explicit current coords are set
        if self.current_latitude is not None and self.current_longitude is not None:
            return (self.current_latitude, self.current_longitude)
        # 2. Check latest event
        latest_event = self.history.first()
        if latest_event and latest_event.latitude is not None and latest_event.longitude is not None:
            return (latest_event.latitude, latest_event.longitude)
        if latest_event and latest_event.location:
            from .geocoding import resolve_coordinates
            return resolve_coordinates(latest_event.location)
        # 3. Fallback based on status
        if self.status == 'delivered':
            return self.get_destination_coords()
        return self.get_origin_coords()

class TrackingEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"

# New model to store admin login events
class LoginLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
