import os
import django
import sys

print("Setting up Django environment...")
# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumipay.settings")
try:
    django.setup()
    print("  Django environment set up successfully")
except Exception as e:
    print(f"  Error setting up Django: {e}")
    sys.exit(1)

from django.core.mail import send_mail
from django.conf import settings

print("\n=== Testing Email Configuration ===")
print(f"SMTP Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"Using TLS: {settings.EMAIL_USE_TLS}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 32 + "\n")

try:
    recipient = input("Enter your email address to receive the test: ").strip()
    if not recipient:
        recipient = "kingsleydike318@gmail.com"  # Fallback email
        print(f"Using default test email: {recipient}")

    print("\nSending test email...")
    send_mail(
        "Test Email from LumiPay",
        "This is a test email from LumiPay.\n\nIf you received this, your email configuration is working correctly!",
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=False,
    )
    print("\n  Test email sent successfully!")
    print("Please check your Mailtrap inbox at: https://mailtrap.io/inbox")
    print(
        "If you don't see the email, check your spam folder or the Mailtrap spam score."
    )

except Exception as e:
    print(f"\n  Failed to send test email: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Verify your Mailtrap credentials in the .env file")
    print("2. Check your internet connection")
    print("3. Try disabling any VPN or proxy")
    print("4. Verify Mailtrap's status at https://mailtrap.status.io/")
    print("\nError details:", str(e))
