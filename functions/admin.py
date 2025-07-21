from django.contrib import admin
from functions.models import (
    Url,
    ExcelFile,
    BulkUrlShort,
    QrCode,
    UrlHitDetail,
)
# Register your models here.

@admin.register(Url)
class UrlAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'short_url',
        'long_url',
        'url_title',
        'url_hit_count',
        'url_created_at',
        'url_updated_at',
    ]

@admin.register(ExcelFile)
class ExcelFileAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'excelsheet',
        'created_at',
    ]

@admin.register(BulkUrlShort)
class BulkUrlShortAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'short_url',
        'long_url',
        'url_hit_count',
        'url_created_at',
        'url_updated_at',
    ]

@admin.register(QrCode)
class QrCodeAdminView(admin.ModelAdmin):
    list_display = [
        'user',
        'long_url',
        'title',
        'qrcode',
        'created_at',
    ]

@admin.register(UrlHitDetail)
class UrlHitDetailAdminView(admin.ModelAdmin):
    list_display = [
        'url',
        'visitor_ip',
        'country',
        'city',
        'hit_time',
        'browser',
        'os',
        'coordinates',
    ]