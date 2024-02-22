from django.urls import include, path,re_path
from .views import DeptView, NUserViewSet, OrgView, RolesViewset ,AUserViewSet,InviteUserView
from rest_framework.routers import DefaultRouter

router =DefaultRouter()
router.register('org',OrgView,basename='orgs')
urlpatterns = [
    #Org Paths`
    # path('',include(router.urls)),
    re_path('org/list_orgs/?',OrgView.as_view({'get':'list_orgs'}),name="list-orgs"),
    path('org/createOrgs/',OrgView.as_view({'post':'create_orgs'}),name="create-orgs"),

    #Dept Paths
    path('dept/listDepts/',DeptView.as_view({'get':'list_depts'}),name="list-depts"),
    path('dept/createDepts/',DeptView.as_view({'post':'create_depts'}),name="create-depts"),
    re_path(r'^dept/deleteDept/?(?P<id>[\w-]*)/?',DeptView.as_view({'delete':'delete_depts'}),name="delete-depts"),
    re_path(r'^dept/updateDept/?(?P<id>[\w-]*)/?',DeptView.as_view({'put':'update_depts'}),name="update-depts"),

    # User Paths For Admins
    re_path(r'^users/list_users/(?P<dept>[\w-]*)/?',AUserViewSet.as_view({'get':'list_users'}),name="list-users"),
    re_path(r'users/getUserInfo/(?P<id>[\w-]*)/?',AUserViewSet.as_view({'get':"get_user_info"}),name="Getuser Info"),
    path('users/elevate/<str:id>', AUserViewSet.as_view({'put': 'elevate'}), name='user-elevate'),
    re_path(r'^users/deleteUser/?(?P<id>[\w-]*)/?',AUserViewSet.as_view({'delete':'delete_user'}),name="delete user"),
    re_path(r'users/invite/?',InviteUserView.as_view(),name='InviteUsers'),
    # For Normal Users
    path('users/getProfileInfo/',NUserViewSet.as_view({'get':'get_current_user_info'}),name="get current user info"),
    path('users/updateProfile/',NUserViewSet.as_view({'put':'update_profile_data'}),name="Update user Profile data"),
    # Roles Paths
    path('role/listRoles/',RolesViewset.as_view({'get':'list_roles'}),name="list-roles"),
    path('role/updateRoles/<str:id>', RolesViewset.as_view({'put': 'update_roles'}), name='update_roles'),
    path('role/deleteRoles/<str:id>',RolesViewset.as_view({'delete': 'delete_roles'}),name='delete-roles'),
    path('role/createRoles/',RolesViewset.as_view({'post':'create_roles'}),name="create-roles"),

    
]