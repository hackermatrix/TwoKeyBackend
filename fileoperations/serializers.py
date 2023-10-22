from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from fileoperations.models import UserFiles




class FileSerializer(ModelSerializer):
    org = serializers.SerializerMethodField
    dept = serializers.SerializerMethodField

    class Meta:
        model = UserFiles
        fields = ['file_name']