from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from logic.models import Departments, Organizations


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['name']

class DepartmentSerializer(ModelSerializer):
    # org_id = serializers.SerializerMethodField

    class Meta:
        model =  Departments
        fields = ['name']

    
