from django.urls import path
from .views import pipeline_view,update_deal_stage,close_deal

urlpatterns=[
    path("pipeline/",pipeline_view),
    path("pipeline/update/<int:deal_id>/",update_deal_stage),
    path("pipeline/close/<int:deal_id>/",close_deal),
]