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
from rest_framework.decorators import action,permission_classes

from authenticate.models import Users
from authenticate.serializers import UsersSerializer
from .custom_perm_classes import *
from backend.supabase_auth import SupabaseAuthBackend
from logic.models import *
from logic.serializers import *
from rest_framework.request import Request



# Organization ViewSet
class OrgView(mixins.ListModelMixin,mixins.CreateModelMixin,GenericViewSet):
    authentication_classes = [SupabaseAuthBackend]
    # permission_classes=[SuperadminRequired]
    serializer_class = OrganizationSerializer
    
    # @action(detail=False, methods=['GET'],permission_classes=[SuperadminRequired])
    def list_orgs(self, request, *args, **kwargs):
        print("perm",self.permission_classes)
        self.queryset = Organizations.objects.all()
        return self.list(request, *args, **kwargs)

    # @action(detail=False, methods=['POST'], permission_classes=SuperadminRequired)
    def create_orgs(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.action == "list_orgs":
            self.permission_classes=[AllowAny]
        elif self.action == "create_orgs":
            self.permission_classes = [SuperadminRequired]
        return super().get_permissions()
    



    
# Department ViewSet
class DeptView(mixins.ListModelMixin,mixins.CreateModelMixin,GenericViewSet):
    queryset = Departments.objects.all()    
    # permission_classes=[OrgadminRequired]
    authentication_classes=[SupabaseAuthBackend]
    serializer_class = DepartmentSerializer


    # @action(detail=True,methods=['GET'],permission_classes=[IsAuthenticated])
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
    
    # @action(detail=True,methods=['POST'],permission_classes=[OrgadminRequired])
    def create_depts(self, request, *args, **kwargs):
        return  self.create(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.action == "list_depts":
            self.permission_classes=[IsAuthenticated]
        elif self.action == "create_depts":
            self.permission_classes = [OrgadminRequired]
        return super().get_permissions()



# User ViewSet
class UserViewSet(mixins.ListModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    # queryset = UserInfo.objects.all() 
    serializer_class = UserInfoSerializer
    queryset = Users.objects.all()
    authentication_classes = [SupabaseAuthBackend]
    # serializer_class = UsersSerializer
    lookup_field = 'id'

    # @action(detail=True, methods=['GET'], permission_classes=[OrgadminRequired])
    def list_users(self, request, *args, **kwargs):
        org_id = request.user.org_id
        self.queryset = UserInfo.objects.filter(org=org_id)
        # self.queryset = Users.objects.filter(org=org_id)
        return self.list(request, *args, **kwargs)
    
    # @action(detail=False,methods=['PUT'],permission_classes=[OrgadminRequired])
    def elevate(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        return self.partial_update(request,*args,**kwargs)
    
    def get_permissions(self):
        if self.action == "list_users":
            self.permission_classes=[OrgadminRequired]
        elif self.action == "elevate":
            self.permission_classes = [OrgadminRequired]
        return super().get_permissions()



    

    
class TestView(APIView):
    authentication_classes=[SupabaseAuthBackend]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response({'msg':"SUccess"})