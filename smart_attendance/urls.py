# smart_attendance/urls.py

from django.contrib import admin
from django.urls import path, include
from attendance.views import wifi_error_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance.urls')),
    path('', include('attendance.urls')),  # This includes the root URL
    path('captcha/', include('captcha.urls')),
    path('wifi-error/', wifi_error_view, name='wifi_error'),
]
