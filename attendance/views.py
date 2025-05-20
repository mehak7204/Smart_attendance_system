# attendance/views.py
import base64
import math
import os
import logging
from .forms import UserLoginForm
from datetime import datetime

from rest_framework.permissions import AllowAny
import io
import pandas as pd
import openpyxl
import socket
import uuid
from django.core.files.storage import FileSystemStorage
import time
import csv
from .models import Profile
from django.http import HttpResponse
from django.utils.text import slugify
from io import StringIO
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth import authenticate, login, get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, response
# from rest_framework.response import Response
# from rest_framework import status
from .models import Event, Attendance, QRCode
from .serializers import EventSerializer, AttendanceSerializer, QRCodeSerializer
from .utils import is_within_range, generate_qr_code, get_client_ip, is_same_subnet
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
import random
from .models import OTP
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Topic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import Topic
from .forms import TopicForm, AttendanceEntryForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
# attendance/views.py
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .utils import generate_qr_code
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
import qrcode
from io import BytesIO
from django.views.generic import View
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .models import AttendanceEntry
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
# from django.shortcuts import render
# from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Topic
from django.http import HttpResponseForbidden
from datetime import timedelta, datetime
from django.shortcuts import render
from django.views.generic import View
# from django_qrcode.views import QRCodeView
from .models import Topic
from .models import AttendanceEntry
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


def success(request):
    return render(request, 'mail_success.html')


def token_send(request):
    return render(request, 'token_send.html')


def compare_roll_numbers(request, topic_id):
    import pandas as pd
    from .models import AttendanceEntry, Topic
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    import logging

    logger = logging.getLogger(__name__)

    try:
        if request.method == "POST":
            # Ensure file is uploaded
            file = request.FILES.get('file')
            if not file:
                logger.error("No file uploaded.")
                return JsonResponse({'success': False, 'error': 'No file uploaded.'})

            logger.info(f"File uploaded: {file.name}")

            # Read the uploaded file into a DataFrame
            df = pd.read_excel(file)

            # Validate required columns
            if 'Name' not in df.columns or 'roll_number' not in df.columns:
                logger.error("Invalid file format. Expected columns: 'Name' and 'roll_number'.")
                return JsonResponse({'success': False, 'error': 'Invalid file format. Expected columns: Name, roll_number.'})

            logger.info("File format validated successfully.")

            # Fetch the topic and related attendance entries
            topic = get_object_or_404(Topic, id=topic_id)
            attendance_entries = AttendanceEntry.objects.filter(topic=topic)
            attendance_roll_numbers = set(attendance_entries.values_list('roll_number', flat=True))

            # Get roll numbers from the uploaded file
            uploaded_roll_numbers = set(df['roll_number'].astype(str))

            # Perform comparison
            present_ids = uploaded_roll_numbers.intersection(attendance_roll_numbers)
            absent_ids = uploaded_roll_numbers.difference(attendance_roll_numbers)
            additional_responses = attendance_roll_numbers.difference(uploaded_roll_numbers)

            logger.info(f"Comparison results - Present: {present_ids}, Absent: {absent_ids}, Additional: {additional_responses}")

            # Store results in session
            request.session['compare_results'] = {
                'present_ids': list(present_ids),
                'absent_ids': list(absent_ids),
                'additional_responses': list(additional_responses),
            }

            # Return success response
            return JsonResponse({'success': True, 'report_id': topic_id})

        else:
            logger.error("Invalid request method.")
            return JsonResponse({'success': False, 'error': 'Invalid request method. Only POST is allowed.'})

    except Exception as e:
        logger.error(f"Error during file processing: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})



def compare_report(request, topic_id):
    # Retrieve comparison results from session
    compare_results = request.session.get("compare_results")
    if not compare_results:
        return render(request, "error.html", {"message": "No comparison data found."})

    return render(request, "compare_report.html", {
        "present_ids": compare_results["present_ids"],
        "absent_ids": compare_results["absent_ids"],
        "additional_responses": compare_results["additional_responses"],
        "topic_id": topic_id,
    })


def download_report(request, topic_id):
    # Retrieve comparison results from session
    compare_results = request.session.get("compare_results")
    if not compare_results:
        return render(request, "error.html", {"message": "No comparison data found."})

    # Create a DataFrame for the CSV file
    data = {
        'Present IDs': compare_results["present_ids"],
        'Absent IDs': compare_results["absent_ids"],
        'Additional Responses': compare_results["additional_responses"]
    }

    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))

    # Generate the file name with current date
    file_name = f"comparison_report_{now().strftime('%Y-%m-%d')}.csv"

    # Prepare the response to send the CSV file
    response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

class GenerateQRCodeView(View):
    login_url = '/login/'

    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = int(timezone.now().timestamp())
        qr_data = f"http://192.168.0.106:8000//attendance/{topic_id}/submit_attendance/?timestamp={timestamp}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Store the latest timestamp in the session
        request.session['latest_qr_timestamp'] = timestamp
        request.session['attendance_stopped'] = False

        return render(request, 'qr_code.html',
                      {'qr_code': img_str, 'topic': topic, 'timestamp': timestamp, 'qr_data': qr_data})


@login_required(login_url='/login/')
def download_topic_details_as_csv(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    entries = topic.attendanceentry_set.all()

    response = HttpResponse(content_type='text/csv')
    filename = f"{slugify(topic.title)}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Serial Number', 'Name', 'Roll Number'])

    for index, entry in enumerate(entries, start=1):
        writer.writerow([index, entry.name, entry.roll_number])

    return response


class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'home.html')


class MyView(View):
    def get(self, request):
        # Generate QR code for a specific text
        qr_code_text = "Your QR Code Text Here"
        qr_code_img = generate_qr_code(qr_code_text)

        # Example logic: Render a template with QR code image
        return render(request, 'my_template.html', {'qr_code_img': qr_code_img})


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        topics = Topic.objects.filter(user=user)
        topic_count = topics.count()

        # Pagination logic
        page = request.GET.get('page', 1)
        paginator = Paginator(topics, 10)  # Show 10 topics per page

        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            topics = paginator.page(1)
        except EmptyPage:
            topics = paginator.page(paginator.num_pages)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            topics_html = render_to_string('includes/topics_list.html', {'topics': topics})
            return JsonResponse({'topics_html': topics_html})

        return render(request, 'dashboard.html', {
            'topics': topics,
            'topic_count': topic_count,
            'paginator': paginator
        })

    def post(self, request):
        order = request.POST.getlist('order[]')
        for index, topic_id in enumerate(order):
            topic = Topic.objects.get(id=topic_id, user=request.user)
            topic.order = index
            topic.save()
        return JsonResponse({'status': 'success'})


class UserLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            profile_obj = Profile.objects.filter(user=user).first()
            if user is not None:
                if not profile_obj.is_verified:
                    messages.success(request, "Your account is not verified, please check your mail")
                    return redirect('/login')
                else:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, 'Invalid Credentials')
        else:
            messages.error(request, 'Invalid CAPTCHA')
        return render(request, 'login.html', {'form': form})


def LogoutView(request):
    logout(request)
    return redirect('login')


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'registration.html', {'error_message': None})

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        # Check if passwords match
        if password != confirm_password:
            error_message = 'Passwords do not match.'
            return render(request, 'registration.html', {'error_message': error_message})
        if not (username and email and password):
            return Response({'detail': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists. Please choose a different username.'
            return render(request, 'registration.html', {'error_message': error_message})
        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            error_message = 'E-mail ID provided is already in use. Login or register with another mail ID.'
            return render(request, 'registration.html', {'error_message': error_message})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        auth_token = str(uuid.uuid4())
        profile_obj = Profile.objects.create(user=user, auth_token=auth_token)
        profile_obj.save()
        if user:
            send_mail_after_registration(username, email, auth_token)
            return redirect('/token')
        return Response({'detail': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, "Your account is already verified")
                return redirect('/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Congratulations! Your account has been verified')
            return redirect('login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')


def error_page(request):
    return render(request, 'mail_verification_error.html')


def send_mail_after_registration(username, email, token):
    subject = "Account Activation | Smart Attendance System"
    message = f'Dear {username}, \nWe are delighted to have you join us on Smart Attendance System! Your account has been created successfully. Click on the following link to verify your account:\n http://projects.klh.edu.in/verify/{token}\n\nRemember, you will be able to login only if your account is activated\n'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


class CreateTopicView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        form = TopicForm()
        return render(request, 'create_topic.html', {'form': form})

    def post(self, request):
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('dashboard')
        return render(request, 'create_topic.html', {'form': form})


class TopicDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk, user=request.user)
        query = request.GET.get('query', '')
        if query:
            entries = topic.attendanceentry_set.filter(
                Q(name__icontains=query) | Q(roll_number__icontains=query)
            )
            if request.is_ajax():
                return render(request, 'partials/entries_list.html', {'entries': entries})
        else:
            entries = topic.attendanceentry_set.all()
        return render(request, 'topic_detail.html', {'topic': topic, 'entries': entries})


def delete_entry(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(AttendanceEntry, id=entry_id)
        entry.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


class TopicUpdateView(UpdateView):
    login_url = '/login/'
    model = Topic
    form_class = TopicForm
    template_name = 'update_topic.html'
    context_object_name = 'topic'
    success_url = reverse_lazy('dashboard')


class TopicDeleteView(DeleteView):
    login_url = '/login/'
    model = Topic
    template_name = 'confirm_delete_topic.html'
    context_object_name = 'topic'
    success_url = reverse_lazy('dashboard')


from django.shortcuts import render
from django.utils.timezone import now
from datetime import timedelta
import psutil


class SubmitAttendanceView(View):
    # def get_server_ip(self):
    #     # try:
    #         hostname = socket.gethostname()
    #         return socket.gethostbyname(hostname)
    #     # except Exception as e:
    #     #     return '127.0.0.1'
    def get_server_ip(self):
        # Iterate through all network interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            if interface == 'Wi-Fi' or 'Wireless' in interface:
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                        return addr.address
        return None


    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = request.GET.get('timestamp')

        client_ip = get_client_ip(request)
        server_ip = self.get_server_ip()
        
        # Logging the IP addresses and subnet check result
        logger = logging.getLogger(__name__)
        logger.info(f"Server IP: {server_ip}, Client IP: {client_ip}")
        if not is_same_subnet(client_ip, server_ip):
            logger.info("IP Check Result: False - Client is not connected to the same subnet as the server.")
            return render(request, 'wifierror.html')
        else:
            logger.info("IP Check Result: True - Client is connected to the same subnet as the server.")

        if not timestamp or not self.is_qr_code_valid(timestamp, request.session.get('latest_qr_timestamp'),
                                                      request.session.get('attendance_stopped')):
            return render(request, 'attendance_error.html')

        # Store the necessary information in the session
        request.session['topic_id'] = topic_id
        request.session['timestamp'] = timestamp
        device_identifier = self.get_device_identifier(request)

        # Check if the user has already submitted attendance within the last hour
        last_submission = AttendanceEntry.objects.filter(
            device_identifier=device_identifier,
            topic=topic
        ).order_by('-submission_time').first()

        if last_submission and now() - last_submission.submission_time < timedelta(minutes=1):
            # Redirect to wait page if the user has already submitted
            time_left = timedelta(hours=1) - (now() - last_submission.submission_time)
            minutes_left = time_left.seconds // 60
            return render(request, 'wait_page.html', {'minutes_left': minutes_left})
        # Render the attendance form
        form = AttendanceEntryForm()
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = request.session.get('timestamp')

        if not timestamp or not self.is_qr_code_valid(timestamp, request.session.get('latest_qr_timestamp'),
                                                      request.session.get('attendance_stopped')):
            return render(request, 'attendance_error.html')

        device_identifier = self.get_device_identifier(request)
        if not device_identifier:
            device_identifier = str(uuid.uuid4())  # Generate a unique identifier
            response.set_cookie('device_identifier', device_identifier)
        now = timezone.now()
        last_submission = AttendanceEntry.objects.filter(device_identifier=device_identifier).order_by(
            '-submission_time').first()

        if last_submission and now - last_submission.submission_time < timedelta(minutes=1):
            # Redirect to a message page saying user needs to wait
            return render(request, 'wait_page.html',
                          {'minutes_left': 50 - (now - last_submission.submission_time).seconds // 60})

        form = AttendanceEntryForm(request.POST, request.FILES)
        if form.is_valid():
            attendance_entry = form.save(commit=False)
            attendance_entry.topic = topic
            attendance_entry.device_identifier = device_identifier
            attendance_entry.submission_time = now
            attendance_entry.save()
            return render(request, 'attendance_success.html')
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

    def get_device_identifier(self, request):
        # This function generates a unique identifier for the device
        return request.META.get('REMOTE_ADDR', '')

    def is_qr_code_valid(self, timestamp, latest_timestamp, attendance_stopped):
        if attendance_stopped:
            return False

        if not latest_timestamp:
            return True

        try:
            qr_code_time = datetime.fromtimestamp(int(timestamp), timezone.utc)
            latest_qr_code_time = datetime.fromtimestamp(int(latest_timestamp), timezone.utc)
            current_time = timezone.now()

            # Log the times for debugging
            logger = logging.getLogger(__name__)
            logger.info(f"QR Code Time: {qr_code_time}, Latest QR Code Time: {latest_qr_code_time}, Current Time: {current_time}")

            if qr_code_time != latest_qr_code_time:
                return False
            if current_time - qr_code_time > timedelta(minutes=2):
                return False
            return True
        except ValueError:
            return False


class StopAttendanceView(View):
    def post(self, request, topic_id):
        request.session['attendance_stopped'] = True
        return redirect('topic_detail', pk=topic_id)


def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def qr_code_view(request):
    # Use the current time as the data for the QR code to ensure it's unique every 2 minutes
    current_time = time.time()
    data = str(int(current_time) // 120)  # Changes every 2 minutes
    qr_code = generate_qr(data)

    return render(request, 'qr_code.html', {'qr_code': qr_code})


def download_all_topics_and_entries_as_csv(request):
    # Fetch the username of the user
    username = request.user.username

    # Fetch all topics for the logged-in user and their entries
    topics = Topic.objects.filter(user=request.user)

    # Generate CSV content
    csv_content = StringIO()
    writer = csv.writer(csv_content)
    writer.writerow(['Topic', 'Name', 'Roll Number'])
    for topic in topics:
        entries = topic.attendanceentry_set.all()
        for entry in entries:
            writer.writerow([topic.title, entry.name, entry.roll_number])

    # Serve the CSV file for download
    filename = f"{slugify(username)}_all_topics_and_entries.csv"
    response = HttpResponse(csv_content.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class AddManualEntryView(View):
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        form = AttendanceEntryForm()
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        form = AttendanceEntryForm(request.POST)
        if form.is_valid():
            attendance_entry = form.save(commit=False)
            attendance_entry.topic = topic
            attendance_entry.save()
            return redirect('topic_detail', topic_id=topic_id)
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})


@csrf_exempt
@require_POST
def reorder_topics(request):
    try:
        order = request.POST.getlist('order[]')
        for index, topic_id in enumerate(order):
            topic = Topic.objects.get(id=topic_id)
            topic.position = index  # Assuming `position` is a field in the `Topic` model
            topic.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'forgot_password.html', {'error_message': None})

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, 'forgot_password.html', {'error_message': 'Provided E-mail ID is not registered'})

        # Redirect to reset password page with email as a parameter
        return redirect(f'/reset-password/?email={email}')


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.GET.get('email')
        return render(request, 'reset_password.html', {'email': email, 'error_message': None})

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password != confirm_password:
            return render(request, 'reset_password.html', {
                'email': email,
                'error_message': 'Passwords do not match'
            })

        user = User.objects.filter(email=email).first()
        if not user:
            return render(request, 'reset_password.html', {
                'email': email,
                'error_message': 'Error resetting password'
            })

        # Update the password
        user.password = make_password(password)
        user.save()

        return redirect('login')


from django.http import JsonResponse
from .models import AttendanceEntry


def update_entry(request, entry_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')

        try:
            entry = AttendanceEntry.objects.get(id=entry_id)
            entry.name = name
            entry.roll_number = roll_number
            entry.save()

            return JsonResponse({'success': True})
        except AttendanceEntry.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Entry not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def wifi_error_view(request):
    return render(request, 'wifierror.html')
