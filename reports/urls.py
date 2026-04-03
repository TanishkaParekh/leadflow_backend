# reports/urls.py

from django.urls import path
from .views import reports_dashboard

urlpatterns = [
    path("dashboard/", reports_dashboard),
]