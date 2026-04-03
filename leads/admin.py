from django.contrib import admin
from .models import (
    Role, Team, User, LeadSource, Lead, FollowUp
)

admin.site.register(Role)
admin.site.register(Team)
admin.site.register(User)
admin.site.register(LeadSource)
admin.site.register(Lead)
admin.site.register(FollowUp)