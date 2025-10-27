from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
try:
    from rest_framework import routers
    from django.urls import re_path
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )
    from school.api_views import (
        StudentViewSet,
        TeacherViewSet,
        CourseViewSet,
        SubjectViewSet,
        SchoolClassViewSet,
        ExamViewSet,
        MarkViewSet,
        AttendanceViewSet,
        FeeViewSet,
        BookViewSet,
        RouteViewSet,
        NotificationViewSet,
    )
    from users.api_views import UserViewSet

    router = routers.DefaultRouter()
    router.register(r'students', StudentViewSet)
    router.register(r'teachers', TeacherViewSet)
    router.register(r'courses', CourseViewSet)
    router.register(r'subjects', SubjectViewSet)
    router.register(r'classes', SchoolClassViewSet)
    router.register(r'exams', ExamViewSet)
    router.register(r'marks', MarkViewSet)
    router.register(r'attendance', AttendanceViewSet)
    router.register(r'fees', FeeViewSet)
    router.register(r'books', BookViewSet)
    router.register(r'routes', RouteViewSet)
    router.register(r'notifications', NotificationViewSet)
    router.register(r'users', UserViewSet)
    has_api = True
except Exception:
    # DRF or SimpleJWT not installed in this environment. API routes disabled until packages are available.
    router = None
    has_api = False

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(('school.urls', 'school'), namespace='school')),
    path('dashboard/', include(('school.urls', 'school'), namespace='school_dashboard')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('students/', include(('students.urls', 'students'), namespace='students')),
    path('teachers/', include(('teachers.urls', 'teachers'), namespace='teachers')),
    path('classes/', include(('classes.urls', 'classes'), namespace='classes')),
    path('exams/', include(('exams.urls', 'exams'), namespace='exams')),
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    path('library/', include(('library.urls', 'library'), namespace='library')),
    path('transport/', include(('transport.urls', 'transport'), namespace='transport')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    # Authentication views: add direct login/logout routes and keep accounts/ for full auth flow
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if has_api and router is not None:
    urlpatterns += [
        path('api/', include(router.urls)),
        # JWT token endpoints
        path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
