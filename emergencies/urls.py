from django.urls import path
from .views import (
    CreateEmergencyReportView,
    CreateMissingReportView,
    ReportListView,
    GroupedReportsByReporterView,
    ReportDetailView,
    UpdateReportStatusView,
    ListPilgrimsWithStatusView, SendMessageNotificationView, MyReportsView,
)

urlpatterns = [
    path('emergency/create-report/', CreateEmergencyReportView.as_view(), name='create-emergency-report'),
    path('missing/create-report/', CreateMissingReportView.as_view(), name='create-missing-report'),

    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/grouped/', GroupedReportsByReporterView.as_view(), name='grouped-reports'),

    path('report/detail/', ReportDetailView.as_view(), name='report-detail'),

    path('report/edit-status/', UpdateReportStatusView.as_view(), name='update-report-status'),
    path('reports/pilgrim-report/', MyReportsView.as_view(), name='get-pilgrim-report'),
    path('notify-user/', SendMessageNotificationView.as_view(), name='notify-user'),

    # قائمة الحجاج وحالاتهم (آمن / بلاغ طارئ / مفقود)
    path('pilgrims/status/', ListPilgrimsWithStatusView.as_view(), name='pilgrims-status'),
]
