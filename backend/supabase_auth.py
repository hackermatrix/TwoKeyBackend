from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest
import jwt
from logic.models import UserInfo
from backend.settings import supabase_secret

class SupabaseAuthBackend(BaseBackend):
    def authenticate(self, request):
        access_token = request.headers.get("Authorization")
        print("RUNNING>>>>>....")

        if not access_token:
            return None  # No access token provided

        try:
            token = access_token.split(' ')[1]
            verified = jwt.decode(token, supabase_secret, audience="authenticated", algorithms=["HS256"], verify=True)

            # Get the sub (subject) claim from the ID token
            sub = verified.get('sub')

            # Find a Django user that corresponds to the user
            user = UserInfo.objects.get_by_pk(sub)
            user.is_authenticated = True
            return (user, None)

        except jwt.exceptions.InvalidSignatureError:
            return None

    def authenticate_header(self, request):
        # This method is used to include authentication information in the response.
        # You can return a string that will be included in the "WWW-Authenticate" header.
        return 'Bearer realm="api"'

    def get_user(self, user_id):
        try:
            return UserInfo.objects.get_by_pk(user_id)
        except UserInfo.DoesNotExist:
            return None