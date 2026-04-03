# reports/serializers.py

from rest_framework import serializers

class ExecutivePerformanceSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_leads = serializers.IntegerField()
    conversions = serializers.IntegerField()
    conversion_rate = serializers.FloatField()