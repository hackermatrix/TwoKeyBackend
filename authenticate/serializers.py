from rest_framework.serializers import ModelSerializer

from authenticate.models import Users




class UsersSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','email','role','dept','org']