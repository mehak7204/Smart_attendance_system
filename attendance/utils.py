from geopy.distance import geodesic
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
import ipaddress
from django.http import HttpRequest

def is_within_range(student_location, event_location, allowed_distance=100):
    distance = geodesic(student_location, event_location).meters
    return distance <= allowed_distance

def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_same_subnet(client_ip: str, server_ip: str) -> bool:
    client_network = '.'.join(client_ip.split('.')[:3])
    server_network = '.'.join(server_ip.split('.')[:3])
    return client_network == server_network
