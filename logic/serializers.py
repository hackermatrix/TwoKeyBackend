from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from logic.models import Departments, Organizations, UserInfo


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['id','name']

class DepartmentSerializer(ModelSerializer):
    # org_id = serializers.SerializerMethodField

    class Meta:
        model =  Departments
        fields = ['name']

class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['id','email','dept','role_priv']

    
