from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ======================================================
# 🔹 STUDENT MODEL (NO MOBILE)
# ======================================================

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    # ✅ When Student deleted → delete related User
    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()


# ======================================================
# 🔹 QUIZ MODEL
# ======================================================

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    total_questions = models.IntegerField()
    status = models.CharField(
        max_length=10,
        choices=(("Active", "Active"), ("Inactive", "Inactive")),
        default="Active"
    )

    def __str__(self):
        return self.title


# ======================================================
# 🔹 QUESTION MODEL
# ======================================================

class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(
        max_length=1,
        choices=(
            ('A', 'Option A'),
            ('B', 'Option B'),
            ('C', 'Option C'),
            ('D', 'Option D'),
        )
    )

    def __str__(self):
        return self.question_text


# ======================================================
# 🔹 QUIZ ATTEMPT MODEL
# ======================================================

class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True, null=True)
    is_mix = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    current_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject or 'MIX'}"


# ======================================================
# 🔹 ATTEMPT ANSWER MODEL
# ======================================================

class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField()


# ======================================================
# 🔥 PASSWORD RESET OTP MODEL (FOR FORGOT PASSWORD)
# ======================================================

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"


# ======================================================
# 🔥 EMAIL REGISTRATION OTP MODEL (FOR REGISTER)
# ======================================================

class EmailRegistrationOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.otp}"