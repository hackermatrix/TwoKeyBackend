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


# User ViewSet
class UserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    # serializer_class = UsersSerializer
    # queryset = Users.objects.all()
    permission_classes = [OrgadminRequired]
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    authentication_classes = [SupabaseAuthBackend]
    lookup_field = "id"

    def list_users(self, request, *args, **kwargs):
        org_id = request.user.org_id
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

    def elevate(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        resp = self.partial_update(request, *args, **kwargs)
        return resp

    def get_permissions(self):
        if self.action == "list_users":
            self.permission_classes = [OthersPerm]
        return super().get_permissions()


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
