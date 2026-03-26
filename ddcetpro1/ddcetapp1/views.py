from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.conf import settings
from .models import PasswordResetOTP
from .models import Student, Quiz, Question, QuizAttempt, AttemptAnswer
import random
import time
from .models import EmailRegistrationOTP
from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
import threading

# ================= HOME =================

def ddcet(request):
    return render(request, 'ddcet.html')


# =================== REGISTER ==================

def register(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ================= VALIDATION =================

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('register')

        # ================= GENERATE EMAIL OTP =================

        otp = str(random.randint(100000, 999999))

        EmailRegistrationOTP.objects.filter(email=email).delete()

        EmailRegistrationOTP.objects.create(
            email=email,
            otp=otp
        )

        # Store registration data in session
        request.session['reg_data'] = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "email": email,
            "password": password,
        }

        from django.core.mail import EmailMultiAlternatives

        subject = "DDCET Registration OTP"

        text_content = f"Your OTP is {otp}"

        html_content = f"""
        <html>
        <body style="background:#f4f4f4; font-family:Arial; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:10px;">
        <h2 style="color:#1f3b6d;">DDCET Account Verification</h2>
        <p>Use the OTP below to verify your account:</p>

        <div style="text-align:center; margin:30px;">
        <h1 style="background:#1f3b6d; color:white; padding:15px 25px; display:inline-block; border-radius:8px;">
        {otp}
        </h1>
        </div>

        <p style="color:gray;">Valid for 10 minutes.</p>
        </div>
        </body>
        </html>
        """

        email_msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )

        email_msg.attach_alternative(html_content, "text/html")

        def send_email_async(subject, text_content, html_content, to_email):
            try:
                email_msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [to_email]
                )
                email_msg.attach_alternative(html_content, "text/html")
                email_msg.send(fail_silently=True)
                print("✅ EMAIL SENT")
            except Exception as e:
                print("❌ EMAIL ERROR:", e)

        threading.Thread(
            target=send_email_async,
            args=(subject, text_content, html_content, email)
        ).start()
        messages.success(request, "OTP sent to your email.")
        return redirect('verify_email_otp')

    return render(request, 'register.html')


# ================= VERIFY EMAIL OTP =================

def verify_email_otp(request):

    reg_data = request.session.get('reg_data')

    if not reg_data:
        return redirect('register')

    email = reg_data.get("email")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_obj = EmailRegistrationOTP.objects.get(
                email=email,
                otp=entered_otp,
                is_verified=False
            )
        except EmailRegistrationOTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return redirect('verify_email_otp')

        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(request, "OTP expired.")
            return redirect('register')

        otp_obj.is_verified = True
        otp_obj.save()

        # 🔥 CREATE USER AFTER OTP VERIFIED
        user = User.objects.create_user(
            username=reg_data["username"],
            email=reg_data["email"],
            password=reg_data["password"],
            first_name=reg_data["first_name"],
            last_name=reg_data["last_name"]
        )

        Student.objects.create(user=user)

        request.session.pop('reg_data', None)
        EmailRegistrationOTP.objects.filter(email=email).delete()

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, "verify-email-otp.html")


# ================= RESEND EMAIL OTP =================

def resend_email_otp(request):

    reg_data = request.session.get('reg_data')

    if not reg_data:
        return JsonResponse({
            "status": "error",
            "message": "Session expired. Please register again."
        })

    email = reg_data.get("email")

    otp = str(random.randint(100000, 999999))

    # Delete old OTP
    EmailRegistrationOTP.objects.filter(email=email).delete()

    # Create new OTP
    EmailRegistrationOTP.objects.create(
        email=email,
        otp=otp
    )

    from django.core.mail import EmailMultiAlternatives

    subject = "DDCET Registration OTP"

    text_content = f"Your OTP is {otp}"

    html_content = f"""
    <html>
    <body style="background:#f4f4f4; font-family:Arial; padding:20px;">
    <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:10px;">
    <h2 style="color:#1f3b6d;">DDCET Account Verification</h2>
    <p>Use the OTP below to verify your account:</p>

    <div style="text-align:center; margin:30px;">
    <h1 style="background:#1f3b6d; color:white; padding:15px 25px; display:inline-block; border-radius:8px;">
    {otp}
    </h1>
    </div>

    <p style="color:gray;">Valid for 10 minutes.</p>
    </div>
    </body>
    </html>
    """

    email_msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )

    email_msg.attach_alternative(html_content, "text/html")

    try:
        email_msg.send(fail_silently=False)
        print("✅ RESEND EMAIL SUCCESS")
    except Exception as e:
        print("❌ RESEND EMAIL ERROR:", e)

    return JsonResponse({
        "status": "success",
        "message": "New OTP sent successfully."
    })


# ================= LOGIN =================

def login_view(request):
    if request.method == "POST":
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if role == "admin" and user.is_superuser:
                return redirect('admin_dashboard')

            if role == "student" and Student.objects.filter(user=user).exists():
                return redirect('student_dashboard')

            logout(request)
            messages.error(request, "Role mismatch")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


# ================= FORGOT PASSWORD (SEND OTP) =================

def forgot(request):

    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('forgot')

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.filter(user=user).delete()

        PasswordResetOTP.objects.create(
            user=user,
            email=email,
            otp=otp
        )

        from django.core.mail import EmailMultiAlternatives

        subject = "DDCET Password Reset Request"

        text_content = f"Your OTP is {otp}"

        email_msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )

        email_msg.send(fail_silently=False)

        request.session["otp_expiry"] = int(time.time()) + 600
        request.session["reset_email"] = email

        return redirect('verify_otp')

    return render(request, 'forgotidpassword.html')

# ================= VERIFY OTP =================

def verify_otp(request):

    if request.user.is_authenticated:
        logout(request)

    email = request.session.get("reset_email")

    if not email:
        return redirect('forgot')

    expiry_time = request.session.get("otp_expiry", 0)
    current_time = int(time.time())
    remaining_time = expiry_time - current_time

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            request.session.flush()
            return redirect('forgot')

        # 🔥 IMPORTANT CHANGE HERE
        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_obj:
            messages.error(request, "Invalid OTP.")
            return redirect('verify_otp')

        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(request, "OTP expired.")
            return redirect('forgot')

        # 🔥 Compare OTP manually (safer)
        if otp_obj.otp != entered_otp:
            messages.error(request, "Invalid OTP.")
            return redirect('verify_otp')

        # ✅ Correct OTP
        otp_obj.is_verified = True
        otp_obj.save()

        request.session["reset_user_id"] = user.id

        return redirect('reset_password')

    return render(request, "verify-otp.html", {
        "remaining_time": max(0, remaining_time)
    })


# ================= RESEND OTP =================

def resend_otp(request):

    email = request.session.get("reset_email")

    if not email:
        return JsonResponse({"status": "error", "message": "Session expired"})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"})

    otp = str(random.randint(100000, 999999))

    PasswordResetOTP.objects.filter(user=user).delete()

    PasswordResetOTP.objects.create(
        user=user,
        email=email,
        otp=otp
    )

    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    subject = "DDCET Email Verification"

    text_content = f"Your OTP is {otp}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background:#f4f4f4; font-family:Arial, sans-serif;">

        <div style="max-width:600px; margin:40px auto; background:#ffffff; padding:30px; border-radius:10px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">

            <h2 style="text-align:center; color:#1f3b6d;">DDCET Account Verification</h2>

            <p style="font-size:16px; color:#333; line-height:1.6;">
                Hello,
            </p>

            <p style="font-size:16px; color:#333; line-height:1.6;">
                Thank you for registering with <strong>DDCET Portal</strong>.
                To complete your account setup, please use the One-Time Password (OTP) provided below.
            </p>

            <p style="font-size:16px; color:#333; line-height:1.6;">
                This OTP is required to verify your email address and ensure the security of your account.
                Please do not share this code with anyone.
            </p>

            <div style="text-align:center; margin:30px 0;">
                <span style="display:inline-block; padding:15px 30px; font-size:28px; letter-spacing:6px; background:#1f3b6d; color:#fff; border-radius:8px;">
                    {otp}
                </span>
            </div>

            <p style="font-size:14px; color:#555; text-align:center;">
                This OTP is valid for 10 minutes.
            </p>

            <hr style="margin:30px 0;">

            <p style="font-size:13px; color:#888; text-align:center;">
                If you did not request this, please ignore this email.
            </p>

        </div>

    </body>
    </html>
    """

    email_msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )

    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send(fail_silently=False)

    # Reset timer
    expiry_time = int(time.time()) + 600
    request.session["otp_expiry"] = expiry_time

    return JsonResponse({
        "status": "success",
        "message": "New OTP sent",
        "remaining_time": 600
    })


# ================= RESET PASSWORD =================

def reset_password(request):

    # 🔥 Do NOT allow logged-in user interference
    if request.user.is_authenticated:
        logout(request)

    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect('forgot')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('forgot')

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('reset_password')

        # 🔥 Set password ONLY for session user
        user.set_password(password1)
        user.save()

        # Delete OTP records
        PasswordResetOTP.objects.filter(user=user).delete()

        # Clear reset session safely
        request.session.pop("reset_user_id", None)
        request.session.pop("reset_email", None)
        request.session.pop("otp_expiry", None)

        messages.success(request, "Password updated successfully.")
        return redirect('login')

    return render(request, "reset-password.html")


# ================= ADMIN DASHBOARD =================

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')

    student_count = Student.objects.count()
    active_subject_count = Quiz.objects.filter(
        status="Active"
    ).values("subject").distinct().count()
    active_quiz_count = Quiz.objects.filter(status="Active").count()

    return render(request, 'admin-dashboard.html', {
        "student_count": student_count,
        "active_subject_count": active_subject_count,
        "active_quiz_count": active_quiz_count,
    })


# ================= ADMIN SUBJECTS PAGE =================

@login_required
def admin_subjects(request):
    if not request.user.is_superuser:
        return redirect('login')

    subjects = Quiz.objects.values('subject').distinct()

    subject_list = []

    for index, sub in enumerate(subjects, start=1):
        subject_name = sub['subject']

        quizzes = Quiz.objects.filter(subject=subject_name)

        active_count = quizzes.filter(status="Active").count()
        inactive_count = quizzes.filter(status="Inactive").count()

        subject_list.append({
            "sr": index,
            "subject": subject_name,
            "total_quizzes": quizzes.count(),
            "active": active_count,
            "inactive": inactive_count
        })

    return render(request, 'admin-subjects.html', {
        "subjects": subject_list
    })


# ================= ADMIN STUDENTS PAGE =================

@login_required
def admin_students(request):
    if not request.user.is_superuser:
        return redirect('login')

    students = User.objects.filter(is_superuser=False).order_by('first_name')

    return render(request, 'admin-students.html', {
        "students": students,
        "total_students": students.count()
    })


# ================= STUDENT DASHBOARD =================

@login_required
def student_dashboard(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    student = get_object_or_404(Student, user=request.user)

    active_subject_count = Quiz.objects.filter(
        status="Active"
    ).values("subject").distinct().count()

    mix_attempts = QuizAttempt.objects.filter(
        student=student,
        is_mix=True
    ).order_by('-created_at')[:5]

    subject_attempts = QuizAttempt.objects.filter(
        student=student,
        is_mix=False
    ).order_by('-created_at')[:5]

    return render(request, 'student-dashboard.html', {
        "active_subject_count": active_subject_count,
        "mix_attempts": mix_attempts,
        "subject_attempts": subject_attempts,
    })# ================= PROFILES =================

@login_required
def admin_profile(request):
    if not request.user.is_superuser:
        return redirect('login')

    return render(request, 'admin-profile.html')


@login_required
def student_profile(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    return render(request, 'student-profile.html')


# ================= QUIZ MANAGEMENT (ADMIN) =================

@login_required
def admin_quizzes(request):
    if not request.user.is_superuser:
        return redirect('login')

    quizzes = Quiz.objects.all()
    return render(request, 'admin-quizzes.html', {"quizzes": quizzes})


@login_required
def add_quiz(request):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == "POST":
        Quiz.objects.create(
            title=request.POST['title'],
            subject=request.POST['subject'],
            total_questions=request.POST['total_questions'],
            status=request.POST['status']
        )
        return redirect('admin_quizzes')

    return render(request, 'add-quiz.html')


@login_required
def view_quiz(request, quiz_id):
    if not request.user.is_superuser:
        return redirect('login')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'view-quiz.html', {"quiz": quiz})


@login_required
def modify_quiz(request, quiz_id):
    if not request.user.is_superuser:
        return redirect('login')

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        quiz.total_questions = request.POST['total_questions']
        quiz.status = request.POST['status']
        quiz.save()
        return redirect('admin_quizzes')

    return render(request, 'modify-quiz.html', {"quiz": quiz})


@login_required
def delete_quiz(request, quiz_id):
    if not request.user.is_superuser:
        return redirect('login')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('admin_quizzes')


# ================= ADD QUESTIONS (ADMIN) =================

@login_required
def add_questions(request, quiz_id):
    if not request.user.is_superuser:
        return redirect('login')

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        Question.objects.create(
            quiz=quiz,
            question_text=request.POST['question'],
            option_a=request.POST['option_a'],
            option_b=request.POST['option_b'],
            option_c=request.POST['option_c'],
            option_d=request.POST['option_d'],
            correct_option=request.POST['correct_option']
        )
        return redirect('add_questions', quiz_id=quiz.id)

    questions = Question.objects.filter(quiz=quiz).order_by('id')

    return render(request, 'add-questions.html', {
        "quiz": quiz,
        "questions": questions
    })


# ================= PRACTICE OPTIONS =================

@login_required
def practice_options(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    return render(request, 'practice-options.html')


# ================= SUBJECT LIST =================

@login_required
def subject_wise(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    subjects = Quiz.objects.filter(
        status="Active"
    ).values_list("subject", flat=True).distinct()

    return render(request, 'subject-wise.html', {
        "subjects": subjects
    })


# ================= MIX QUIZ =================

@login_required
def mix_quiz(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    student = get_object_or_404(Student, user=request.user)

    if 'mix_qids' not in request.session:

        qids = list(
            Question.objects.filter(
                quiz__status="Active"
            ).values_list('id', flat=True)
        )

        random.shuffle(qids)

        request.session['mix_qids'] = qids[:10]
        request.session['mix_index'] = 0
        request.session['mix_score'] = 0

        total_time = len(request.session['mix_qids']) * 90
        request.session['mix_total_time'] = total_time
        request.session['mix_start_time'] = int(time.time())

        attempt = QuizAttempt.objects.create(
            student=student,
            subject="MIX",
            is_mix=True,
            score=0,
            started_at=timezone.now()
        )

        request.session['mix_attempt_id'] = attempt.id

    index = request.session['mix_index']
    qids = request.session['mix_qids']

    total_time = request.session.get('mix_total_time')
    start_time = request.session.get('mix_start_time')

    if not total_time or not start_time:
        total_time = len(qids) * 90
        request.session['mix_total_time'] = total_time
        request.session['mix_start_time'] = int(time.time())
        start_time = request.session['mix_start_time']

    elapsed = int(time.time()) - start_time
    remaining_time = total_time - elapsed

    if remaining_time <= 0:
        remaining_time = 0

    if index >= len(qids) or remaining_time <= 0:

        score = request.session['mix_score']

        attempt_id = request.session.get('mix_attempt_id')
        if attempt_id:
            attempt = QuizAttempt.objects.get(id=attempt_id)
            attempt.score = score
            attempt.finished_at = timezone.now()

            if attempt.started_at:
                duration = (attempt.finished_at - attempt.started_at).total_seconds()
                attempt.duration_seconds = int(duration)

            attempt.save()

        request.session.pop('mix_qids', None)
        request.session.pop('mix_index', None)
        request.session.pop('mix_score', None)
        request.session.pop('mix_total_time', None)
        request.session.pop('mix_start_time', None)
        request.session.pop('mix_attempt_id', None)

        return render(request, 'mix-quiz.html', {
            "finished": True,
            "score": score
        })

    question = Question.objects.get(id=qids[index])

    options = [
        ('A', question.option_a),
        ('B', question.option_b),
        ('C', question.option_c),
        ('D', question.option_d),
    ]
    random.shuffle(options)

    if request.method == "POST":

        selected = request.POST.get('answer')
        is_correct = selected == question.correct_option

        if is_correct:
            request.session['mix_score'] += 2
        else:
            request.session['mix_score'] -= 0.5

        attempt_id = request.session.get('mix_attempt_id')
        if attempt_id:
            attempt = QuizAttempt.objects.get(id=attempt_id)

            AttemptAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected,
                is_correct=is_correct
            )

        request.session['mix_index'] += 1
        return redirect('mix_quiz')

    return render(request, 'mix-quiz.html', {
        "question": question,
        "options": options,
        "index": index + 1,
        "total": len(qids),
        "remaining_time": remaining_time,
        "current_score": request.session.get('mix_score', 0),
        "total_marks": len(qids) * 2
    })


# ================= SUBJECT QUIZ =================

@login_required
def subject_quiz(request, subject):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    student = get_object_or_404(Student, user=request.user)

    quiz = Quiz.objects.filter(
        subject=subject,
        status="Active"
    ).first()

    if not quiz:
        return redirect('practice_options')

    key = f"{subject}_qids"

    if key not in request.session:

        qids = list(
            Question.objects.filter(quiz=quiz).values_list('id', flat=True)
        )

        random.shuffle(qids)

        request.session[key] = qids[:quiz.total_questions]
        request.session['sub_index'] = 0
        request.session['sub_score'] = 0

        total_time = len(request.session[key]) * 90
        request.session['sub_total_time'] = total_time
        request.session['sub_start_time'] = int(time.time())

        attempt = QuizAttempt.objects.create(
            student=student,
            subject=subject,
            is_mix=False,
            score=0,
            started_at=timezone.now()
        )

        request.session['sub_attempt_id'] = attempt.id

    index = request.session['sub_index']
    qids = request.session[key]

    total_time = request.session.get('sub_total_time')
    start_time = request.session.get('sub_start_time')

    if not total_time or not start_time:
        total_time = len(qids) * 90
        request.session['sub_total_time'] = total_time
        request.session['sub_start_time'] = int(time.time())
        start_time = request.session['sub_start_time']

    elapsed = int(time.time()) - start_time
    remaining_time = total_time - elapsed

    if remaining_time <= 0:
        remaining_time = 0

    if index >= len(qids) or remaining_time <= 0:

        score = request.session['sub_score']

        attempt_id = request.session.get('sub_attempt_id')

        if attempt_id:
            attempt = QuizAttempt.objects.get(id=attempt_id)
            attempt.score = score
            attempt.finished_at = timezone.now()

            if attempt.started_at:
                duration = (attempt.finished_at - attempt.started_at).total_seconds()
                attempt.duration_seconds = int(duration)

            attempt.save()

        request.session.pop(key, None)
        request.session.pop('sub_index', None)
        request.session.pop('sub_score', None)
        request.session.pop('sub_total_time', None)
        request.session.pop('sub_start_time', None)
        request.session.pop('sub_attempt_id', None)

        return render(request, 'subject-quiz.html', {
            "finished": True,
            "score": score,
            "subject": subject
        })

    question = Question.objects.get(id=qids[index])

    options = [
        ('A', question.option_a),
        ('B', question.option_b),
        ('C', question.option_c),
        ('D', question.option_d),
    ]
    random.shuffle(options)

    if request.method == "POST":

        selected = request.POST.get('answer')

        if selected is None:
            is_correct = False
        elif selected == question.correct_option:
            request.session['sub_score'] += 2
            is_correct = True
        else:
            request.session['sub_score'] -= 0.5
            is_correct = False

        attempt_id = request.session.get('sub_attempt_id')
        if attempt_id:
            attempt = QuizAttempt.objects.get(id=attempt_id)

            AttemptAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected,
                is_correct=is_correct
            )

        request.session['sub_index'] += 1
        return redirect('subject_quiz', subject=subject)

    return render(request, 'subject-quiz.html', {
        "question": question,
        "options": options,
        "index": index + 1,
        "total": len(qids),
        "subject": subject,
        "correct_option": question.correct_option,
        "remaining_time": remaining_time,
        "current_score": request.session.get('sub_score', 0),
        "total_marks": len(qids) * 2
    })
# ======================================================
# ================= RECENT ACTIVITY ====================
# ======================================================

@login_required
def recent_activity(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    return render(request, 'recent-activity.html')


@login_required
def recent_mix_attempts(request):
    student = get_object_or_404(Student, user=request.user)

    attempts = QuizAttempt.objects.filter(
        student=student,
        is_mix=True
    ).order_by('-created_at')[:5]

    return render(request, 'recent-mix-attempts.html', {
        "attempts": attempts
    })


@login_required
def recent_subject_attempts(request):
    student = get_object_or_404(Student, user=request.user)

    attempts = QuizAttempt.objects.filter(
        student=student,
        is_mix=False
    ).order_by('-created_at')[:5]

    return render(request, 'recent-subject-attempts.html', {
        "attempts": attempts
    })


@login_required
def attempt_detail(request, attempt_id):
    student = get_object_or_404(Student, user=request.user)

    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        student=student
    )

    answers = AttemptAnswer.objects.filter(
        attempt=attempt
    ).select_related('question')

    if attempt.is_mix:
        template_name = "mix-attempt-detail.html"
    else:
        template_name = "subject-attempt-detail.html"

    return render(request, template_name, {
        "attempt": attempt,
        "answers": answers
    })


# ================= SCORES PAGE =================

@login_required
def scores_view(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    student = get_object_or_404(Student, user=request.user)

    attempts = QuizAttempt.objects.filter(
        student=student
    ).order_by('-created_at')

    results = []

    for attempt in attempts:
        total_questions = AttemptAnswer.objects.filter(attempt=attempt).count()
        total_marks = total_questions * 2

        percentage = 0
        if total_marks > 0:
            percentage = (attempt.score / total_marks) * 100

        results.append({
            "id": attempt.id,
            "type": "Mix" if attempt.is_mix else attempt.subject,
            "marks": attempt.score,
            "percentage": round(percentage, 2)
        })

    return render(request, "scores.html", {
        "results": results
    })


# ================= SUBJECTS PAGE =================

@login_required
def subjects_view(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    subjects = Quiz.objects.filter(
        status="Active"
    ).values_list("subject", flat=True).distinct()

    return render(request, "subjects.html", {
        "subjects": subjects
    })


# ================= STUDY MATERIAL SUBJECT LIST =================

@login_required
def materials_view(request):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    subjects = Quiz.objects.filter(
        status="Active"
    ).values_list("subject", flat=True).distinct()

    return render(request, "materials.html", {
        "subjects": subjects
    })


# ================= MATERIAL DETAIL PAGE =================

@login_required
def material_detail_view(request, subject):
    if not Student.objects.filter(user=request.user).exists():
        return redirect('login')

    return render(request, "material-detail.html", {
        "subject": subject
    })


# ================= LOGOUT =================

def logout_view(request):
    logout(request)
    return redirect('login')