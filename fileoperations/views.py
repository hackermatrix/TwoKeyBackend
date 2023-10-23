from backend import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from backend.custom_perm_classes import *
from rest_framework.permissions import IsAuthenticated
from fileoperations.serializers import FileSerializer
from supabase import create_client, Client
from decouple import config
from rest_framework.response import Response
from rest_framework import mixins
from backend.supabase_auth import SupabaseAuthBackend
from rest_framework import generics
from .models import *


class FileListing(mixins.ListModelMixin
               ,generics.GenericAPIView):
    
    serializer_class= FileSerializer
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]
    queryset = Objects.objects.all()

    def get(self,request,*args,**kwargs):
        queryset = Objects.objects.prefetch_related('owner').filter(owner__org=request.user.org)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
