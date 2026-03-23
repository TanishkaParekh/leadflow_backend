from django.db import models
from django.contrib.auth.hashers import make_password


# Role
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Team
class Team(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# User
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)

    password = models.CharField(max_length=255)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members'
    )

    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members'
    )

    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# LeadSource
class LeadSource(models.Model):
    name = models.CharField(max_length=100)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


# Lead
class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('lost', 'Lost'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)

    company = models.CharField(max_length=255, blank=True)

    source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True)

    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assigned_leads'
    )

    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# FollowUp
class FollowUp(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('missed', 'Missed'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    followup_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    notes = models.TextField(blank=True)

    reminder_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FollowUp for {self.lead}"


# PipelineStage
class PipelineStage(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField()
    probability_percent = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# Deal
class Deal(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    deal_value = models.DecimalField(max_digits=12, decimal_places=2)

    stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True)

    expected_close_date = models.DateField(null=True, blank=True)

    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Invoice
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    deal = models.ForeignKey(Deal, on_delete=models.CASCADE)

    invoice_number = models.CharField(max_length=100, unique=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    due_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


# Payment
class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)

    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255)

    payment_date = models.DateTimeField()

    is_partial = models.BooleanField(default=False)

    def __str__(self):
        return self.transaction_id


# CalendarEvent
class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('reminder', 'Reminder'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)

    location = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(blank=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_events'
    )
    attendees = models.ManyToManyField(
        User, blank=True, related_name='attending_events'
    )

    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


# Notification
class Notification(models.Model):
    TYPE_CHOICES = [
        ('followup', 'Follow-up'),
        ('payment', 'Payment'),
        ('assignment', 'Assignment'),
        ('discount', 'Discount'),
    ]

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_notifications'
    )

    message = models.TextField()

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.receiver}"


# Report
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('revenue', 'Revenue'),
        ('leads', 'Leads'),
        ('performance', 'Performance'),
    ]

    name = models.CharField(max_length=255)

    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    filters = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name