from rest_framework.generics import ListAPIView

from global_services.firebase.notifications import send_fcm_notification
from .permissions import IsAdmin, IsPilgrim
from .serializers import PilgrimProfileSerializer, EmergencyProfileSerializer, FamilyProfileSerializer, \
    NormalProfileSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import User, PilgrimProfile, EmergencyProfile, FamilyProfile, NormalProfile, VerificationCode
from django.contrib.auth import authenticate
from .utils import create_and_send_verification, send_verification_email
from global_services.exceptions import error_response

signer = TimestampSigner()


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)

        create_and_send_verification(user, "activation",
                                     "Email Verification Code", "Your verification code is: {code}")

        account_type = user.account_type
        if account_type == "pilgrim":
            PilgrimProfile.objects.create(
                user=user,
                health_id=self.request.data.get('health_id', ''),
                medical_info=self.request.data.get('medical_info', ''),
                id_or_pass_number=self.request.data.get('id_or_pass_number', '')
            )
        elif account_type == "emergency":
            EmergencyProfile.objects.create(user=user)

            recipients = User.objects.filter(account_type='admin').exclude(fcm_token=None)
            tokens = [user.fcm_token for user in recipients if user.fcm_token]
            responce = send_fcm_notification(
                tokens=tokens,
                title="New Emergency Account",
                body="Request to activate emergency account"
            )

        elif account_type == "family":
            id_or_pass_number = self.request.data.get('id_or_pass_number')
            pilgrim_profile = get_object_or_404(PilgrimProfile, id_or_pass_number=id_or_pass_number)
            pilgrim = pilgrim_profile.user

            FamilyProfile.objects.create(user=user, pilgrim=pilgrim)
        elif account_type == "normal":
            NormalProfile.objects.create(user=user)


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        user = get_object_or_404(User, email=email)

        verification = VerificationCode.objects.filter(user=user, code=code, purpose='activation').first()

        if not verification:
            return error_response("Invalid or expired verification code.", status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        verification.delete()

        return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)


class EmergencyProfilesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = EmergencyProfileSerializer
    queryset = EmergencyProfile.objects.select_related('user')


class ActivateEmergencyProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        profile_id = request.data.get('profile_id')  # test
        is_active = request.data.get('is_active')  # test

        profile = get_object_or_404(EmergencyProfile, id=profile_id)
        profile.is_active = is_active
        profile.save()

        if not is_active:
            send_verification_email("Profile Activation", "Admins declined to activate your account",
                                    profile.user.email)
            return Response({"message": "Declined Profile Activation."})

        send_verification_email("Profile Activation", "Your emergency profile is activated, you can login",
                                profile.user.email)

        return Response({"message": "Emergency profile activated and email sent."})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("Invalid email or password.", 401)

        if not user.check_password(password):
            return error_response("Invalid email or password.", 401)
        if not user.is_active:
            return error_response("Account is not activated.", 403)

        if user.account_type == "emergency" and not user.emergency_profile.is_active:
            return error_response("Your account is pending admin approval.", 403)

        fcm_token = request.data.get("fcm_token")
        if fcm_token:
            user.fcm_token = fcm_token
            user.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "account_type": user.account_type,
            "id": user.id
        })


class SendResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("No user found with this email address.", 404)

        try:
            create_and_send_verification(user, "reset", "Password Reset Code", "Your password reset code is: {code}")

        except Exception as e:
            return error_response(str(e), 500)

        return Response({'detail': 'Password reset code sent successfully.'}, status=status.HTTP_200_OK)


class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        user = get_object_or_404(User, email=email)

        verification = VerificationCode.objects.filter(user=user, code=code, purpose="reset").first()
        if not verification:
            return error_response("Invalid or expired verification code.", status.HTTP_400_BAD_REQUEST)

        verification.delete()

        signer = TimestampSigner()
        temp_token = signer.sign(user.pk)

        return Response({"temp_token": temp_token}, status=status.HTTP_200_OK)


class PasswordResetWithTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get('temp_token')
        new_password = request.data.get('new_password')

        if not temp_token or not new_password:
            return error_response("Temp token and new password are required.", 400)

        if len(new_password) < 8:
            return error_response("Password must be at least 8 characters long.", 400)

        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(temp_token, max_age=600)
            user = get_object_or_404(User, pk=user_pk)
            user.set_password(new_password)
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Password reset successfully.",
                "token": token.key
            }, status=status.HTTP_200_OK)

        except SignatureExpired:
            return error_response("Temp token has expired.", 400)
        except BadSignature:
            return error_response("Invalid temp token.", 400)


class SendLoginCodeView(APIView):
    permission_classes = [AllowAny | IsPilgrim]

    def post(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        health_id = request.data.get('health_id')

        if not email or not first_name or not last_name or not health_id:
            return error_response("Email, full name, and health ID are required.", 400)

        try:
            user = User.objects.get(email=email, account_type='pilgrim')
        except User.DoesNotExist:
            return error_response("No pilgrim user found with this email.", 404)

        pilgrim_profile = getattr(user, 'pilgrim_profile', None)
        if not pilgrim_profile:
            return error_response("Pilgrim profile not found.", 404)

        if user.first_name != first_name or user.last_name != last_name or pilgrim_profile.health_id != health_id:
            return error_response("Provided information does not match.", 400)

        try:
            create_and_send_verification(user, "login",
                                         "Login Verification Code", "Your login verification code is: {code}")
        except Exception as e:
            return error_response(str(e), 500)

        return Response({'detail': 'Login verification code sent successfully.'}, status=status.HTTP_200_OK)


class LoginWithCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return error_response("Email and code are required.", 400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("No user found with this email.", 404)

        verification = VerificationCode.objects.filter(user=user, code=code, purpose="login").first()
        if not verification:
            return error_response("Invalid or expired verification code.", 400)

        verification.delete()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "account_type": user.account_type,
            "id": user.id
        }, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        user_data = self.get_serializer(user).data
        profile_data = self.get_profile_data(user)

        return Response({
            "user": user_data,
            "profile": profile_data
        })

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        user_serializer = self.get_serializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        profile_serializer_class = self.get_profile_serializer_class(user.account_type)
        profile_instance = self.get_profile_instance(user)

        if profile_serializer_class and profile_instance:
            profile_serializer = profile_serializer_class(
                profile_instance,
                data=request.data,
                partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
            profile_data = profile_serializer.data
        else:
            profile_data = {}

        return Response({
            "message": "User and profile updated successfully.",
            "user": user_serializer.data,
            "profile": profile_data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def get_profile_serializer_class(self, account_type):
        return {
            "pilgrim": PilgrimProfileSerializer,
            "emergency": EmergencyProfileSerializer,
            "family": FamilyProfileSerializer,
            "normal": NormalProfileSerializer
        }.get(account_type, None)

    def get_profile_instance(self, user):
        return getattr(user, f"{user.account_type}_profile", None)

    def get_profile_data(self, user):
        profile_instance = self.get_profile_instance(user)
        serializer_class = self.get_profile_serializer_class(user.account_type)
        if profile_instance and serializer_class:
            return serializer_class(profile_instance).data
        return {}


class ListPilgrimsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        pilgrims = User.objects.filter(account_type='pilgrim', is_active=True)
        data = [{"id": pilgrim.id, "full_name": pilgrim.get_full_name()} for pilgrim in pilgrims]
        return Response(data, status=status.HTTP_200_OK)


class GetSupervisorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        supervisor = User.objects.filter(is_superuser=True).first()
        if not supervisor:
            return Response({"detail": "No supervisor found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "id": supervisor.id,
            "full_name": supervisor.get_full_name(),
            "email": supervisor.email
        }, status=status.HTTP_200_OK)


class GetLinkedPilgrimView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family_profile = getattr(request.user, 'family_profile', None)
        if not family_profile:
            return Response({"error": "No family profile found"}, status=404)

        pilgrim = family_profile.pilgrim
        return Response({
            "pilgrim_id": pilgrim.id,
            "full_name": pilgrim.get_full_name(),
            "email": pilgrim.email
        }, status=200)
