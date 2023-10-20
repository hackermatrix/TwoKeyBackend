from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from logic.models import Departments, Organizations, Role, UserInfo


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['id','name']

class DepartmentSerializer(ModelSerializer):
    # org_id = serializers.SerializerMethodField

    class Meta:
        model =  Departments
        fields = ['id','name']

class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
class UserInfoSerializer(ModelSerializer):
    # role = RoleSerializer
    class Meta:
        model = UserInfo
        fields = ['id','email','dept','role_priv','is_approved']


    
