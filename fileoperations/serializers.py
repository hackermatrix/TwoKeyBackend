from django.shortcuts import get_object_or_404
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from .utils.supa import supabase
from logic.models import UserInfo
from decouple import config

from .models import AccessLog, Objects, SharedFiles




class FileSerializer(ModelSerializer):
    org_name = serializers.SerializerMethodField()
    dept_name = serializers.SerializerMethodField()
    metadata =serializers.JSONField


    def get_org_name(self,obj):
        owner = getattr(obj, 'owner', None)
        print(owner.org_id)
        if(owner):
            return owner.org.name
    def get_dept_name(self,obj):
        owner = getattr(obj, 'owner', None)
        if(owner):
            return owner.dept.name
        
    class Meta:
        model = Objects
        fields = ['id','name','org_name','dept_name','metadata']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['metadata'].pop('eTag')
        data['metadata'].pop('cacheControl')
        data['metadata'].pop('contentLength')
        data['metadata'].pop('lastModified')
        data['metadata'].pop('httpStatusCode')
        return super().to_representation(instance)




class SharedFileSerializer(serializers.ModelSerializer):
    shared_with = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = SharedFiles
        fields = ["file", "file_name", 'shared_with','expiration_time','download_allowed']

    def create(self, validated_data):
        # Adding the signed_url to the share:
        file_name = validated_data['file'].name
        expiration_time = validated_data['expiration_time']
        res = supabase.storage.from_(config('BUCKET_NAME')).create_signed_url(file_name,expiration_time*60)
        signed_url = res['signedURL']
        validated_data.update({'signed_url':signed_url})


        # shared_with_emails = validated_data.pop('shared_with', [])
        # shared_with_ids = self.get_user_ids(shared_with_emails)
        # instance = super(SharedFileSerializer, self).create(validated_data)

        # for user_id in shared_with_ids:
        #     instance.shared_with.add(user_id)

        return super().create(validated_data)

        

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
        data['shared_with'] = [{str(user.id):user.email} for user in instance.shared_with.all()]
        return data
    
class SharedFilesRecepient(ModelSerializer):
    class Meta:
        model = SharedFiles
        fields = ['id','signed_url']

class AccessLogSerializer(ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['user','file','event']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserInfo.objects.get(id=data['user']).email
        data['file'] = Objects.objects.get(id=data['file']).name
        print(data['user'])
        print(data['file'])
        return data
    
