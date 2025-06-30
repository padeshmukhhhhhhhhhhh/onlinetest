from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(StudentTestSession)
admin.site.register(StudentAnswer)
