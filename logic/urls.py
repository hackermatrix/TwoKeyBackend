from django.urls import include, path
from .views import DeptView, OrgView, RolesViewset ,UserViewSet
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
    path('users/elevate/<str:id>', UserViewSet.as_view({'put': 'elevate'}), name='user-elevate'),

    # Roles Paths
    path('role/list_roles/',RolesViewset.as_view({'get':'list_roles'}),name="list-roles"),
    path('role/update_roles/<str:id>', RolesViewset.as_view({'put': 'update_roles'}), name='update_roles'),
    path('role/delete_roles/<str:id>',RolesViewset.as_view({'delete': 'delete_roles'}),name='delete-roles'),
    path('role/create_roles/',RolesViewset.as_view({'post':'create_roles'}),name="create-roles"),
]