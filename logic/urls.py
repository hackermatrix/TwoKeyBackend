from django.urls import include, path
from .views import DeptView, NUserViewSet, OrgView, RolesViewset ,AUserViewSet
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

    # User Paths For Admins
    path('users/list_users/',AUserViewSet.as_view({'get':'list_users'}),name="list-users"),
    path('users/elevate/<str:id>', AUserViewSet.as_view({'put': 'elevate'}), name='user-elevate'),
    # For Normal Users
    path('users/getProfileInfo/',NUserViewSet.as_view({'get':'get_current_user_info'}),name="get current user info"),
    path('users/updateProfile/',NUserViewSet.as_view({'put':'update_profile_data'}),name="Update user Profile data"),
    # Roles Paths
    path('role/list_roles/',RolesViewset.as_view({'get':'list_roles'}),name="list-roles"),
    path('role/update_roles/<str:id>', RolesViewset.as_view({'put': 'update_roles'}), name='update_roles'),
    path('role/delete_roles/<str:id>',RolesViewset.as_view({'delete': 'delete_roles'}),name='delete-roles'),
    path('role/create_roles/',RolesViewset.as_view({'post':'create_roles'}),name="create-roles"),
]