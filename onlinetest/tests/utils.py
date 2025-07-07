import random
from django.core.mail import send_mail
from .models import *
from django.utils import timezone
from dotenv import load_dotenv
import logging
import requests
import os
import json
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



logger = logging.getLogger(__name__)

load_dotenv()

class CustomResponse(Response):
    def __init__(self, st, message, data=None, errors=None, status_code=status.HTTP_200_OK):
        response_data = {
            "st": st,
            "message": message
            
        }
        
        if st == 1:
            response_data["data"] = data
        elif st == 2:
            response_data["errors"] = errors
        
        super().__init__(response_data, status=status_code)

def generate_otp():
    return str(random.randint(100000, 999999))

# def send_otp_email(to_email, otp):
#     send_mail(
#         subject='Your OTP for Login',
#         message=f'Your OTP is: {otp}',
#         from_email='djnagomail@gmail.com',
#         recipient_list=[to_email],
#         fail_silently=False,
#     )

def send_otp_email(email, otp, user):
    subject = 'Your OTP Code'
    from_email = 'djnagomail@gmail.com'
    to = [email]

    
    html_content = render_to_string('otp_email.html', {
        'user': user,
        'otp': otp
    })

    
    text_content = f'Your OTP code is {otp}'

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()



def calculate_and_submit_test(session):
    if session.submitted:
        return

    answers = StudentAnswer.objects.filter(session=session)
    total_questions = session.test.questions.count()
    correct_answers = answers.filter(is_correct=True).count()

    logger.info(f"Total Marks: {session.test.total_marks}")
    logger.info(f"Total Questions: {total_questions}")
    logger.info(f"Correct Answers: {correct_answers}")

    if total_questions == 0:
        score = 0
    else:
        marks_per_question = session.test.total_marks / total_questions
        logger.info(f"Marks Per Question: {marks_per_question}")
        score = round(correct_answers * marks_per_question)

    logger.info(f"Final Score: {score}")

    session.score = score
    session.submitted = True
    session.submitted_at = timezone.now()
    session.save()





def generate_questions_prompt(title, num_questions):
    return f"""
    Generate {num_questions} multiple-choice questions for a Python test titled: "{title}". 
    Each question should be returned in the following JSON format:

    {{
    "text": "Question text here",
    "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
    }},
    "correct_answer": "A"
    }}

    Rules:
    - Questions must be factual and relevant to the topic.
    - Ensure variety in correct options (not always A).
    - Keep text clear and concise.
    - Do NOT add explanations or comments.

    Return the output as a JSON list of {num_questions} items, and nothing else.
    """



API_URL = "https://openrouter.ai/api/v1/chat/completions"




def generate_questions_via_ai(title, num_questions):
    prompt = generate_questions_prompt(title, num_questions)
   
    try:
        

        headers = {
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(API_URL, headers=headers, data=json.dumps(data))

        
        if response.status_code != 200:
            
            return {"error": f"API request failed with status {response.status_code}"}

        
        response_data = response.json()


        
        tweet_summary = response_data['choices'][0]['message']['content']
        
       
       
        return tweet_summary

    except requests.exceptions.RequestException as e:
        
        return {"error": "Network request failed"}
    
    except KeyError:
       
        return {"error": "Invalid API response format"}
    
    except Exception as e:
        
        return {"error": "An unexpected error occurred"}


