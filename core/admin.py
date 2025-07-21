from django.contrib import admin
from core.models import (
    User,
    Plan,
    Subscription,
    Payment,
    UserLoginHistory,
)

# Register your models here.

@admin.register(User)
class UserAdminView(admin.ModelAdmin):
    list_display = [
        'email',
        'password', 
        'first_name', 
        'last_name', 
        'is_superuser', 
        'is_staff', 
        'is_active',
    ]


@admin.register(Plan)
class PlanAdminView(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
        'duration',
        'number_url',
        'number_qr',
        'api_access',
        'bulk_url_short',
        'details',
        'subs_count',
        'created_at',
        'updated_at',
    ]

@admin.register(Subscription)
class SubscriptionAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'plan',
        'used_urls',
        'expires_at',
    ]

@admin.register(Payment)
class PaymentAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'plan',
        'payment_id',
        'amount',
        'timestamp',
        'payment_status',
    ]


@admin.register(UserLoginHistory)
class UserLoginHistoryAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'ip_address',
        'browser',
        'os',
        'country',
        'city',
        'login_time',
    ]