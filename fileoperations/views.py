import uuid
from django.core import exceptions
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from decouple import config
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from backend import settings
from backend.custom_perm_classes import SuperadminRequired, OrgadminRequired, OthersPerm
from backend.supabase_auth import SupabaseAuthBackend

from .models import *
from fileoperations.serializers import (
    AccessLogSerializer,
    AllowedLocationSerializer,
    FileSerializer,
    SharedFileSerializer,
    SharedFilesRecepient,
)

from .utils.supa import create_signed





class FileListing(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FileSerializer
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]
    queryset = Objects.objects.all()

    # List all files uploaded by all users from all departments.
    def get(self, request, *args, **kwargs):
        dept_choice = kwargs.get("dept")
        if(dept_choice):
            try:
                res = Departments.objects.get(name=dept_choice)

            except (Departments.DoesNotExist,ValueError,exceptions.ValidationError):
                return Response({"error":"invalid request"},status=status.HTTP_400_BAD_REQUEST)

            self.queryset = (
                Objects.objects.prefetch_related("owner")
                .filter(owner__org=request.user.org,owner__dept=res.id,bucket_id="TwoKey")
                .exclude(name=".emptyFolderPlaceholder")
                .order_by("-created_at")
            )
        else:
            self.queryset = (
                Objects.objects.prefetch_related("owner")
                .filter(owner__org=request.user.org,bucket_id="TwoKey")
                .exclude(name=".emptyFolderPlaceholder")
                .order_by("-created_at")
            )
        return self.list(request, *args, **kwargs)


class ExtraChecksMixin:
    # Check if the user creating or deleting a share is the owner of the file
    def check_file_ownership(self, request, file_id):
        try:
            file_object = Objects.objects.get(id=file_id)
            file_owner = file_object.owner
        except Exception:
            return False
        current_user = request.user
        if current_user == file_owner:
            return True
        return False



#  Below are the endpoints used at the Sender's side.
class ShareViewSetSender(
    ExtraChecksMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = SharedFileSerializer
    permission_classes = [OthersPerm]
    queryset = SharedFiles.objects.all()

    # Delete a file share if the user is the owner of the file
    def destroy(self, request, *args, **kwargs):
        file_id = kwargs.get("file")
        if self.check_file_ownership(request, file_id):
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(
                {"error": "You cannot delete this share"},
                status=status.HTTP_403_FORBIDDEN,
            )

    # Share a file (alias for create)
    # Create a file share for list of UUIDs.
    # - Share a list of files
    # - Assigns a presigned url to the share as in the expiration_time parameter.
    # - Security Features not yet added.
    def share_file(self, request):
        file_ids = request.data.get("file", [])
        shared_files = []
        if type(file_ids) != list:
            return Response(
                {"error": "file should be a list"}, status=status.HTTP_400_BAD_REQUEST
            )
        for file_id in file_ids:
            if self.check_file_ownership(request, file_id):
                request.data.pop("file")
                request.data["file"] = file_id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                shared_files.append(file_id)
            else:
                return Response(
                    {"error": "You cannot share this file"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        headers = self.get_success_headers(serializer.data)
        response_data = {
            "message": "Shares created SuccessFully!",
            "shared_files": shared_files,
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    # Get information about the shared file, including its name, id, and the list of users it's shared with
    # Returns Information about the Shared file given
    #  - file_name
    #  - file_id
    #  - Shared_with list
    def get_file_info(self, request, *args, **kwargs):
        self.lookup_field = "file"
        pk = kwargs.get("file")
        res = self.retrieve(request)
        return res

    # Delete All share of a file
    # User file ownership check added already
    def delete_share(self, request, *args, **kwargs):
        self.lookup_field = "file"
        pk = kwargs.get("file")
        return self.destroy(request)

    # Edit file access
    # - The Access log entry is not implemented
    def edit_access(self, request, **kwargs):
        file_id = kwargs.get("file")
        self.lookup_field = "file"
        if self.check_file_ownership(request, file_id):
            return self.partial_update(request, **kwargs)
        else:
            return Response(
                {"error": "You cannot modify this share"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# Below will be used at recepient's end


class ShareViewSetReceiver(
    ExtraChecksMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = SharedFilesRecepient
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        sec_obj = SecCheck.objects.get(shared=instance)
        if sec_obj.geo_enabled == None:
            return super().retrieve(request, *args, **kwargs)
        else:
            try:
                latitude = float(self.request.data.get("latitude", 0))
                longitude = float(self.request.data.get("longitude", 0))
                user_location = Point(latitude, longitude, srid=4326)
                required_location = sec_obj.geo_enabled.location_point
                distance_in_kms = user_location.distance(required_location) * 100

                if distance_in_kms <= 1:
                    return super().retrieve(request, *args, **kwargs)
                else:
                    return Response(
                        {"error": "Location Not Allowed!"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            except ValueError:
                return Response({"error": "wrong parameter value"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                return Response({"error":str(error)},status=status.HTTP_400_BAD_REQUEST)

    # Endpoint Serves recepient with the presigned url
    # - Adds an access log entry.
    def get_shared_file_url(self, request, *args, **kwargs):
        # Only files shared with the current user
        user = request.user
        self.lookup_field = "file"
        if(not self.check_file_ownership(request,kwargs.get("file"))):
            self.queryset = SharedFiles.objects.filter(shared_with__id=request.user.id)
            response = self.retrieve(request, *args, **kwargs)
            print(response.status_code)
            if response.status_code == 200:

                file_id = kwargs.get("file")
                access_log_data = {
                    'user': user.id,
                    'username': user.username,
                    'user_email':user.email,
                    'file': uuid.UUID(file_id),
                    'file_name' : Objects.objects.get(id=file_id).name,
                    'event': 'file_access',
                    'org': user.org.id
                }

                access_log_serializer = AccessLogSerializer(data=access_log_data)

                if access_log_serializer.is_valid():
                    access_log_serializer.save()

            return response
        else:
            self.queryset = Objects.objects.filter(owner=user)
            objs = get_object_or_404(self.queryset,id=kwargs.get('file'))
            signed_url = create_signed(objs.name,60)
            return Response({"id":objs.id,"signed_url":signed_url['signedURL']})

    def screen_shot_alert(self, request, *args, **kwargs):
        # Only files shared with the current user
        user = request.user
        file_id = kwargs.get("file")
        try:
            shared = SharedFiles.objects.get(shared_with__id=request.user.id,file=file_id)
            print(shared)

            file_id = kwargs.get("file")
            access_log_data = {
                'user': user.id,
                'username': user.username,
                'user_email':user.email,
                'file': uuid.UUID(file_id),
                'file_name' : Objects.objects.get(id=file_id).name,
                'event': 'screenshot',
                'org': user.org.id
            }
            access_log_serializer = AccessLogSerializer(data=access_log_data)
            if access_log_serializer.is_valid():
                access_log_serializer.save()
            return Response(
                {"message": "Screenshot event logged successfully"},
                status=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationError:
            return Response({"error":"wrong parameter value"},status=status.HTTP_400_BAD_REQUEST)
        except SharedFiles.DoesNotExist:
            return Response({"error": "invalid share"},status=status.HTTP_400_BAD_REQUEST)
        except Objects.DoesNotExist:
            return Response({"error": "file does not exist"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)},status=status.HTTP_400_BAD_REQUEST)


    # Fetch the screen shot attempts for Current user's files
    def get_logs(self, request, *args, **kwargs):
        self.serializer_class = AccessLogSerializer
        user = request.user
        event = kwargs.get("event")
        file = kwargs.get("file")
        try:
            n = int(request.GET.get("recs","0"))
        except ValueError:
            return Response({"error":"invalid parameter"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error":str(error)})


 # Selecting the type of event
        if event == "screen":
            return self.handle_screen_event(request, user, n)

        elif event == "access":
            if file:
                return self.handle_access_event_by_file(request, user, file, n)
            else:
                return self.handle_access_event_all(request, user, n)
            
        else:
            return Response({"error":"specify event type"},status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
# Functions handling events
    def handle_screen_event(self, request, user, n):
        file_ids_owned_by_user = Objects.objects.filter(owner=user).values("id")
        self.queryset = AccessLog.objects.filter(
            event="screenshot",
            file__in=file_ids_owned_by_user,
            org=user.org
        )
        self.queryset = self.queryset[:n] if n >= 1 else self.queryset

        return self.list(request)

    def handle_access_event_by_file(self, request, user, file, n):
        try:
            self.queryset = AccessLog.objects.filter(file=file, org=user.org).exclude(event='screenshot')
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            return self.list(request) 
        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
    def handle_access_event_all(self, request, user, n):
        try:
            self.queryset = AccessLog.objects.filter(org=user.org).exclude(event='screenshot')
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            return self.list(request) 
        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)



class GeoLocationView(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [OrgadminRequired]
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = AllowedLocationSerializer
    queryset = AllowedLocations.objects.all()

    def perform_create(self, serializer):
        try:
            current_user = self.request.user
            organization = current_user.org
            # Set the organization ID in the serializer before creating the entry.
            serializer.save(org=organization)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return super().perform_create(serializer)

    def create_location(self, request):
        print(request.data)
        return self.create(request)

    def get_locations(self, request):
        user_org = request.user.org
        self.queryset = AllowedLocations.objects.filter(org=user_org)
        return self.list(request)

    def get_permissions(self):
        if self.action == "get_locations":
            self.permission_classes = [OthersPerm]
        return super().get_permissions()
