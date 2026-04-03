from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Sum
from rest_framework_simplejwt.authentication import JWTAuthentication

from leads.models import Lead, User
from pipeline.models import Deal
from .serializers import ExecutivePerformanceSerializer


@api_view(["GET"])
def reports_dashboard(request):
    # Extract user from JWT (FIX)
    try:
        jwt_auth = JWTAuthentication()
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response({"error": "Authorization header missing"}, status=401)

        token = auth_header.split()[1]
        validated_token = jwt_auth.get_validated_token(token)

        user_id = validated_token.get("user_id")
        user = User.objects.get(id=user_id)

    except Exception as e:
        return Response({"error": f"Authentication failed: {str(e)}"}, status=401)

    # 🔹 Role-based filtering (NOW WORKS)
    if user.role and user.role.name == "Sales Rep":
        leads = Lead.objects.filter(assigned_to=user)
        deals = Deal.objects.filter(lead__assigned_to=user)
    else:
        leads = Lead.objects.filter(team__manager=user)
        deals = Deal.objects.filter(lead__team__manager=user)

    # 🔹 Summary
    total_revenue = deals.filter(is_won=True).aggregate(
        total=Sum("deal_value")
    )["total"] or 0

    active_leads = leads.count()

    converted = deals.filter(is_won=True).count()
    conversion_rate = (converted / active_leads * 100) if active_leads > 0 else 0

    # 🔹 Monthly revenue
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

    # 🔹 Lead source performance
    source_data = leads.values("source__name").annotate(count=Count("id"))
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

    # 🔹 Executive performance
    executives = []
    users = leads.values("assigned_to").distinct()

    for u in users:
        user_leads = leads.filter(assigned_to=u["assigned_to"])
        user_deals = deals.filter(
            lead__assigned_to=u["assigned_to"],
            is_won=True
        )

        total = user_leads.count()
        conversions = user_deals.count()

        rate = (conversions / total * 100) if total > 0 else 0

        first_lead = user_leads.first()

        executives.append({
            "name": first_lead.assigned_to.first_name if first_lead else "Unknown",
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