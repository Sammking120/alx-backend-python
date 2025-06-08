# middleware.py

import logging
import time as time_module
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.http import HttpResponseForbidden
from collections import defaultdict



# Configure logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')  # Logs will be written to this file
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()

        # Define restricted hours (outside 6PM to 9PM)
        start_allowed = time(18, 0)  # 6:00 PM
        end_allowed = time(21, 0)    # 9:00 PM

        # Check if the request is to the chat/messaging path
        if request.path.startswith('/chat/'):
            if not (start_allowed <= current_time <= end_allowed):
                return HttpResponseForbidden("Access to the chat is restricted between 6 PM and 9 PM.")

        return self.get_response(request)




class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_logs = defaultdict(list)  # {ip_address: [timestamp1, timestamp2, ...]}
        self.limit = 5  # max messages
        self.window = 60  # seconds

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith('/chat/'):
            ip_address = self.get_client_ip(request)
            current_time = time_module.time()

            # Clean old timestamps
            timestamps = [t for t in self.message_logs[ip_address] if current_time - t < self.window]
            self.message_logs[ip_address] = timestamps

            if len(timestamps) >= self.limit:
                return HttpResponseForbidden("Message rate limit exceeded. Please wait a moment before sending more messages.")

            self.message_logs[ip_address].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Get client IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
