from django.db import models
from users.models import User


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('EMERGENCY', 'Emergency Report'),  # بلاغ حاج
        ('MISSING', 'Missing Report'),      # بلاغ مفقود
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_status_display()}"


class EmergencyReport(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='emergency_details')
    pilgrim = models.ForeignKey(User, on_delete=models.CASCADE)
    report_reason = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Emergency report for {self.pilgrim.first_name}"


class MissingReport(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='missing_details')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    missing_name = models.CharField(max_length=255, blank=True, null=True)
    missing_health_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    last_seen_location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='missing_reports/', blank=True, null=True)

    def __str__(self):
        return f"Missing report: {self.missing_name or 'Unnamed'}"
