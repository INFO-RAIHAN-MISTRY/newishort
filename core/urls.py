from django.urls import path, include
from .views import (
    home,
    dashboard,
    check_url,
    manage_urls,
    manage_plans,
    bulk_url_short,
    manage_qrcodes,
    check_out,
    payment_success,
    get_url_data,
    update_url,
    login_activities,
    delete_url,
    delete_qr,
    bulk_shorted_urls,
    delete_bulk_url,
    url_analytics,
    export_bulk_url_short,
    pricing,
    reset_password,
    error,
    status_update
)

# app name ...
app_name = 'core'

urlpatterns = [
    #frontend Urls..
    path('', home, name='Home'),
    path('home/pricing/', pricing, name="pricing"),
    path('<slug>/', check_url, name="Check_Url"),
    path('error/404/', error, name="error"),

    # Dashboard Urls...
    path('user/dashboard/', dashboard, name="User_Dashboard"),
    path('user/manage-urls/', manage_urls, name="Manage_Urls"),
    path('user/manage-plan/', manage_plans, name="Manage_Plan"),
    path('user/bulk-url-short/', bulk_url_short, name="Bulk_Url_Short"),
    path('user/manage-qrs/', manage_qrcodes, name="Manage_QR_codes"),
    path('user/checkout/plan/', check_out, name="Check_Out"),
    path('user/payment/success/', payment_success, name="Payment_Success"),
    path('user/get_url_data/<id>', get_url_data, name="get_url_data"),
    path('user/update_url/<id>', update_url, name="update_url"),
    path('user/login/activities', login_activities, name="login_activities"),
    path('user/url/delete/', delete_url, name="delete_url"),
    path('user/qr/delete', delete_qr, name="delete_qr"),
    path('user/bulk/shorted/urls', bulk_shorted_urls, name="bulk_shorted_urls"),
    path('user/bulk/url/delete', delete_bulk_url, name="delete_bulk_url"),
    path('user/analytical/url/view',url_analytics,name='url_analytics'),
    path('user/export_bulk_url_short/', export_bulk_url_short, name='export_bulk_url_short_csv'),
    path('user/reset/password/', reset_password, name="reset_password"),
    path('user/url/status/<id>/', status_update, name="status_update")
]
