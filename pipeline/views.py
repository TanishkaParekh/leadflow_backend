from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum

from .models import Deal,PipelineStage
from .serializers import DealSerializer
# Create your views here.

@api_view(['GET']) #pipeline view  
def pipeline_view(request):
    user=request.user

    if user.role.name=="Sales Rep":
        deals=Deal.objects.filter(lead_assigned_to=user)

    elif user.role.name=="Sales Manager":
        deals=Deal.objects.filter(lead_assigned_to=user.team)

    else:#admin
        deals=Deal.objects.all()
    
    stages=PipelineStage.objects.all().order_by("order")

    pipeline_data=[]

    for stage in stages:
        stage_deals=deals.filter(
            stage=stage,
            is_won=False,
            is_lost=False,
        )

        serializer=DealSerializer(stage_deals,many=True)
        total_value=stage_deals.aggregate(
            total=Sum("deal_value")
        )["total"] or 0

        pipeline_data.append({
            "stage_id":stage.id,
            "stage_name":stage.name,
            "count":stage_deals.count(),
            "total_value":total_value,
            "deals":serializer.data,
        })
    #closed and lost deals for separate display  
    closed_deals=deals.filter(is_won=True)
    lost_deals=deals.filter(is_lost=True)

    return Response({
        "pipeline":pipeline_data,
        "closed_deals":DealSerializer(closed_deals,many=True).data,
        "lost_deals":DealSerializer(lost_deals,many=True).data,
    })

@api_view(['PATCH']) #update deal (DRAG AND DROP)
def update_deal_stage(request,deal_id):
    try:
        deal=Deal.objects.get(id=deal_id)
    except Deal.DoesNotExist:
        return Response({"error":"Deal not found"},status=404)
    
    stage_id=request.data.get("stage_id")
    try:
        stage=PipelineStage.objects.get(id=stage_id)
    except PipelineStage.DoesNotExist:
        return Response({"error":"Pipeline stage not found"},status=404)
    
    deal.stage=stage
    deal.is_won=False
    deal.is_lost=False
    deal.save()

    return Response({"message":"Deal stage updated successfully"})

@api_view(['PATCH']) #mark deal as won/lost
def close_deal(request,deal_id):
    try:
        deal=Deal.objects.get(id=deal_id)
    except Deal.DoesNotExist:
        return Response({"error":"Deal not found"},status=404)
    
    status=request.data.get("status")
    if status=="won":
        deal.is_won=True
        deal.is_lost=False
    elif status=="lost":
        deal.is_won=False
        deal.is_lost=True
    else:
        return Response({"error":"Invalid status"},status=400)
    
    deal.save()
    return Response({"message":"Deal status updated successfully"})