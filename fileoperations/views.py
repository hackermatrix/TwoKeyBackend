from backend import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from backend.custom_perm_classes import *
from rest_framework.permissions import IsAuthenticated
from supabase import create_client, Client
from decouple import config
from rest_framework.response import Response

class FileViewset(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def upload_file(self,request):
        pass

class TestView(APIView):
    def get(self,request):
        bucket = "TwoKey"
        filename = "my-file.jpg"
        url = config("SUPA_URL")
        key = config('SERVICE_ROLE_KEY')
        supabase = create_client(url,key)
        # signed_url = supabase.storage.from_(bucket).create_signed_url(
        #     filename, expires_in=3600)
        res = supabase.storage.from_(bucket).list()

        print(res)
        return Response(url)
