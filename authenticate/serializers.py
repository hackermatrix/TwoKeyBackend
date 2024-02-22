from rest_framework.serializers import ModelSerializer

from authenticate.models import Users
import bcrypt



class UsersSerializer(ModelSerializer):
    def create(self,validated_data):
        password_in_plain = validated_data['encrypted_password']

        bytes = password_in_plain.encode('utf-8') 
        # generating the salt 
        salt = bcrypt.gensalt() 
        # Hashing the password 
        hash = bcrypt.hashpw(bytes, salt) 
        validated_data['encrypted_password'] = hash.decode('utf-8')
        created = super().create(validated_data)
        return created
    class Meta:
        model = Users
        fields = ['id','email',"encrypted_password","confirmation_token","raw_app_meta_data"]