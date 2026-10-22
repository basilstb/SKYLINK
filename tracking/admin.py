from django.contrib import admin
from .models import Shipment, TrackingEvent, LoginLog
from django.contrib.auth.models import User, Group

# Unregister default auth models to simplify admin UI
admin.site.unregister(User)
admin.site.unregister(Group)

# Customize admin site titles
admin.site.site_header = "Delivery Site Administration"
admin.site.site_title = "Delivery Site Admin"
admin.site.index_title = "Tracking Management"

# Admin actions to bulk update shipment status
def make_in_transit(modeladmin, request, queryset):
    queryset.update(status='in_transit')
make_in_transit.short_description = "Mark selected shipments as In Transit"

def make_arrived(modeladmin, request, queryset):
    queryset.update(status='arrived')
make_arrived.short_description = "Mark selected shipments as Arrived"

def make_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')
make_delivered.short_description = "Mark selected shipments as Delivered"

def make_exception(modeladmin, request, queryset):
    queryset.update(status='exception')
make_exception.short_description = "Mark selected shipments as Exception"

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    actions = [make_in_transit, make_arrived, make_delivered, make_exception]
    list_display = ('tracking_number', 'sender_name', 'receiver_name', 'status', 'registered_date')
    search_fields = ('tracking_number', 'sender_name', 'receiver_name')
    list_filter = ('status',)

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'status', 'location')

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address')
    list_filter = ('login_time',)
    search_fields = ('user__username', 'ip_address')
