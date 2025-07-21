# middleware.py
from core.models import UserLoginHistory
from user_agents import parse
import requests

class LoginHistoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.get('login_record_created', False):
                # Create a login record only if it hasn't been created for this session
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                user = request.user

                # Make an API request to ipinfo.io to retrieve location information
                location_data = self.get_location_data(ip_address)

                # Extract location details
                city = location_data.get('city', 'Unknown')
                country = location_data.get('country', 'Unknown')

                # Parse the User-Agent string using django-user-agents
                user_agent_info = parse(user_agent)

                browser = user_agent_info.browser.family or 'Unknown'
                os = user_agent_info.os.family or 'Unknown'

                UserLoginHistory.objects.create(
                    user=user,
                    ip_address=ip_address,
                    browser=browser,
                    os=os,
                    country=country,
                    city=city,
                )

                # Set a flag in the session to indicate that a login record has been created
                request.session['login_record_created'] = True

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_location_data(self, ip_address):
        # Make an API request to the geolocation service and parse the response
        api_key = '91430a070fdb33'
        url = f'https://ipinfo.io/{ip_address}/json?token={api_key}'
        response = requests.get(url)
        location_data = response.json()
        return location_data
