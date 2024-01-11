from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest
import jwt
from logic.models import UserInfo
from rest_framework import status
from rest_framework.response import Response
from backend.settings import supabase_secret
from authenticate.models import Users
from rest_framework.renderers import JSONRenderer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

class SupabaseAuthBackend(BaseBackend):
    def authenticate(self, request):
        access_token = request.headers.get("Authorization")
        cache_key = f"authenticated_user:{access_token}"

        # Check if user is in cache
        cached_user = cache.get(cache_key)
        if cached_user:
            return cached_user, None

        if not access_token:
            return None  # No access token provided

        try:
            token = access_token.split(' ')[1]
            verified = jwt.decode(token, supabase_secret, audience="authenticated", algorithms=["HS256"], verify=True)

            # Get the sub (subject) claim from the ID token
            sub = verified.get('sub')

            # Find a Django user that corresponds to the user
            user = UserInfo.objects.select_related("org").get(id=sub)
            user.is_authenticated = True

            # Cache the user for future requests
            cache.set(cache_key, user,timeout=3600)

            return user, None

        except jwt.exceptions.InvalidSignatureError as e:
            return None
        except jwt.exceptions.ExpiredSignatureError as e:
            return None

    def authenticate_header(self, request):
        # This method is used to include authentication information in the response.
        # You can return a string that will be included in the "WWW-Authenticate" header.
        return 'Bearer realm="api"'

    
    def get_user(self, user_id):
        try:
            return UserInfo.objects.get(id=user_id)
            # return Users.objects.get(id=user_id)
        except UserInfo.DoesNotExist:
            return None