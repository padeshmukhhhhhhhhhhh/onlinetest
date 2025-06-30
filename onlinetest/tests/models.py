from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.INSTRUCTOR)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)  
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        INSTRUCTOR = "instructor", "Instructor"
        STUDENT = "student", "Student"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
   

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField()
    
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tests',
        limit_choices_to={'role': 'instructor'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Question(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return f"Question {self.id} for Test: {self.test.title}"


class StudentTestSession(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='test_sessions'
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='student_sessions'
    )
    start_time = models.DateTimeField()
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.email} - {self.test.title}"


class StudentAnswer(models.Model):
    session = models.ForeignKey(
        StudentTestSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Session {self.session.id} "
