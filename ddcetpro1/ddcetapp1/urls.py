from django.urls import path
from . import views

urlpatterns = [

    # ================= HOME =================
    path('', views.ddcet, name='ddcet'),

    # ================= AUTH =================
    path('register/', views.register, name='register'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),
    path('resend-email-otp/', views.resend_email_otp, name='resend_email_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🔐 OTP SYSTEM
    path('forgot/', views.forgot, name='forgot'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),   # 🔥 NEW
    path('reset-password/', views.reset_password, name='reset_password'),

    # ================= ADMIN =================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('admin-students/', views.admin_students, name='admin_students'),
    path('admin-subjects/', views.admin_subjects, name='admin_subjects'),
    path('admin-quizzes/', views.admin_quizzes, name='admin_quizzes'),
    path('add-quiz/', views.add_quiz, name='add_quiz'),
    path('view-quiz/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
    path('modify-quiz/<int:quiz_id>/', views.modify_quiz, name='modify_quiz'),
    path('delete-quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('add-questions/<int:quiz_id>/', views.add_questions, name='add_questions'),

    # ================= STUDENT =================
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('scores/', views.scores_view, name='scores'),

    # 🔵 QUIZ SUBJECT PAGE (DO NOT TOUCH)
    path('subjects/', views.subjects_view, name='subjects'),

    # ================= STUDY MATERIAL (SEPARATE SYSTEM) =================
    path('materials/', views.materials_view, name='materials'),
    path('materials/<str:subject>/', views.material_detail_view, name='material_detail'),

    # ================= PRACTICE =================
    path('practice/', views.practice_options, name='practice_options'),
    path('practice/mix/', views.mix_quiz, name='mix_quiz'),
    path('practice/subject/', views.subject_wise, name='subject_wise'),
    path('practice/subject/<str:subject>/', views.subject_quiz, name='subject_quiz'),

    # ================= RECENT ACTIVITY =================
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('recent-activity/mix/', views.recent_mix_attempts, name='recent_mix_attempts'),
    path('recent-activity/subject/', views.recent_subject_attempts, name='recent_subject_attempts'),
    path('recent-activity/attempt/<int:attempt_id>/', views.attempt_detail, name='attempt_detail'),
]