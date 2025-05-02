from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

ACCOUNT_TYPES = [
    ("pilgrim", "Pilgrim"),
    ("family", "Family"),
    ("emergency", "Emergency"),
    ("normal", "Normal User"),
    ("admin", "Admin User")
]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    fcm_token = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name', 'account_type']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class PilgrimProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pilgrim_profile')
    health_id = models.CharField(max_length=50)
    id_or_pass_number = models.CharField(max_length=50)
    medical_info = models.TextField(blank=True, null=True)
    campaign_number = models.CharField(max_length=100, blank=True, null=True)


class EmergencyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emergency_profile')
    is_active = models.BooleanField(default=False)
    # location = models.CharField(max_length=255)


class FamilyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_profile')
    pilgrim = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_member')


class NormalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='normal_profile')


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # "activation" or "reset"
    created_at = models.DateTimeField(auto_now_add=True)

#
# class FamilyRelation(models.Model):
#     family_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
#     pilgrim = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
#     is_confirmed = models.BooleanField(default=False)
