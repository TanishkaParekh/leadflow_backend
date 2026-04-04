from rest_framework import serializers
from .models import Deal

class DealSerializer(serializers.ModelSerializer):
    lead_name = serializers.SerializerMethodField()
    company = serializers.CharField(source='lead.company')

    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'deal_value',
            'stage',
            'lead_name',
            'company',
            'is_won',
            'is_lost'
        ]

    def get_lead_name(self, obj):
        if obj.lead:
            return f"{obj.lead.first_name} {obj.lead.last_name}"
        return None