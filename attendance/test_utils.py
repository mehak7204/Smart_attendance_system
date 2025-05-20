# test_utils.py
import unittest
from geopy.distance import geodesic
from attendance.utils import is_within_range, generate_qr_code, get_client_ip, is_same_subnet

class UtilsTestCase(unittest.TestCase):

    def test_is_within_range(self):
        student_location = (34.0522, -118.2437)  # Los Angeles
        event_location = (34.0522, -118.2430)    # Close to Los Angeles
        self.assertTrue(is_within_range(student_location, event_location, allowed_distance=100))

        event_location_far = (34.0522, -118.2500)  # Further away
        self.assertFalse(is_within_range(student_location, event_location_far, allowed_distance=100))

    def test_generate_qr_code(self):
        text = "Hello, World!"
        qr_image = generate_qr_code(text)
        self.assertIsNotNone(qr_image)  # Check that an image is returned
        self.assertTrue(hasattr(qr_image, 'save'))  # Check that it has a save method

    def test_get_client_ip(self):
        class MockRequest:
            META = {
                'HTTP_X_FORWARDED_FOR': '192.168.1.1',
                'REMOTE_ADDR': '127.0.0.1'
            }

        request = MockRequest()
        self.assertEqual(get_client_ip(request), '192.168.1.1')

        # Test without X-Forwarded-For
        request.META['HTTP_X_FORWARDED_FOR'] = ''
        self.assertEqual(get_client_ip(request), '127.0.0.1')

    def test_is_same_subnet(self):
        self.assertTrue(is_same_subnet('192.168.1.10', '192.168.1.20'))
        self.assertFalse(is_same_subnet('192.168.1.10', '192.168.2.20'))

if __name__ == '__main__':
    unittest.main()