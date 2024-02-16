from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from logic.models import Departments, Organizations, Role, UserInfo
from authenticate.models import Users 

class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['id','name']

class DepartmentSerializer(ModelSerializer):
    # org_id = serializers.SerializerMethodField

    class Meta:
        model =  Departments
        fields = ['id','name','metadata']

class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"



class AUserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['id','dept','manager','role_priv','is_approved','is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('dept')
        data['username'] = instance.username
        data['email'] = instance.email
        data['name'] = instance.name
        data['last_name'] = instance.last_name
        data ['dept'] = instance.dept.name
        data['profile_pic'] = instance.profile_pic



        # Adding additional data when requesting user is org_admin 
        request = self.context.get("request")
    
        if request and request.user.role_priv == "org_admin":
            current_user = Users.objects.get(id=instance.id)
            data["created_at"] = current_user.created_at
            data["last_sign_in_at"]=current_user.last_sign_in_at
            data['country'] = instance.country
            data['state'] = instance.state
            data['city'] = instance.city
            data['postalcode'] = instance.postal_code
            data['phone'] = instance.phone
            
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
    
