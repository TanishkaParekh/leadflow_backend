from django.db.models import Sum
from leads.models import Invoice # Import from the other app

def get_invoice_dashboard_stats():
    """
    Business logic to calculate the dashboard stats.
    Returns a dictionary of raw data.
    """
    # 1. Aggregations
    total_invoiced = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    paid_total = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_total = Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    overdue_total = Invoice.objects.filter(status='overdue').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # 2. Count for the "Critical" badge
    overdue_count = Invoice.objects.filter(status='overdue').count()

    return {
        "total_invoiced": float(total_invoiced),
        "paid_amount": float(paid_total),
        "pending_amount": float(pending_total),
        "overdue_amount": float(overdue_total),
        "overdue_count": overdue_count,
    }