import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    send_mail(
        subject='Your OTP for Login',
        message=f'Your OTP is: {otp}',
        from_email='djnagomail@gmail.com',
        recipient_list=[to_email],
        fail_silently=False,
    )
