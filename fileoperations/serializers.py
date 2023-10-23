from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Objects




class FileSerializer(ModelSerializer):
    org_name = serializers.SerializerMethodField()
    dept_name = serializers.SerializerMethodField()


    def get_org_name(self,obj):
        owner = getattr(obj, 'owner', None)
        if(owner):
            return owner.org.name
    def get_dept_name(self,obj):
        owner = getattr(obj, 'owner', None)
        if(owner):
            return owner.dept.name
        
    class Meta:
        model = Objects
        fields = ['name','org_name','dept_name']

