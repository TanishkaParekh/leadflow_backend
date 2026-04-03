# reports/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Sum
from datetime import datetime

from leads.models import Lead
from pipeline.models import Deal
from .serializers import ExecutivePerformanceSerializer


@api_view(["GET"])
def reports_dashboard(request):
    user = request.user

    # 🔹 Role-based filtering
    if user.role.name == "Sales Rep":
        leads = Lead.objects.filter(assigned_to=user)
        deals = Deal.objects.filter(lead__assigned_to=user)
    else:
        leads = Lead.objects.filter(team__manager=user)
        deals = Deal.objects.filter(lead__team__manager=user)

    
       
    total_revenue = deals.filter(is_won=True).aggregate(
        total=Sum("deal_value")
    )["total"] or 0

    active_leads = leads.count()

    converted = deals.filter(is_won=True).count()
    conversion_rate = (converted / active_leads * 100) if active_leads > 0 else 0

    
    # REVENUE TREND (Monthly)
    
    monthly_data = []

    for month in range(1, 13):
        month_revenue = deals.filter(
            is_won=True,
            created_at__month=month
        ).aggregate(total=Sum("deal_value"))["total"] or 0

        monthly_data.append({
            "month": month,
            "revenue": month_revenue
        })


    #  LEAD SOURCE PERFORMANCE

    source_data = leads.values("source__name").annotate(
        count=Count("id")
    )

    total_leads_count = leads.count()

    lead_sources = []
    for src in source_data:
        percentage = (
            src["count"] / total_leads_count * 100
            if total_leads_count > 0 else 0
        )

        lead_sources.append({
            "source": src["source__name"] or "Unknown",
            "percentage": round(percentage, 2)
        })

    
    # CONVERSION BY EXECUTIVE
   
    executives = []

    users = leads.values("assigned_to").distinct()

    for u in users:
        user_leads = leads.filter(assigned_to=u["assigned_to"])
        user_deals = deals.filter(lead__assigned_to=u["assigned_to"], is_won=True)

        total = user_leads.count()
        conversions = user_deals.count()

        rate = (conversions / total * 100) if total > 0 else 0

        executives.append({
            "name": user_leads.first().assigned_to.first_name,
            "total_leads": total,
            "conversions": conversions,
            "conversion_rate": round(rate, 2)
        })

    return Response({
        "summary": {
            "total_revenue": total_revenue,
            "active_leads": active_leads,
            "conversion_rate": round(conversion_rate, 2)
        },
        "revenue_trend": monthly_data,
        "lead_sources": lead_sources,
        "executive_performance": ExecutivePerformanceSerializer(executives, many=True).data
    })

















# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.db.models import Count, Sum
# from django.contrib.auth import get_user_model

# from leads.models import Lead
# from pipeline.models import Deal
# from .serializers import ExecutivePerformanceSerializer

# User = get_user_model()


# @api_view(["GET"])
# def reports_dashboard(request):
#     user = User.objects.get(username="coco")  # your admin user

#     # TEMP: use superuser instead of role
#     if user.is_superuser:
#         leads = Lead.objects.all()
#         deals = Deal.objects.all()
#     else:
#         leads = Lead.objects.filter(assigned_to=user)
#         deals = Deal.objects.filter(lead__assigned_to=user)

#     # -------------------------------
#     # TOTAL REVENUE
#     # -------------------------------
#     total_revenue = deals.filter(is_won=True).aggregate(
#         total=Sum("deal_value")
#     )["total"] or 0

#     # -------------------------------
#     # ACTIVE LEADS
#     # -------------------------------
#     active_leads = leads.count()

#     # -------------------------------
#     #  CONVERSION RATE
#     # -------------------------------
#     converted = deals.filter(is_won=True).count()
#     conversion_rate = (converted / active_leads * 100) if active_leads > 0 else 0

#     # -------------------------------
#     #  REVENUE TREND (Monthly)
#     # -------------------------------
#     monthly_data = []

#     for month in range(1, 13):
#         month_revenue = deals.filter(
#             is_won=True,
#             created_at__month=month
#         ).aggregate(total=Sum("deal_value"))["total"] or 0

#         monthly_data.append({
#             "month": month,
#             "revenue": month_revenue
#         })

#     # -------------------------------
#     #  LEAD SOURCE PERFORMANCE
#     # -------------------------------
#     source_data = leads.values("source__name").annotate(
#         count=Count("id")
#     )

#     total_leads_count = leads.count()

#     lead_sources = []
#     for src in source_data:
#         percentage = (
#             src["count"] / total_leads_count * 100
#             if total_leads_count > 0 else 0
#         )

#         lead_sources.append({
#             "source": src["source__name"] or "Unknown",
#             "percentage": round(percentage, 2)
#         })

#     # -------------------------------
#     #  CONVERSION BY EXECUTIVE
#     # -------------------------------
#     executives = []

#     users = leads.values("assigned_to").distinct()

#     for u in users:
#         user_leads = leads.filter(assigned_to=u["assigned_to"])
#         user_deals = deals.filter(
#             lead__assigned_to=u["assigned_to"],
#             is_won=True
#         )

#         total = user_leads.count()
#         conversions = user_deals.count()

#         rate = (conversions / total * 100) if total > 0 else 0

#         first_lead = user_leads.first()

#         executives.append({
#             "name": first_lead.assigned_to.first_name if first_lead else "Unknown",
#             "total_leads": total,
#             "conversions": conversions,
#             "conversion_rate": round(rate, 2)
#         })

#     return Response({
#         "summary": {
#             "total_revenue": total_revenue,
#             "active_leads": active_leads,
#             "conversion_rate": round(conversion_rate, 2)
#         },
#         "revenue_trend": monthly_data,
#         "lead_sources": lead_sources,
#         "executive_performance": ExecutivePerformanceSerializer(executives, many=True).data
#     })