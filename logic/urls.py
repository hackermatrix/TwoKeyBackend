from django.urls import include, path
from .views import DeptView, OrgView, TestView ,UserViewSet
from rest_framework.routers import DefaultRouter

router =DefaultRouter()
router.register('org',OrgView,basename='orgs')
urlpatterns = [
    #Org Paths`
    # path('',include(router.urls)),
    path('org/list_orgs/',OrgView.as_view({'get':'list_orgs'}),name="list-orgs"),
    path('org/create_orgs/',OrgView.as_view({'post':'create_orgs'}),name="create-orgs"),

    #Dept Paths
    path('dept/list_depts/',DeptView.as_view({'get':'list_depts'}),name="list-depts"),
    path('dept/create_depts/',DeptView.as_view({'post':'create_depts'}),name="create-depts"),

    # User Paths
    path('users/list_users/',UserViewSet.as_view({'get':'list_users'}),name="list-users"),
    path('users/elevate/<str:id>', UserViewSet.as_view({'put': 'elevate'}), name='user-elevate')
]