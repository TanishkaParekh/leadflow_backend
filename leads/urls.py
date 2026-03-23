from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('calendar/', views.calendar_list_create, name='calendar-list-create'),
    path('calendar/<int:pk>/', views.calendar_detail, name='calendar-detail'),

        # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/signup/', auth_views.signup, name='auth-signup'),
    path('auth/login/',  auth_views.login,  name='auth-login'),
    path('auth/logout/', auth_views.logout, name='auth-logout'),
]