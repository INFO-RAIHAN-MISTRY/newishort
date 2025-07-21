from django.utils import timezone
from django.db import models
from .validators import validate_xlsx_extension
from core.models import (
    User
)
import random
import string
import qrcode
import user_agents
from io import BytesIO
from django.core.files import File
import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your models here.

class Url(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    short_url = models.CharField(max_length = 20, blank=True, verbose_name="Short Url Auto Generated")
    long_url = models.TextField(verbose_name="Long Url")
    url_title = models.CharField(max_length=100, verbose_name="Url Title")
    url_hit_count = models.PositiveIntegerField(default=0, verbose_name="Url Hit Count")
    status = models.BooleanField(default=True)
    url_created_at = models.DateField(auto_now=True)
    url_updated_at = models.DateField(auto_now=True)

    def check_and_send_milestone_notifications(self):
        milestones = [5, 10, 50, 100, 500, 1000, 5000, 10000, 100000]  # Set the milestone increment to 10 clicks
        email = self.user.email
        for milestone in milestones:
            if self.url_hit_count == milestone:
                subject = "Congrat's for your achivement !"
                title = self.url_title
                hit = self.url_hit_count
                html_message = render_to_string('congrats.html',{'title':title, 'hit':hit})

                # Create an EmailMessage with the same HTML content for both HTML and plain text
                email = EmailMessage(
                    subject,
                    html_message,  # Use the same HTML content for both HTML and plain text
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                email.content_subtype = 'html'  # Set the content type to HTML
                email.send()
            else:
                pass  # Use 'pass' as a placeholder when no notification is needed

    def save(self, *args, **kwargs):
        self.check_and_send_milestone_notifications()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.url_title


class UrlHitDetail(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='urls')
    visitor_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Visitor IP")
    country = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    coordinates = models.CharField(max_length=250, null=True, blank=True)
    region = models.CharField(max_length=250, null=True, blank=True)
    hit_time = models.DateTimeField(null=True, blank=True, verbose_name="Hit Time")
    browser = models.CharField(max_length=100, blank=True, verbose_name="Browser")
    os = models.CharField(max_length=100, blank=True, verbose_name="Operating System")

    def save(self, *args, **kwargs):
        if not self.city or not self.country:
            # Get visitor's IP address and country
            self.country, self.city, self.coordinates, self.region = self.get_visitor_info()
            self.hit_time = timezone.now()

        if not self.browser or not self.os:
            # Parse and extract browser and OS details from User Agent
            self.parse_user_agent()

        super(UrlHitDetail, self).save(*args, **kwargs)

    '''def get_visitor_info(self, request=None):
        try:
            # Get the visitor's IP address from the request object if provided
            visitor_ip = None

            if request:
                visitor_ip = request.META.get('REMOTE_ADDR')
                # visitor_ip = "1.184.176.27"

                location_data = self.get_location_data(visitor_ip)

                # Extract location details
                self.city = location_data.get('city', 'Unknown')
                self.country = location_data.get('country', 'Unknown')
                self.coordinates = location_data.get('loc', 'unknown')
                self.region = location_data.get('region', 'unknown')

        except Exception as e:
            print("Exception:", e)

        return self.country, self.city, self.coordinates, self.region'''

    def get_visitor_info(self, request=None):
        # try:
        #     # Get the visitor's IP address from the request object if provided
        #     visitor_ip = None

        #     if request:
        #         # visitor_ip = request.META.get('REMOTE_ADDR')
        visitor_ip = self.get_client_ip(request)
        print(visitor_ip)

        location_data = self.get_location_data(visitor_ip)

        # Extract location details
        self.city = location_data.get('city', 'Unknown')
        self.country = location_data.get('country', 'Unknown')
        self.coordinates = location_data.get('loc', 'unknown')
        self.region = location_data.get('region', 'unknown')

        # except Exception as e:
        #     print("Exception:", e)

        return self.country, self.city, self.coordinates, self.region

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    
    def parse_user_agent(self, request):
        # Extract browser and OS details from User Agent
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')

        if user_agent_string:
            user_agent = user_agents.parse(user_agent_string)
            self.browser = user_agent.browser.family
            self.os = user_agent.os.family
    
    def get_location_data(self, ip_address):
        # Make an API request to the geolocation service and parse the response
        api_key = '91430a070fdb33'
        url = f'https://ipinfo.io/{ip_address}/json?token={api_key}'
        response = requests.get(url)
        location_data = response.json()
        return location_data


class ExcelFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    excelsheet = models.FileField(upload_to='Excel_Files', max_length=100, verbose_name="Upload Excel Sheet", validators=[validate_xlsx_extension])
    created_at = models.DateField(auto_now=True)

class BulkUrlShort(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_url = models.CharField(max_length = 20, blank=True, verbose_name="Short Url Auto Generated")
    long_url = models.TextField(verbose_name="Long Url")
    url_title = models.CharField(max_length=250, null=True, blank=True, verbose_name="Url Related Title")
    url_hit_count = models.PositiveIntegerField(default=0, verbose_name="Url Hit Count")
    url_created_at = models.DateField(auto_now=True)
    url_updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        random_short = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
        self.short_url = str(random_short)
        super(BulkUrlShort, self).save(*args, **kwargs)

class QrCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    long_url = models.TextField()
    title = models.CharField(max_length=100)
    qrcode = models.ImageField(upload_to='Qrcodes', null=True, blank='True', verbose_name="Qr code Auto Generated")
    created_at = models.DateField(auto_now=True)

    # save method
    def save(self, *args, **kwargs):
        my_qr = qrcode.make(self.long_url)
        file_name = f'{self.user}-{self.title}qr.png'
        stream = BytesIO()
        my_qr.save(stream, 'PNG')
        self.qrcode.save(file_name, File(stream), save=False)
        super().save(*args, **kwargs)
    
