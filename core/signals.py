from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Plan, Subscription, User
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender = User)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        user_obj = User.objects.get(email = instance)
        default_plan = Plan.objects.get(name = "Basic")
        expires_at = datetime.now() + timedelta(days = default_plan.duration)
        Subscription.objects.create(user = user_obj, plan = default_plan, expires_at = expires_at)
        default_plan.subs_count += 1
        default_plan.save()


