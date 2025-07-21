from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import (
    UserManager,
)
from datetime import datetime, timedelta
import string, random

# Create your models here.
class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    email_token = models.CharField(max_length=250, null=True, blank=True)
    is_email_varified = models.BooleanField(default=False)
    method = models.CharField(max_length=50, choices=[('manually', 'Manually'), ('google', 'Google')], default='manually')
    google_id = models.CharField(max_length=250, null=True, blank=True)
    extra_data = models.TextField(null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        random_short = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(20)])
        self.email_token = str(random_short)
        super(User, self).save(*args, **kwargs)

class Plan(models.Model):
    name = models.CharField(max_length=50, verbose_name='Plan Name')
    price = models.FloatField(default=0.0, verbose_name='Plan Price')
    duration = models.IntegerField(default=365, verbose_name='Plan Duration in Day')
    number_url = models.BigIntegerField(default = 0, verbose_name='Number of urls')
    number_qr = models.BigIntegerField(default = 0, verbose_name='Number of qr codes')
    api_access = models.BooleanField(default = False)
    bulk_url_short = models.BooleanField(default=False)
    details = models.TextField(verbose_name='Plan Details')
    subs_count = models.BigIntegerField(default=0, verbose_name='Plan Subscribe Count')
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # one to one relationship
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    used_urls = models.PositiveIntegerField(default = 0)
    used_qrs = models.PositiveBigIntegerField(default = 0)
    expires_at = models.DateTimeField(null = True, blank = True)
    razorpay_payment_id = models.CharField(max_length=250, null=True, blank=True)
    # payment_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.plan.name

    def save(self, *args, **kwargs):
        if not self.id: # Only set expires_at for the new users
            self.expires_at = datetime.now() + timedelta(days = self.plan.duration)
        super(Subscription, self).save(*args, **kwargs)

    def get_subscription_details(request):
        subscription_obj = Subscription.objects.get(user = request.user)
        return subscription_obj.plan

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # one to many relations ....
    # subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE) # one to many relations ....
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    payment_id = models.CharField(max_length=250, null=True, blank=True)
    amount = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=50, choices=[('success','SUCCESS'), ('failed', 'FAILED')])


class UserLoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    browser = models.CharField(max_length=250, null=True, blank=True)
    os = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)