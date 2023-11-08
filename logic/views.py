import json
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import render
from django.core import exceptions
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.decorators import action, permission_classes

from authenticate.models import Users
from authenticate.serializers import UsersSerializer
from backend.custom_perm_classes import *
from backend.supabase_auth import SupabaseAuthBackend
from logic.models import *
from logic.serializers import *
from rest_framework.request import Request


# Organization ViewSet
class OrgView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [SuperadminRequired]
    serializer_class = OrganizationSerializer

    def list_orgs(self, request, *args, **kwargs):
        print("perm", self.permission_classes)
        self.queryset = Organizations.objects.all()
        return self.list(request, *args, **kwargs)

    def create_orgs(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "list_orgs":
            self.permission_classes = [AllowAny]
        return super().get_permissions()


# Department ViewSet
class DeptView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Departments.objects.all()
    # permission_classes=[OrgadminRequired]
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = DepartmentSerializer

    def list_depts(self, request, *args, **kwargs):
        org_id = request.user.org_id
        self.queryset = Departments.objects.filter(org=org_id)
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org_id = request.user.org
        serializer.save(org=org_id)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_depts(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "list_depts":
            self.permission_classes = [OthersPerm]
        elif self.action == "create_depts":
            self.permission_classes = [OrgadminRequired]
        return super().get_permissions()


# User ViewSet for Org Admin
class AUserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    # serializer_class = UsersSerializer
    # queryset = Users.objects.all()
    permission_classes = [OrgadminRequired]
    queryset = UserInfo.objects.all()
    serializer_class = AUserInfoSerializer
    authentication_classes = [SupabaseAuthBackend]
    lookup_field = "id"

    def list_users(self, request, *args, **kwargs):
        org_id = request.user.org_id
        dept = kwargs.get("dept")
        if(dept):
            try:
                dept_id = Departments.objects.get(name=dept)
                self.queryset = UserInfo.objects.filter(dept=dept_id)
            except Departments.DoesNotExist:
                return Response({"error":"department not found"},status=status.HTTP_404_NOT_FOUND)
        else:
            self.queryset = (
                UserInfo.objects.filter(org=org_id)
                .exclude(role_priv="org_admin")
                .exclude(role_priv="super_admin")
                .exclude(id=request.user.id)
            )
            # self.queryset = Users.objects.filter(org=org_id)
        return self.list(request, *args, **kwargs)

    # Checking the Role's Existance
    def partial_update(self, request, *args, **kwargs):
        if("role_priv" in request.data):
            serializer = RoleSerializer(data=request.data["role_priv"], partial=True)
            kk = serializer.is_valid()

            role = request.data["role_priv"]
            try:
                Role.objects.get(role=role)
            except Role.DoesNotExist:
                return Response(
                    {"error": "this role does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except exceptions.ValidationError:
                return Response(
                    {"error": "invalid value"}, status=status.HTTP_400_BAD_REQUEST
                )
            return super().partial_update(request, *args, **kwargs)
        else:
            return super().partial_update(request, *args, **kwargs)
        

    def elevate(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        resp = self.partial_update(request, *args, **kwargs)
        return resp

    def get_permissions(self):
        if self.action == "list_users":
            self.permission_classes = [OthersPerm]
        return super().get_permissions()


# User Viewset for  Normal users
class NUserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin,GenericViewSet):
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]
    serializer_class = NUserInfoSerializer
    lookup_field = "id"
    

    def get_current_user_info(self,request):
        current_user = request.user
        serializer = self.get_serializer(current_user)
        print(serializer.data)
        return Response(serializer.data)
    
    def update_profile_data(self, request, **kwargs):
        # Retrieve the object based on the request user's ID
        user_id = request.user.id
        try:
            user_info = UserInfo.objects.get(id=user_id)
        except UserInfo.DoesNotExist:
            return Response({"error": "Profile not found for this user"}, status=404)

        # Check permissions if needed
        self.check_object_permissions(request, user_info)

        # Update the user_info object with the request data
        serializer = self.get_serializer(user_info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

# Roles Viewset
class RolesViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    authentication_classes = [SupabaseAuthBackend]
    queryset = Role.objects.all()
    permission_classes = [SuperadminRequired]
    serializer_class = RoleSerializer
    lookup_field = "id"

    def list_roles(self, request):
        return self.list(request)

    def create_roles(self, request):
        return self.create(request)

    def update_roles(self, request):
        return self.update(request)

    def delete_roles(self, request, *args, **kwargs):
        kwargs.get("pk")
        return self.destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "list_roles":
            self.permission_classes = [OrgadminRequired]
        return super().get_permissions()
