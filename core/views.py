from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html
import razorpay
from django.conf import settings
from core.models import (
    User,
    Plan,
    Subscription,
    Payment,
    UserLoginHistory,
)
from functions.models import (
    Url,
    BulkUrlShort,
    QrCode,
    UrlHitDetail,
)
from functions.utils import (
    parse_csv_file,
)

from django.core.paginator import Paginator
import random
import string
from django.db.models import Avg, Max, Min, Sum, Count
import json
import pandas as pd
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Frontend View...

def check_url(request, slug):
    try:
        # Get the URL object associated with the short URL slug
        url_obj = Url.objects.get(short_url=slug)

        if url_obj.status is True:

            # Get the URL object associated with the short URL slug
            url_obj = Url.objects.get(short_url=slug)

            # Create a UrlHitDetail instance to store hit details
            hit_detail = UrlHitDetail(url=url_obj)
            hit_detail.visitor_ip = request.META.get('REMOTE_ADDR')
            print(hit_detail.visitor_ip)
            
            # Get visitor info once and store the values in variables
            country, city, coordinates, region = hit_detail.get_visitor_info(request)

            # Set the country and city in the hit_detail instance
            hit_detail.country = country
            hit_detail.city = city
            hit_detail.coordinates = coordinates
            hit_detail.region = region

            # Call the parse_user_agent() method to populate browser and OS details
            hit_detail.parse_user_agent(request)

            hit_detail.hit_time = timezone.now()

            hit_detail.save()

            url_obj.url_hit_count = url_obj.url_hit_count+1
            url_obj.save()

            return redirect(url_obj.long_url)
        
        else:
            return redirect('core:error')

    except Url.DoesNotExist:
        try:
            url_obj = BulkUrlShort.objects.get(short_url = slug)
            url_obj.url_hit_count = url_obj.url_hit_count+1
            url_obj.save()
            return redirect(url_obj.long_url)
        
        except BulkUrlShort.DoesNotExist:
            return redirect('core:error')

def home(request):
    return render(request, 'Basic/index.html')


def pricing(request):
    return render(request, 'Basic/pricing.html')


# Dashboard Views...

@login_required(login_url='user_auth:auth_login')
def dashboard(request):
    payment_obj = Payment.objects.filter(user = request.user).order_by('-timestamp')[:7]
    url_obj = Url.objects.filter(user = request.user).all().count()
    total_hit_count = (
        Url.objects.filter(user = request.user).aggregate(total_hits=Sum('url_hit_count', default=0))['total_hits'] +
        BulkUrlShort.objects.filter(user = request.user).aggregate(total_hits=Sum('url_hit_count', default=0))['total_hits']
    )
    bulk_url_obj = BulkUrlShort.objects.filter(user = request.user).all().count()
    qr_obj = QrCode.objects.filter(user = request.user).all().count()

    context = {
        'transctions':payment_obj,
        'url_obj': url_obj,
        'total_hit_count': total_hit_count,
        'bulk_url_obj': bulk_url_obj,
        'qr_obj': qr_obj,
    }
    return render(request,'Dashboard/index.html', context)


@login_required(login_url='user_auth:auth_login')
def manage_urls(request):
    subscrption = Subscription.objects.get(user = request.user)
    now = timezone.now()

    # Check if subscrption has expired or not
    if subscrption.expires_at < now:
        messages.error(request, f"dear, {request.user} your plan has been expired, Subscribe a new plan to continue our services.")
    
    if subscrption.used_urls < subscrption.plan.number_url:
        if request.method == "POST":
            long_url = request.POST['long_url']
            url_title = request.POST['url_title']
            random_short = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
            url_create = Url.objects.create(
                user = request.user,
                short_url = str(random_short),
                long_url = long_url,
                url_title = url_title,
            )

            if url_create:
                subscrption.used_urls += 1
                subscrption.save()

                messages.success(request, f"Short url of {url_title} is created successfully.")
                return redirect('core:Manage_Urls')
            else:
                messages.error(request, f"Short url of {url_title} is not create yet, due to some issues!")
                return redirect('core:Manage_Urls')
    else:
        messages.error(request, format_html(f"Dear, {request.user} you have reached your limit as your active plan, if you want to access more of our features then subscribe our Premium plans from Manage Plans !"))

    url_obj = Url.objects.filter(user = request.user).order_by('-id')
    paginator = Paginator(url_obj, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'urls': page_obj,
    }

    return render(request, 'Dashboard/manage-urls.html', context)

@login_required(login_url='user_auth:auth_login')
def manage_plans(request):
    subscription_obj = Subscription.objects.get(user = request.user)
    plan_obj = Plan.objects.all()
    context = {
        "plans":plan_obj,
        "subscription": subscription_obj.plan.name
    }
    return render(request, 'Dashboard/plans.html', context)

@login_required(login_url='user_auth:auth_login')
def bulk_url_short(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        urls = parse_csv_file(excel_file)
        batch_size = 100
        total_urls = len(urls)
        shortened_urls = []
        progress_data_list = []  # Initialize an empty list to store progress data

        for start_idx in range(0, total_urls, batch_size):
            end_idx = start_idx + batch_size
            batch_urls = urls[start_idx:end_idx]

            for url in batch_urls:
                short_url = BulkUrlShort.objects.create(user=request.user, long_url=url)
                shortened_urls.append(short_url)

        # Calculate the count of shortened URLs
        num_shortened_urls = len(shortened_urls)

        # Set a success message in the session
        success_message = f'{num_shortened_urls} URLs shortened successfully.'
        messages.success(request, success_message)

        # Create a JSON response with the success message and progress data list
        response_data = {
            'success': True,
            'message': success_message,
        }

        return JsonResponse(response_data)

    return render(request, 'Dashboard/bulk-url-short.html')


@login_required(login_url='user_auth:auth_login')
def manage_qrcodes(request):
    subscrption = Subscription.objects.get(user = request.user)
    now = timezone.now()

    # Check if subscrption has expired or not
    if subscrption.expires_at < now:
        messages.error(request, f"dear, {request.user} your plan has been expired, Subscribe a new plan to continue our services.")

    if subscrption.used_qrs < subscrption.plan.number_qr:
        if request.method == "POST":
            long_url = request.POST['long_url']
            url_title = request.POST['url_title']
            qr_create = QrCode.objects.create(
                user = request.user,
                long_url = long_url,
                title = url_title,
            )

            if qr_create:
                subscrption.used_urls += 1
                subscrption.save()
                messages.success(request, f"QR code of {url_title} is created successfully.")
                return redirect('core:Manage_QR_codes')
            
            else:
                messages.error(request, f"QR code of {url_title} is not create yet, due to some issues!")
                return redirect('core:Manage_QR_codes')
    else:
        messages.error(request, format_html(f"Dear, {request.user} you have reached your limit as your active plan, if you want to access more of our features then subscribe our Premium plans from Manage Plans !"))

    qr_obj = QrCode.objects.filter(user = request.user)
    context = {
        'qrs': qr_obj,
    }

    return render(request, 'Dashboard/manage-qrs.html', context)

@login_required(login_url='user_auth:auth_login')
def check_out(request):
    if request.method == "POST":
        plan_obj = Plan.objects.get(id = request.POST['plan_id'])

        # Razorpay Gateway Settings --> 

        RAZOR_client = razorpay.Client(auth=(settings.RAZOR_KEY, settings.RAZOR_KEY_SECRET))
        RAZOR_payment = RAZOR_client.order.create({'amount': plan_obj.price * 100, "currency" : "INR", "payment_capture":1})

        print(RAZOR_payment)

        subs_obj = Subscription.objects.get(user = request.user)
        subs_obj.razorpay_payment_id = RAZOR_payment['id']
        subs_obj.save()
    
    context = {
        'plan': plan_obj,
        'payment': RAZOR_payment,
    }
    return render(request, 'Dashboard/checkout.html', context)

@login_required(login_url="account_login")
def payment_success(request):
    order_id = request.GET.get('razorpay_order_id')
    plan = request.GET.get('plan_id')
    subscription_obj = Subscription.objects.get(razorpay_payment_id = order_id)
    new_plan_id = Plan.objects.get(id = plan)
    new_plan_id.subs_count += 1
    new_plan_id.save()
    expires_at = datetime.now() + timedelta(days = new_plan_id.duration)
    subscription_obj.user = request.user
    subscription_obj.plan = new_plan_id
    subscription_obj.expires_at = expires_at
    subscription_obj.save()
    send_email_after_subscribe(request.user.email, plan)

    Payment.objects.create(
        user = request.user,
        plan = new_plan_id,
        payment_id = subscription_obj.razorpay_payment_id,
        amount = subscription_obj.plan.price,
        payment_status = 'success',
    )

    return render(request, 'Dashboard/payment-success.html')


def send_email_after_subscribe(email, plan):
    subject = 'Thank You For Subscribe !'
    plan_obj = Plan.objects.get(id = plan)
    # Render the HTML template and include the user's email
    html_message = render_to_string('email/subscribe.html', {'user_email':email, 'plan':plan_obj})

    # Create an EmailMessage with the same HTML content for both HTML and plain text
    email = EmailMessage(
        subject,
        html_message,  # Use the same HTML content for both HTML and plain text
        settings.EMAIL_HOST_USER,
        [email],
    )
    email.content_subtype = 'html'  # Set the content type to HTML
    email.send()


def get_url_data(request, id):
    url_obj = Url.objects.get(id = id)

    data = {
        'short_url': url_obj.short_url,
        'url_title': url_obj.url_title,
        'long_url' : url_obj.long_url,
    }
    print(data)
    return JsonResponse(data)


def update_url(request, id):
    if request.method == "POST":
        short_url = request.POST.get('short_url')
        url_title = request.POST.get('url_title')
    
        url_obj = Url.objects.get(id = id)
        if Url.objects.filter(short_url = short_url).first():
            messages.error(request, "Duplicate entry, try again !!")
        else:
            url_obj.short_url = short_url
            url_obj.url_title = url_title
            url_obj.save()
            messages.success(request,f'{url_title} update successfully')
            return JsonResponse({'success':True})
    
    return JsonResponse({'fail':True})

def login_activities(request):
    login_history_obj = UserLoginHistory.objects.filter(user = request.user).order_by('-id')
    paginator = Paginator(login_history_obj, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'activities' : page_obj
    }
    return render(request, 'Dashboard/login-activities.html', context)

def delete_url(request):
    element_id = request.GET.get('element_id')
    try:
        url_obj = Url.objects.get(id = element_id)
        url_obj.delete()
        return JsonResponse({'message':'Element Deleted Successfully'})
    
    except Exception as e:
        print(e)

    return JsonResponse({'message':'invalid request'}, status=400)

def delete_qr(request):
    element_id = request.GET.get('element_id')
    try:
        qr_obj = QrCode.objects.get(id = element_id)
        qr_obj.delete()
        return JsonResponse({'message':'Element Deleted Successfully'})
    
    except Exception as e:
        print(e)

    return JsonResponse({'message':'invalid request'}, status=400)

def bulk_shorted_urls(request):
    # Initialize message and count variables
    message = None

    # Retrieve the message and count from the query parameters
    message_param = request.GET.get('message')

    # Check if message_param is not empty or None
    if message_param:
        message = message_param

    bulk_url_obj = BulkUrlShort.objects.filter(user = request.user).order_by('-id')
    paginator = Paginator(bulk_url_obj, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'urls':page_obj,
        'message': message,
    }
    return render(request, 'Dashboard/bulk-sorted-urls.html', context)

def delete_bulk_url(request):
    element_id = request.GET.get('element_id')
    try:
        url_obj = BulkUrlShort.objects.get(id = element_id)
        url_obj.delete()
        return JsonResponse({'message':'Element Deleted Successfully'})
    
    except Exception as e:
        print(e)

    return JsonResponse({'message':'invalid request'}, status=400)

def url_analytics(request):
    url_obj = Url.objects.get(id = request.GET['url_id'])
    analytical_obj = UrlHitDetail.objects.filter(url = url_obj).order_by("-id")
    analytical_data = UrlHitDetail.objects.filter(url = url_obj).values('country').annotate(hit_count=Count('country')).order_by('-hit_count')
    analytical_data_browser = UrlHitDetail.objects.filter(url=url_obj).values('browser').annotate(hit_count=Count('browser')).order_by('-hit_count')

    
    markers = []
    for data in analytical_data:
        country = data['country']
        hit_count = data['hit_count']
        
        # Fetch coordinates from UrlHitDetail model
        url_hit_detail = UrlHitDetail.objects.filter(url=url_obj, country=country).first()
        if url_hit_detail:
            coordinates = url_hit_detail.coordinates
            region = url_hit_detail.region
        else:
            coordinates = None
            region = None
        
        markers.append({
            'country': country,
            'hit_count': hit_count,
            'coordinates': coordinates,
            'region': region,
        })
    
    browser_data = []
    for data in analytical_data_browser:
        browser = data['browser']
        hit_count = data['hit_count']

        browser_data.append({
            'browser': browser,
            'hit_count': hit_count,
        })
    
    browser_data_json = json.dumps(browser_data)

    context = {
        'url': url_obj,
        'analytical_url': analytical_obj,
        'marker': markers,
        'browser_data': browser_data_json,
        'browser': browser_data,
    }

    return render(request,'Dashboard/analitycal-view.html', context)


def export_bulk_url_short(request):
    # Fetch data for a specific user (modify the query as needed)
    user = request.user  # or any other method to get the user
    data = BulkUrlShort.objects.filter(user=user)

    # Define the filename
    filename = f"bulk_url_short_{user.email}.csv"

    # Create a response with the appropriate content type and headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a DataFrame from the queryset
    df = pd.DataFrame(data.values())

    # Set column headers
    df.columns = ['id', 'user_id', 'short_url', 'long_url', 'url_title', 'url_hit_count', 'url_created_at', 'url_updated_at']

    # Write the DataFrame to the response
    df.to_csv(response, index=False)

    return response


def reset_password(request):
    if request.method == "POST":
        new_pass = request.POST['new_pass']

        user_obj = User.objects.get(id = request.user.id)
        user_obj.set_password(new_pass)

        messages.success(request, "Password successfully changed. You need's to re-login if session destroy !")
        return redirect('core:User_Dashboard')
    

def error(request):
    return render(request, '404.html')

def status_update(request, id):
    url_obj = Url.objects.get(id = id)

    if url_obj.status is True:
        url_obj.status = False
        url_obj.save()

    else:
        url_obj.status = True
        url_obj.save()

    messages.success(request, "Url status updated !")
    return redirect('core:Manage_Urls')
