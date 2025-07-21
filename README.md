# 🔗 Smart URL Shortener & QR Generator

A powerful and secure Django-based web application that allows users to shorten URLs, generate QR codes, and track detailed analytics. Includes advanced user authentication, subscription plans, email notifications, and session tracking.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🚀 Features

- **URL Shortening** – Generate clean, short URLs for long links.
- **QR Code Generator** – Instantly create QR codes for shortened URLs.
- **Analytics Tracking** – Monitor URL click counts, locations, devices, and more.
- **Secure Authentication** – Google OAuth2 login with two-step email verification.
- **Role-Based Access Control** – Free and premium subscription plans with feature restrictions.
- **Email Notifications** – Get updates on account activity and subscription status via SMTP.
- **Session Logging** – Track user login activity including IP address, browser, and timestamp.

---

## 🔧 Tech Stack

- **Backend**: Django, Python  
- **Database**: MySQL  
- **Authentication**: Google OAuth2, Django AllAuth  
- **Payment Gateway**: Razorpay API  
- **Frontend**: HTML, CSS, Bootstrap  
- **Email Services**: SMTP (Gmail/Yahoo etc.)

---

## 🔐 Authentication

- **Google OAuth2 Login**
- **Two-Step Email Verification**

---

## 💳 Subscription Plans

- **Free Plan**: Basic URL shortening + limited analytics
- **Premium Plan**: Unlimited short links, advanced analytics, QR features, email alerts

---

## 🛠️ Setup Instructions

```bash
# Clone the repository
git clone https://github.com/name/repo.git
cd repo

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env or settings.py for:
# - MySQL credentials
# - Google OAuth2 keys
# - SMTP email settings
# - Razorpay API keys

# Run migrations
python manage.py migrate

# Create a superuser (admin access)
python manage.py createsuperuser

# Start the server
python manage.py runserver
