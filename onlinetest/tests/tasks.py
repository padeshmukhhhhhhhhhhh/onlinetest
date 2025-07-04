from celery import shared_task
from .models import StudentTestSession
from .utils import calculate_and_submit_test  

@shared_task
def auto_submit_test(session_id):
    try:
        session = StudentTestSession.objects.get(id=session_id)
        calculate_and_submit_test(session)  
    except StudentTestSession.DoesNotExist:
        pass
