from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CalendarEvent, User
import json


@csrf_exempt
@require_http_methods(["GET", "POST"])
def calendar_list_create(request):

    # List all events
    if request.method == "GET":
        events = CalendarEvent.objects.all().order_by('start_time')
        data = []
        for event in events:
            data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "event_type": event.event_type,
                "location": event.location,
                "meeting_link": event.meeting_link,
                "user": event.user_id,
                "attendees": [
                    {
                        "id": a.id,
                        "first_name": a.first_name,
                        "last_name": a.last_name,
                        "email": a.email,
                    }
                    for a in event.attendees.all()
                ],
                "lead": event.lead_id,
                "deal": event.deal_id,
            })
        return JsonResponse(data, safe=False, status=200)

    # Create event
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            # Validate required fields
            required_fields = ['title', 'start_time', 'end_time', 'event_type', 'user']
            missing = [f for f in required_fields if not body.get(f)]
            if missing:
                return JsonResponse({"error": f"Missing required fields: {missing}"}, status=400)

            user = User.objects.get(id=body.get('user'))

            event = CalendarEvent.objects.create(
                title=body.get('title'),
                description=body.get('description', ''),
                start_time=body.get('start_time'),
                end_time=body.get('end_time'),
                event_type=body.get('event_type'),
                location=body.get('location', ''),
                meeting_link=body.get('meeting_link', ''),
                user=user,
                lead_id=body.get('lead'),
                deal_id=body.get('deal'),
            )

            # Add attendees
            attendee_ids = body.get('attendee_ids', [])
            if attendee_ids:
                event.attendees.set(attendee_ids)

            return JsonResponse({
                "id": event.id,
                "title": event.title,
                "message": "Event created successfully"
            }, status=201)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def calendar_detail(request, pk):

    # Get event
    try:
        event = CalendarEvent.objects.get(pk=pk)
    except CalendarEvent.DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)

    # Get single event
    if request.method == "GET":
        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "event_type": event.event_type,
            "location": event.location,
            "meeting_link": event.meeting_link,
            "user": event.user_id,
            "attendees": [
                {
                    "id": a.id,
                    "first_name": a.first_name,
                    "last_name": a.last_name,
                    "email": a.email,
                }
                for a in event.attendees.all()
            ],
            "lead": event.lead_id,
            "deal": event.deal_id,
        }, status=200)

    # Edit event
    if request.method == "PATCH":
        try:
            body = json.loads(request.body)

            event.title = body.get('title', event.title)
            event.description = body.get('description', event.description)
            event.start_time = body.get('start_time', event.start_time)
            event.end_time = body.get('end_time', event.end_time)
            event.event_type = body.get('event_type', event.event_type)
            event.location = body.get('location', event.location)
            event.meeting_link = body.get('meeting_link', event.meeting_link)
            event.lead_id = body.get('lead', event.lead_id)
            event.deal_id = body.get('deal', event.deal_id)
            event.save()

            # Update attendees if provided
            attendee_ids = body.get('attendee_ids')
            if attendee_ids is not None:
                event.attendees.set(attendee_ids)

            return JsonResponse({
                "id": event.id,
                "title": event.title,
                "message": "Event updated successfully"
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # Delete event
    if request.method == "DELETE":
        event.delete()
        return JsonResponse({}, status=204)