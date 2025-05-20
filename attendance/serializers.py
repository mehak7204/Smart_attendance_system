from rest_framework import serializers
from .models import Event, Attendance, QRCode

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'
