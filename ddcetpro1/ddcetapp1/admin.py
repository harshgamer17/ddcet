from django.contrib import admin
from django.contrib.auth.models import User
from .models import Quiz, Question, Student, QuizAttempt, AttemptAnswer


# ================= QUIZ ADMIN =================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'total_questions', 'status')
    list_filter = ('subject', 'status')
    search_fields = ('title', 'subject')
    ordering = ('subject', 'title')   # ✅ SUBJECT WISE ORDER


# ================= QUESTION ADMIN =================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'get_subject')
    list_filter = ('quiz', 'quiz__subject')
    search_fields = ('question_text',)

    # ✅ IMPORTANT PART (SEQUENCE FIX)
    ordering = ('quiz__subject', 'quiz', 'id')

    def get_subject(self, obj):
        return obj.quiz.subject

    get_subject.short_description = "Subject"


# ================= STUDENT ADMIN =================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    # ✅ Same table style like Django Users
    list_display = (
        'get_username',
        'get_email',
        'get_first_name',
        'get_last_name',
        'get_staff_status',
        'get_active_status',
    )

    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    )

    list_filter = (
        'user__is_staff',
        'user__is_active',
    )

    ordering = ('user__username',)

    # ================= CUSTOM COLUMN METHODS =================

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
    get_username.admin_order_field = 'user__username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email Address"
    get_email.admin_order_field = 'user__email'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = "First Name"
    get_first_name.admin_order_field = 'user__first_name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = "Last Name"
    get_last_name.admin_order_field = 'user__last_name'

    def get_staff_status(self, obj):
        return obj.user.is_staff
    get_staff_status.boolean = True
    get_staff_status.short_description = "Staff Status"
    get_staff_status.admin_order_field = 'user__is_staff'

    def get_active_status(self, obj):
        return obj.user.is_active
    get_active_status.boolean = True
    get_active_status.short_description = "Active"
    get_active_status.admin_order_field = 'user__is_active'


# ================= QUIZ ATTEMPT ADMIN =================
@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'subject',
        'is_mix',
        'score',
        'current_index',
        'created_at',
    )

    list_filter = (
        'is_mix',
        'subject',
        'created_at',
    )

    search_fields = (
        'student__user__username',
        'subject',
    )

    ordering = ('-created_at',)


# ================= ATTEMPT ANSWER ADMIN =================
@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):

    list_display = (
        'attempt',
        'question',
        'selected_option',
        'is_correct',
    )

    list_filter = (
        'is_correct',
    )

    search_fields = (
        'attempt__student__user__username',
        'question__question_text',
    )
