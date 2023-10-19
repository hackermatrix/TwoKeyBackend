from django.urls import include, path
from .views import DeptView, OrgView, TestView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'org', OrgView, basename='organization')
router.register(r'dept',DeptView,basename="departments")



urlpatterns = [
    path('',include(router.urls)),
]