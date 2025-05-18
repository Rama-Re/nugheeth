from rest_framework import status
from .models import Report, EmergencyReport, MissingReport
from users.models import User
from .serializers import EmergencyReportCreateSerializer, MissingReportCreateSerializer
from global_services.firebase.notifications import send_fcm_notification
from global_services.googleMap.directions import get_directions
from django.shortcuts import get_object_or_404
from .serializers import ReportListSerializer
from users.permissions import IsAdmin, IsEmergency, IsPilgrim
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from collections import defaultdict
import requests


class CreateEmergencyReportView(APIView):
    permission_classes = [IsAuthenticated, IsPilgrim]

    def post(self, request):
        serializer = EmergencyReportCreateSerializer(data=request.data)
        if serializer.is_valid():
            report = Report.objects.create(report_type='EMERGENCY')
            EmergencyReport.objects.create(
                report=report,
                pilgrim=request.user,
                report_reason=serializer.validated_data['report_reason'],
                location=serializer.validated_data['location']
            )

            recipients = User.objects.filter(account_type__in=['emergency', 'admin']).exclude(fcm_token=None)
            tokens = [user.fcm_token for user in recipients if user.fcm_token]
            send_fcm_notification(
                tokens=tokens,
                title=f"🚨 بلاغ طارئ من {request.user.get_full_name()}",
                body=f"السبب: {serializer.validated_data['report_reason']}"
            )

            # for user in emergency_users:
            #     send_fcm_notification(
            #         tokens=user.fcm_token,
            #         title="بلاغ طارئ جديد",
            #         body=serializer.validated_data['report_reason']
            #     )

            return Response({"message": "Emergency report sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateMissingReportView(APIView):
    def post(self, request):
        serializer = MissingReportCreateSerializer(data=request.data)
        if serializer.is_valid():
            report = Report.objects.create(report_type='MISSING')
            MissingReport.objects.create(
                report=report,
                reported_by=request.user,
                missing_name=serializer.validated_data.get('missing_name'),
                missing_health_id=serializer.validated_data.get('missing_health_id'),
                description=serializer.validated_data['description'],
                last_seen_location=serializer.validated_data['last_seen_location'],
                contact_number=serializer.validated_data.get('contact_number'),
                photo=serializer.validated_data.get('photo')
            )

            recipients = User.objects.filter(account_type__in=['emergency', 'admin']).exclude(fcm_token=None)
            tokens = [user.fcm_token for user in recipients if user.fcm_token]
            responce = send_fcm_notification(
                tokens=tokens,
                title="New Missing Report",
                body=serializer.validated_data['description']
            )
            # for user in emergency_users:
            #     send_fcm_notification(
            #         token=user.fcm_token,
            #         title="بلاغ مفقود جديد",
            #         body=serializer.validated_data['description']
            #     )

            return Response({"message": "Missing report sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportListView(ListAPIView):
    queryset = Report.objects.all().order_by('-created_at').prefetch_related('emergency_details__pilgrim',
                                                                             'missing_details')
    serializer_class = ReportListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]


class GroupedReportsByReporterView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        reports = Report.objects.all().select_related(
            'emergency_details__pilgrim',
            'missing_details__reported_by'
        )

        grouped = defaultdict(list)

        for report in reports:
            if report.report_type == 'EMERGENCY' and hasattr(report, 'emergency_details'):
                user = report.emergency_details.pilgrim
                name = user.get_full_name()
                location = report.emergency_details.location
            elif report.report_type == 'MISSING' and hasattr(report,
                                                             'missing_details') and report.missing_details.reported_by:
                user = report.missing_details.reported_by
                name = report.missing_details.missing_name
                location = report.missing_details.last_seen_location
            else:
                continue

            grouped[(user.id, user.get_full_name())].append({
                "id": report.id,
                "type": report.report_type,
                "status": report.status,
                "name": name,
                "created_at": report.created_at.isoformat(),
                "location": location
            })
        response_data = []
        for (user_id, user_name), report_list in grouped.items():
            sorted_reports = sorted(report_list, key=lambda r: r['created_at'], reverse=True)
            print(sorted_reports)
            response_data.append({
                "reporter_id": user_id,
                "reporter_name": user_name,
                "reports": sorted_reports
            })

        # final_serializer = ReporterGroupedReportsSerializer(response_data, many=True)
        return Response(response_data)


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEmergency | IsAdmin]

    def post(self, request):
        report_id = request.data.get('report_id')
        report = get_object_or_404(Report, id=report_id)
        data = {
            'id': report.id,
            'type': report.report_type,
            'status': report.status,
            'created_at': report.created_at
        }

        if report.report_type == 'EMERGENCY' and hasattr(report, 'emergency_details'):
            er = report.emergency_details
            data.update({
                'report_reason': er.report_reason,
                'location': er.location,
                'pilgrim': {
                    'id': er.pilgrim.id,
                    'name': er.pilgrim.get_full_name(),
                    'id_number': er.pilgrim.pilgrim_profile.id_or_pass_number
                }
            })
        elif report.report_type == 'MISSING' and hasattr(report, 'missing_details'):
            mr = report.missing_details

            data.update({
                'missing_name': mr.missing_name,
                'health_id': mr.missing_health_id,
                'description': mr.description,
                'last_seen_location': mr.last_seen_location,
                'contact_number': mr.contact_number,
                'photo_url': mr.photo.url if mr.photo else None,
                'reported_by': {
                    'id': mr.reported_by.id if mr.reported_by else None,
                    'name': mr.reported_by.get_full_name() if mr.reported_by else None,
                    'id_number': mr.reported_by.pilgrim_profile.id_or_pass_number
                }
            })

        return Response(data, status=status.HTTP_200_OK)


class UpdateReportStatusView(APIView):
    permission_classes = [IsAuthenticated, IsEmergency]

    def patch(self, request):
        new_status = request.data.get("status")
        valid_statuses = ['NEW', 'IN_PROGRESS', 'RESOLVED']

        if new_status not in valid_statuses:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report_id = request.data.get("report_id")
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        report.status = new_status
        report.save()

        return Response({
            "message": "Report status updated successfully.",
            "report_id": report.id,
            "new_status": report.status
        }, status=status.HTTP_200_OK)


class ListPilgrimsWithStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsEmergency]

    def get(self, request):
        pilgrims = User.objects.filter(account_type='pilgrim', is_active=True)
        data = []

        for pilgrim in pilgrims:
            status_info = {
                "status": "safe",
                "report_status": "RESOLVED"
            }

            unresolved_emergency = EmergencyReport.objects.filter(
                pilgrim=pilgrim,
                report__status__in=['NEW', 'IN_PROGRESS']
            ).first()

            if unresolved_emergency:
                status_info = {
                    "status": "EMERGENCY",
                    "report_status": unresolved_emergency.report.status
                }
            else:
                missing_report = MissingReport.objects.filter(
                    missing_name__iexact=pilgrim.get_full_name(),
                    report__status__in=['NEW', 'IN_PROGRESS']
                ).first()
                if missing_report:
                    status_info = {
                        "status": "MISSING",
                        "report_status": missing_report.report.status
                    }

            data.append({
                "id": pilgrim.id,
                "full_name": pilgrim.get_full_name(),
                **status_info
            })

        return Response(data, status=status.HTTP_200_OK)


class MyReportsView(APIView):
    permission_classes = [IsAuthenticated, IsPilgrim]

    def get(self, request):
        user = request.user

        emergency_reports = EmergencyReport.objects.filter(pilgrim=user).select_related('report')
        missing_reports = MissingReport.objects.filter(reported_by=user).select_related('report')

        combined = []

        for er in emergency_reports:
            combined.append({
                "id": er.report.id,
                "type": "EMERGENCY",
                "status": er.report.status,
                "created_at": er.report.created_at,
                "location": er.location,
                "reason": er.report_reason,
            })

        for mr in missing_reports:
            combined.append({
                "id": mr.report.id,
                "type": "MISSING",
                "status": mr.report.status,
                "created_at": mr.report.created_at,
                "missing_name": mr.missing_name,
                "last_seen_location": mr.last_seen_location,
                "description": mr.description,
            })

        # ترتيب حسب الأحدث
        combined.sort(key=lambda x: x["created_at"], reverse=True)

        return Response(combined, status=status.HTTP_200_OK)


class ReportsByPilgrimIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pilgrim_id):
        try:
            user = User.objects.get(id=pilgrim_id, account_type='pilgrim')
        except User.DoesNotExist:
            return Response({"error": "الحاج غير موجود."}, status=status.HTTP_404_NOT_FOUND)

        emergency_reports = EmergencyReport.objects.filter(pilgrim=user).select_related('report')
        missing_reports = MissingReport.objects.filter(reported_by=user).select_related('report')

        combined = []

        for er in emergency_reports:
            combined.append({
                "id": er.report.id,
                "type": "EMERGENCY",
                "status": er.report.status,
                "created_at": er.report.created_at,
                "location": er.location,
                "reason": er.report_reason,
            })

        for mr in missing_reports:
            combined.append({
                "id": mr.report.id,
                "type": "MISSING",
                "status": mr.report.status,
                "created_at": mr.report.created_at,
                "missing_name": mr.missing_name,
                "last_seen_location": mr.last_seen_location,
                "description": mr.description,
            })

        combined.sort(key=lambda x: x["created_at"], reverse=True)

        return Response(combined, status=status.HTTP_200_OK)


class SendMessageNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        title = request.data.get('title', 'رسالة جديدة')
        body = request.data.get('body', '')

        if not recipient_id or not body:
            return Response({"error": "الرجاء تحديد المستلم ومحتوى الرسالة."}, status=status.HTTP_400_BAD_REQUEST)

        recipient = get_object_or_404(User, id=recipient_id)

        if not recipient.fcm_token:
            return Response({"error": "لا يوجد FCM Token لهذا المستخدم."}, status=status.HTTP_400_BAD_REQUEST)

        # إرسال الإشعار
        send_fcm_notification(
            tokens=[recipient.fcm_token],
            title=title,
            body=body
        )

        return Response({"message": "تم إرسال الإشعار بنجاح."}, status=status.HTTP_200_OK)


class DirectionsAPIView(APIView):
    permission_classes = [AllowAny]  # يمكن تعديل الصلاحيات لاحقًا

    def post(self, request):
        origin = request.data.get('origin')
        destination = request.data.get('destination')

        if not origin or not destination:
            return Response(
                {"error": "Both 'origin' and 'destination' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = get_directions(origin, destination)
            return Response(data, content_type='application/json; charset=utf-8')
        except requests.RequestException as e:
            return Response(
                {"error": "Failed to fetch directions", "details": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except ValueError as ve:
            return Response(
                {"error": str(ve)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
