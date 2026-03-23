from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_list_create, name='calendar-list-create'),
    path('calendar/<int:pk>/', views.calendar_detail, name='calendar-detail'),
]