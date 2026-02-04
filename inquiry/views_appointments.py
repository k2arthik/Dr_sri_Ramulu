from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from utils.dynamodb import save_appointment_to_dynamodb

@require_http_methods(['GET'])
def appointment_view(request):
    from utils.dynamodb import fetch_taken_slots
    import datetime

    # Services list
    services = ["General Checkup", "Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics", "Dental Care"]
    
    # Selected date (default to today)
    selected_date_str = request.GET.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except:
        selected_date = datetime.datetime.now().date()
        selected_date_str = selected_date.isoformat()

    now = datetime.datetime.now()
    is_today = selected_date == now.date()

    # Generate Slots
    all_slots = []
    for h in range(10, 22): # 10 AM to 9 PM
        for m in [30] if h == 10 else [0, 30]:
            if h == 21 and m > 30: continue
            
            period = "AM" if h < 12 else "PM"
            display_h = h if h <= 12 else h - 12
            time_str = f"{display_h}:{m:02d} {period}"
            
            # Filter past slots if today
            if is_today:
                slot_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if slot_time <= now:
                    continue
            
            all_slots.append(time_str)

    # Fetch Taken Slots from DynamoDB
    taken_raw = fetch_taken_slots(selected_date_str)
    # taken_raw contains "10:30AM" type strings. We need to match with template format "10:30 AM"
    taken_slots = []
    for t in taken_raw:
        # Simple cleanup: Ensure space before AM/PM
        t_clean = t.replace('AM', ' AM').replace('PM', ' PM').strip()
        taken_slots.append(t_clean)

    return render(request, 'html/appointments.html', {
        'services': services,
        'time_slots': all_slots,
        'taken_slots': taken_slots,
        'selected_date': selected_date_str,
        'today': now.strftime('%Y-%m-%d')
    })

@require_http_methods(['POST'])
def appointment_api_view(request):
    data = request.POST
    
    # Validate required fields
    required = ['name', 'email', 'phone', 'service', 'date', 'time_slot']
    for field in required:
        if not data.get(field):
             return JsonResponse({'error': f'Missing field: {field}'}, status=400)

    try:
        # Save to DynamoDB (Atomic Collision Check included inside save_appointment_to_dynamodb)
        from utils.dynamodb import save_appointment_to_dynamodb
        saved_item = save_appointment_to_dynamodb(data)
        
        # Send Emails
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # To Patient
            msg_patient = f"Dear {data['name']},\n\nYour appointment for {data['service']} on {data['date']} at {data['time_slot']} has been requested and is pending confirmation.\nID: {saved_item['id']}"
            send_mail(f"Appointment Requested: {saved_item['id']}", msg_patient, settings.DEFAULT_FROM_EMAIL, [data['email']], fail_silently=True)

            # To Admin
            msg_admin = f"New Appointment Request:\nID: {saved_item['id']}\nName: {data['name']}\nService: {data['service']}\nDate: {data['date']}\nSlot: {data['time_slot']}\nPhone: {data['phone']}"
            send_mail(f"NEW APPOINTMENT: {saved_item['id']}", msg_admin, settings.DEFAULT_FROM_EMAIL, ['g12113251a@gmail.com'], fail_silently=True)
        except Exception as e:
            print(f"Mail Error: {e}")

        return JsonResponse({'success': True, 'id': saved_item['id']})
    
    except Exception as e:
        # Catch collision or other logic errors
        return JsonResponse({'error': str(e)}, status=400)
