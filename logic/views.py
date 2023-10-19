import json
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.decorators import action
from .custom_perm_classes import *
from backend.supabase_auth import SupabaseAuthBackend
from logic.models import *
from logic.serializers import *
from rest_framework.request import Request


class OrgView(generics.ListCreateAPIView,ViewSet):
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = OrganizationSerializer

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def list_orgs(self, request, *args, **kwargs):
        self.queryset = Organizations.objects.all()
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['POST'], permission_classes=[SuperadminRequired])
    def create_orgs(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# class OrgAdminView(mixins.ListModelMixin,GenericViewSet):
#     # THis view will be used to create Org Admin accounts
#     permission_classes=[SuperadminRequired]
#     authentication_classes=[SupabaseAuthBackend]


    
class DeptView(generics.ListCreateAPIView,ViewSet):
    queryset = Departments.objects.all()    
    # permission_classes=[OrgadminRequired]
    authentication_classes=[SupabaseAuthBackend]
    serializer_class = DepartmentSerializer


    @action(detail=True,methods=['GET'])
    def list_depts(self,request,*args,**kwargs):
        org_id = request.user.org_id
        self.queryset = Departments.objects.filter(org=org_id)
        return self.list(request,*args,**kwargs)
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org_id = request.user.org
        serializer.save(org=org_id)  
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True,methods=['POST'])
    def create_depts(self, request, *args, **kwargs):
        return  self.create(request, *args, **kwargs)


# class UserViewSet(generics.GenericAPIView,ViewSet):


    
class TestView(APIView):
    authentication_classes=[SupabaseAuthBackend]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response({'msg':"SUccess"})