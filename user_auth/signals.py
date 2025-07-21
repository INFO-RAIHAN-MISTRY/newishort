from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

@receiver(post_save, sender = User)
def SendConfirmationMail(sender, instance, created, **kwargs):
    if created:
        user_obj = User.objects.get(email = instance)
        if not user_obj.is_email_varified:
            send_email_after_register(user_obj.email, user_obj.email_token)

# def send_email_after_register(email, email_token):
#     subject = 'Your email id needs to be verified'
#     message = f'Hii, Press the link to verify Your Account. http://localhost:8000/auth/verify/{email_token}'
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     send_mail(subject, message, from_email, recipient_list)

def send_email_after_register(email, email_token):
    subject = 'Verify your email address !'

    # Render the HTML template and include the user's email
    verification_link = f'https://ishort.in/auth/verify/{email_token}'  # Update the link as needed
    html_message = render_to_string('email/verification-email.html', {'verification_link': verification_link, 'user_email': email})

    # Create an EmailMessage with the same HTML content for both HTML and plain text
    email = EmailMessage(
        subject,
        html_message,  # Use the same HTML content for both HTML and plain text
        settings.EMAIL_HOST_USER,
        [email],
    )
    email.content_subtype = 'html'  # Set the content type to HTML
    email.send()
