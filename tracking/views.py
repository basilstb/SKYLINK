from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Shipment, TrackingEvent
from .geocoding import resolve_coordinates

def index(request):
    return render(request, 'index.html')

def get_shipment_by_id(tracking_id):
    """Helper to look up shipment with 0/O typo tolerance."""
    if not tracking_id:
        return None
    tid = tracking_id.strip()
    shipment = Shipment.objects.filter(tracking_number__iexact=tid).first()
    if not shipment and ('O' in tid.upper() or '0' in tid):
        alt_zero = tid.upper().replace('O', '0')
        shipment = Shipment.objects.filter(tracking_number__iexact=alt_zero).first()
        if not shipment:
            alt_o = tid.upper().replace('0', 'O')
            shipment = Shipment.objects.filter(tracking_number__iexact=alt_o).first()
    return shipment

def tracking(request):
    raw_id = request.GET.get('id')
    tracking_id = raw_id.strip() if raw_id else None
    shipment = get_shipment_by_id(tracking_id)
    return render(request, 'tracking.html', {'shipment': shipment, 'tracking_id': tracking_id})

def api_shipment_live(request, tracking_id):
    """
    Real-time Live Tracking API Endpoint.
    Returns live coordinates, status, route waypoints, and event history.
    100% compatible with PythonAnywhere free tier via HTTP polling.
    """
    shipment = get_shipment_by_id(tracking_id)
    if not shipment:
        return JsonResponse({'success': False, 'error': 'Shipment not found'}, status=404)

    # Resolve coordinates
    origin_lat, origin_lng = shipment.get_origin_coords()
    dest_lat, dest_lng = shipment.get_destination_coords()
    curr_lat, curr_lng = shipment.get_current_coords()

    # Calculate status percentage
    progress_map = {
        'label_created': 15,
        'Label Created': 15,
        'package_received': 25,
        'Package Received': 25,
        'in_transit': 55,
        'In Transit': 55,
        'departed_facility': 65,
        'Departed Facility': 65,
        'arrived': 85,
        'Arrived at Facility': 85,
        'out_for_delivery': 92,
        'Out for Delivery': 92,
        'delivered': 100,
        'Delivered': 100,
        'exception': 40,
        'Delayed': 40,
    }
    progress_percent = progress_map.get(shipment.status, progress_map.get(shipment.status.lower().replace(' ', '_'), 50))

    # Build history events with coordinates
    events_data = []
    events = shipment.history.all()
    for ev in events:
        ev_lat = ev.latitude
        ev_lng = ev.longitude
        if ev_lat is None or ev_lng is None:
            ev_lat, ev_lng = resolve_coordinates(ev.location)
        events_data.append({
            'status': ev.status,
            'location': ev.location,
            'timestamp': ev.timestamp.strftime("%b %d, %Y - %H:%M"),
            'lat': ev_lat,
            'lng': ev_lng,
        })

    latest_loc = shipment.current_location_name or (events[0].location if events else f"{shipment.sender_city}, {shipment.sender_country}")

    data = {
        'success': True,
        'tracking_number': shipment.tracking_number,
        'status': shipment.status,
        'status_display': shipment.get_status_display() if hasattr(shipment, 'get_status_display') else shipment.status,
        'progress_percent': progress_percent,
        'current_location': latest_loc,
        'current_coords': {
            'lat': curr_lat,
            'lng': curr_lng,
        },
        'origin': {
            'name': shipment.sender_name,
            'city': shipment.sender_city,
            'country': shipment.sender_country,
            'lat': origin_lat,
            'lng': origin_lng,
        },
        'destination': {
            'name': shipment.receiver_name,
            'address': shipment.receiver_address,
            'phone': shipment.receiver_phone,
            'lat': dest_lat,
            'lng': dest_lng,
        },
        'dates': {
            'registered': shipment.registered_date.strftime("%b %d, %Y") if shipment.registered_date else None,
            'departure': shipment.departure_date.strftime("%b %d, %Y") if shipment.departure_date else None,
            'arrival': shipment.arrival_date.strftime("%b %d, %Y") if shipment.arrival_date else None,
        },
        'events': events_data,
        'last_updated': timezone.now().strftime("%H:%M:%S UTC"),
    }
    return JsonResponse(data)

@login_required
def dashboard(request):
    shipments = Shipment.objects.all().order_by('-registered_date')
    return render(request, 'dashboard.html', {'shipments': shipments})

@login_required
def create_shipment(request):
    if request.method == 'POST':
        tracking_number = (request.POST.get('tracking_number') or '').strip().upper()
        sender_name = request.POST.get('sender_name')
        sender_country = request.POST.get('sender_country')
        sender_city = request.POST.get('sender_city')
        receiver_name = request.POST.get('receiver_name')
        receiver_address = request.POST.get('receiver_address')
        receiver_phone = request.POST.get('receiver_phone')
        registered_date = request.POST.get('registered_date')
        departure_date = request.POST.get('departure_date') or None
        arrival_date = request.POST.get('arrival_date') or None
        status = request.POST.get('status')
        location = request.POST.get('location')

        # Auto-resolve coordinates if not explicitly provided
        orig_lat, orig_lng = resolve_coordinates(f"{sender_city}, {sender_country}", sender_country)
        dest_lat, dest_lng = resolve_coordinates(receiver_address)
        curr_lat, curr_lng = resolve_coordinates(location)

        # Allow manual coordinate override if supplied in POST
        if request.POST.get('current_latitude') and request.POST.get('current_longitude'):
            try:
                curr_lat = float(request.POST.get('current_latitude'))
                curr_lng = float(request.POST.get('current_longitude'))
            except (ValueError, TypeError):
                pass

        shipment = Shipment.objects.create(
            tracking_number=tracking_number,
            sender_name=sender_name,
            sender_country=sender_country,
            sender_city=sender_city,
            receiver_name=receiver_name,
            receiver_address=receiver_address,
            receiver_phone=receiver_phone,
            registered_date=registered_date,
            departure_date=departure_date,
            arrival_date=arrival_date,
            status=status,
            origin_latitude=orig_lat,
            origin_longitude=orig_lng,
            destination_latitude=dest_lat,
            destination_longitude=dest_lng,
            current_latitude=curr_lat,
            current_longitude=curr_lng,
            current_location_name=location,
        )
        
        TrackingEvent.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            latitude=curr_lat,
            longitude=curr_lng,
            timestamp=timezone.now()
        )
        messages.success(request, f'Shipment {tracking_number} created with live GPS tracking.')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def update_status(request):
    if request.method == 'POST':
        tracking_number = (request.POST.get('tracking_number') or '').strip()
        status = request.POST.get('status')
        location = request.POST.get('location')
        custom_date = request.POST.get('custom_date')

        # Coordinates handling
        curr_lat, curr_lng = resolve_coordinates(location)
        if request.POST.get('latitude') and request.POST.get('longitude'):
            try:
                curr_lat = float(request.POST.get('latitude'))
                curr_lng = float(request.POST.get('longitude'))
            except (ValueError, TypeError):
                pass

        shipment = get_shipment_by_id(tracking_number)
        if shipment:
            shipment.status = status
            shipment.current_latitude = curr_lat
            shipment.current_longitude = curr_lng
            shipment.current_location_name = location
            shipment.save()

            event = TrackingEvent(
                shipment=shipment,
                status=status,
                location=location,
                latitude=curr_lat,
                longitude=curr_lng
            )
            if custom_date:
                event.timestamp = custom_date
            event.save()
            
            messages.success(request, f'Shipment {shipment.tracking_number} updated to {status} at {location}.')
        else:
            messages.error(request, f'Shipment {tracking_number} not found.')
            
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def api_update_coordinates(request):
    """Fast AJAX endpoint for updating coordinates directly from dashboard."""
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        location_name = request.POST.get('location_name', '')
        status = request.POST.get('status')

        shipment = get_shipment_by_id(tracking_number)
        if not shipment:
            return JsonResponse({'success': False, 'error': 'Shipment not found'}, status=404)

        try:
            shipment.current_latitude = float(lat)
            shipment.current_longitude = float(lng)
            if location_name:
                shipment.current_location_name = location_name
            if status:
                shipment.status = status
            shipment.save()

            # Record event
            TrackingEvent.objects.create(
                shipment=shipment,
                status=status or shipment.status,
                location=location_name or f"GPS: {lat}, {lng}",
                latitude=shipment.current_latitude,
                longitude=shipment.current_longitude,
                timestamp=timezone.now()
            )
            return JsonResponse({'success': True, 'message': 'Coordinates updated successfully'})
        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
