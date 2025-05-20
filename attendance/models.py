from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.otp

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=200)

class QRCode(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    qr_code_data = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
class Topic(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)  # Add this line

    class Meta:
        ordering = ['position']  # Ensure topics are ordered by position by default

    def __str__(self):
        return self.title

class AttendanceEntry(models.Model):
    # Define fields for the AttendanceEntry model
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    selfie = models.ImageField(upload_to='media/', blank=True, null=True)
    submission_time = models.DateTimeField(default=timezone.now)
    device_identifier = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name} - {self.roll_number} - {self.selfie}"
