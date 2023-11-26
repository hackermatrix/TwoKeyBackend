from django.shortcuts import get_object_or_404
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from .utils.supa import supabase
from logic.models import UserInfo
from decouple import config
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import AccessLog, AllowedLocations, Objects, SecCheck, SharedFiles




class FileSerializer(ModelSerializer):
    org_name = serializers.SerializerMethodField()
    dept_name = serializers.SerializerMethodField()
    metadata =serializers.JSONField


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
        fields = ['id','name','org_name','dept_name','metadata']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # print(instance.owner.email)
        data['owner_email'] = instance.owner.email
        data['metadata'].pop('eTag')
        data['metadata'].pop('cacheControl')
        data['metadata'].pop('contentLength')
        data['metadata'].pop('httpStatusCode')
        
        return data


class SecCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecCheck
        fields = ['download_enabled','geo_enabled','unique_identifiers']




class SharedFileSerializer(serializers.ModelSerializer):
    shared_with = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)
    owner = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    security_check = SecCheckSerializer()

    class Meta:
        model = SharedFiles
        fields = ["file","owner", "file_name",'last_updated', 'shared_with','expiration_time',"security_check"]

    def create(self, validated_data):
        # Adding the signed_url to the share:
        security_check = validated_data.pop('security_check')
        file_name = validated_data['file'].name
        expiration_time = validated_data['expiration_time']
        res = supabase.storage.from_(config('BUCKET_NAME')).create_signed_url(file_name,expiration_time*60)
        signed_url = res['signedURL']
        validated_data.update({'signed_url':signed_url})


        # Creating SecCheck Object.
        created = super().create(validated_data)
        SecCheck(shared=created,**security_check).save()
        # print(temp)
        return created
    
    def get_last_updated(self,obj):
        return obj.file.updated_at
    
    def get_owner(self,obj):
        return obj.file.owner.email
    
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
        # print(dir(instance))
        # print(instance.security_check)
        data = super().to_representation(instance)
        data.pop("security_check")
        
        serializer = SecCheckSerializer(SecCheck.objects.get(shared=SharedFiles.objects.get(file=data['file'])))
        data["security_check"] = serializer.data

        data['shared_with'] = [{"user_id":str(user.id),"user_email":user.email,"profile_pic":user.profile_pic} for user in instance.shared_with.all()]
        

        fields_to_include = self.context.get('fields')

        if fields_to_include:
            data = {key: value for key, value in data.items() if key in fields_to_include}
        


        return data
    
class SharedFilesRecepient(ModelSerializer):
    class Meta:
        model = SharedFiles
        fields = ['id','signed_url']




class AccessLogSerializer(ModelSerializer):
    class Meta:
        model = AccessLog
        exclude = ["timestamp","id"]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = instance.user_email
        data['username'] = instance.username
        # data['file'] = Objects.objects.get(id=data['file']).name
        data['file'] = instance.file_name
        try:
            userobj = UserInfo.objects.get(id=instance.user)
            data['profile_pic'] = userobj.profile_pic
        except:
            data['profile_pic'] ="placeholder"
        data['timestamp'] = instance.timestamp
        return data
    

class AllowedLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AllowedLocations
        geo_field = 'location_point' 
        fields =['name','location_point']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        return data