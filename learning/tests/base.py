from django.test import TestCase, override_settings

@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
class BaseTestCase(TestCase):
    pass