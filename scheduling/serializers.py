from rest_framework import serializers
from .models import CalendarEvent, User

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class CalendarEventSerializer(serializers.ModelSerializer):
    attendees = AttendeeSerializer(many=True, read_only=True)
    attendee_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, source='attendees'
    )

    class Meta:
        model = CalendarEvent
        fields = '__all__'