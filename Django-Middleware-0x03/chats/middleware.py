# middleware.py

import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden

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