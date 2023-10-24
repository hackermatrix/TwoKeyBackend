from django.shortcuts import get_object_or_404
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist,ValidationError


from logic.models import UserInfo

from .models import Objects, SharedFiles




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


class SharedFileSerializer(serializers.ModelSerializer):
    shared_with = serializers.ListField(child=serializers.EmailField(), write_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = SharedFiles
        fields = ["file", "file_name", 'shared_with']

    def create(self, validated_data):
        shared_with_emails = validated_data.pop('shared_with', [])
        shared_with_ids = self.get_user_ids(shared_with_emails)
        instance = super(SharedFileSerializer, self).create(validated_data)

        for user_id in shared_with_ids:
            instance.shared_with.add(user_id)

        return instance

    def get_user_ids(self, emails):
        user_ids = []
        for email in emails:
            try:
                user = UserInfo.objects.get(email=email.lower())
                user_ids.append(user.id)
            except UserInfo.DoesNotExist:
                # Handle or log the exception as needed
                pass
        return user_ids
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['shared_with'] = [user.email for user in instance.shared_with.all()]
        return data