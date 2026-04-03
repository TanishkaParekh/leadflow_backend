from django.db.models import Sum
from django.utils import timezone
from leads.models import Invoice, Payment

def get_monthly_financial_report(month=None, year=None):
    """
    Summarizes all financial activity for a specific month.
    """
    now = timezone.now()
    # Convert string params to int, or default to current date
    try:
        month = int(month) if month else now.month
        year = int(year) if year else now.year
    except (ValueError, TypeError):
        month, year = now.month, now.year

    # 1. Filter Invoices and Payments for the period
    monthly_invoices = Invoice.objects.filter(created_at__month=month, created_at__year=year)
    monthly_payments = Payment.objects.filter(payment_date__month=month, payment_date__year=year)

    # 2. Build the dataset
    return {
        "period": f"{year}-{month:02d}",
        "invoices": {
            "total_count": monthly_invoices.count(),
            "total_value": float(monthly_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            "paid_count": monthly_invoices.filter(status='paid').count(),
            "overdue_count": monthly_invoices.filter(status='overdue').count(),
        },
        "payments": {
            "total_collected": float(monthly_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0),
            "transaction_count": monthly_payments.count(),
        }
    }