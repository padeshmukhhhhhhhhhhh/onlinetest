import random
from django.core.mail import send_mail
from .models import *
from django.utils import timezone

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


def calculate_and_submit_test(session):
   

    if session.submitted:
        return  

    answers = StudentAnswer.objects.filter(session=session)
    score = sum([1 for answer in answers if answer.is_correct])

    session.score = score
    session.submitted = True
    session.submitted_at = timezone.now()
    session.save()