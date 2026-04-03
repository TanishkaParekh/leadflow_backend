from django.urls import path
from .views import MonthlyReportAPIView

urlpatterns = [
    # Endpoint: /api/invoices/monthly-report/
    path('monthly-report/', MonthlyReportAPIView.as_view(), name='monthly-report'),
]