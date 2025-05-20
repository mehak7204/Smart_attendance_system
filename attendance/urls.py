# attendance/urls.py
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import UserLoginView, HomeView, DashboardView, UserRegistrationView, CreateTopicView, TopicDetailView, TopicUpdateView, TopicDeleteView, MyView, GenerateQRCodeView, SubmitAttendanceView, StopAttendanceView, download_topic_details_as_csv, download_all_topics_and_entries_as_csv, AddManualEntryView, reorder_topics, ForgotPasswordView, ResetPasswordView
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', token_send, name="token_send"),
    path('success/', success, name="success"),
    path('verify/<auth_token>', verify, name="verify"),
    path('verification_error/', error_page, name="verification_error"),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('create_topic/', CreateTopicView.as_view(), name='create_topic'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('logout/', views.LogoutView, name='logout'),
    # path('admin/', admin.site.urls),
    path('attendance/update-entry/<int:entry_id>/', views.update_entry, name='update_entry'),
    path('topic/update/<int:pk>/', TopicUpdateView.as_view(), name='update_topic'),
    path('topic/delete/<int:pk>/', TopicDeleteView.as_view(), name='delete_topic'),
    path('my-view/', MyView.as_view(), name='my_view'),
    path('topic/<int:topic_id>/', TopicDetailView.as_view(), name='topic_detail'),
    path('attendance/delete-entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('attendance/<int:topic_id>/generate-qr/', GenerateQRCodeView.as_view(), name='generate_qr_code'),
    path('attendance/<int:topic_id>/submit_attendance/', SubmitAttendanceView.as_view(), name='submit_attendance'),
    path('attendance/<int:topic_id>/stop/', StopAttendanceView.as_view(), name='stop_attendance'),
    path('qr/', views.qr_code_view, name='qr_code'),
    path('attendance/<int:topic_id>/download-csv/', download_topic_details_as_csv, name='download_topic_details_as_csv'),
    path('download-all-topics/', download_all_topics_and_entries_as_csv, name='download_all_topics'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('reorder_topics/', views.reorder_topics, name='reorder_topics'),
    path('attendance/compare/<int:topic_id>/', views.compare_roll_numbers, name='compare_roll_numbers'),
    path("attendance/report/<int:topic_id>/", views.compare_report, name="compare_report"),
    path("attendance/report/<int:topic_id>/download/", views.download_report, name="download_report"),
    path('attendance/<int:topic_id>/add_manual_entry/', AddManualEntryView.as_view(), name='add_manual_entry'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
