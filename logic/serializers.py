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



class AUserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['id','dept','manager','role_priv','is_approved']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('dept')
        data['username'] = instance.username
        data['email'] = instance.email
        data['name'] = instance.name
        data['last_name'] = instance.last_name
        data ['dept'] = instance.dept.name

        return data

class NUserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ['is_approved','is_authenticated','org','role_priv']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['org'] = instance.org.name
        data['dept'] = instance.dept.name
        data['role_priv'] = instance.role_priv
        if(instance.manager is not None):
            data['manager'] = instance.manager.name
        return data
    
