import uuid
from django.core.cache import cache
from django.core import exceptions
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from decouple import config
from django.db import connection, reset_queries
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

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
    FileMetaSerializer,
    SharedFileSerializer,
    SharedFilesRecepient,
    AddDepartmentsSerializer,
)

from .utils.supa import create_signed
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


Cache_TTL = 60

class FileListing(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FileSerializer
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]
    queryset = Objects.objects.all()


    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print("Queries :", connection.queries)
        print("Queries count :", len(connection.queries))
        return response

    # List all files uploaded by all users from all departments.

    def get(self, request, *args, **kwargs):
        dept_choice = kwargs.get("dept")
        file_type = request.GET.get("type")
        user = request.user
        try:
            n = int(request.GET.get("recs", "0"))
        except ValueError:
            return Response(
                {"error": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return Response({"error": str(error)})

        if file_type == "owned":
            return self.get_files_owned_by_user(request, user)
        elif file_type == "received":
            return self.get_files_shared_to_user(request, user)
        elif file_type == "shared":
            return self.get_files_shared_by_user(request, user)
        else:
            return self.get_all_files(request, dept_choice, n)
            
    
    def get_all_files(self, request, dept_choice, n, *args, **kwargs):
        if dept_choice:
            try:
                dept = Departments.objects.get(name=dept_choice)

            except (Departments.DoesNotExist, ValueError, exceptions.ValidationError):
                return Response(
                    {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )
            
            self.queryset = (
                Objects.objects.select_related("owner")
                .prefetch_related(Prefetch('file_info', queryset=File_Info.objects.prefetch_related('depts')))
                .filter(owner__org=request.user.org, bucket_id="TwoKey",file_info__depts=dept.id)
                .exclude(name=".emptyFolderPlaceholder")
                .order_by("-created_at")
            )


        else:
            # print(FileSerializer(Objects.objects.prefetch_related().exclude(name=".emptyFolderPlaceholder"),many=True).data)
            # k = FileMetaSerializer(File_Info.objects.prefetch_related("depts").all(),many=True).data
            # print(k)
            self.queryset = (
                Objects.objects.select_related("owner")
                .prefetch_related(Prefetch('file_info', queryset=File_Info.objects.prefetch_related('depts')))
                .filter(owner__org=request.user.org, bucket_id="TwoKey")
                .exclude(name=".emptyFolderPlaceholder")
                .order_by("-created_at")
            )
        self.queryset = self.queryset[:n] if n >= 1 else self.queryset
        
        return self.list(request, *args, **kwargs)
    
    def get_files_owned_by_user(self, request, user):
        self.queryset = Objects.objects.select_related("owner").prefetch_related(Prefetch('file_info', queryset=File_Info.objects.prefetch_related('depts'))).select_related("owner__dept").filter(bucket_id="TwoKey",owner=user)
        return self.list(request)
    
    def get_files_shared_by_user(self, request, user):
        # Fetching files shared by user
        self.queryset = Objects.objects.prefetch_related(Prefetch('file_info', queryset=File_Info.objects.prefetch_related('depts'))).filter(sharedfiles__file__owner=user.id)
        return self.list(request)
    
    def get_files_shared_to_user(self, request, user):
        # Fetching files shared with the user
        self.queryset = Objects.objects.prefetch_related(Prefetch('file_info', queryset=File_Info.objects.prefetch_related('depts'))).filter(sharedfiles__shared_with=user)
        return self.list(request)

class AddDepartmentsToFileView(APIView):    
    permission_classes = [OthersPerm]
    def post(self, request, file):
           file_info = get_object_or_404(File_Info, file=file)
           serializer = AddDepartmentsSerializer(data=request.data)

           if serializer.is_valid():
               department_ids = serializer.validated_data.get('department_ids', [])

               # Validate that each department ID exists
               for department_id in department_ids:
                   get_object_or_404(Departments, id=department_id)

               # Check if departments are already associated and add only unique departments
               unique_department_ids = set(department_ids) - set(file_info.depts.values_list('id', flat=True))

               # Add the unique departments to the File_Info instance
               file_info.depts.add(*unique_department_ids)
               file_info.save()

               return Response({'detail': 'Departments added successfully'}, status=status.HTTP_200_OK)

           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
    queryset = SharedFiles.objects.select_related("file").select_related("file__owner").all()

    # def dispatch(self, request, *args, **kwargs):
    #     response = super().dispatch(request, *args, **kwargs)
    #     print("Queries :", connection.queries)
    #     print("Queries count :", len(connection.queries))
    #     return response

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
        shared_with = request.data["shared_with"]
        if type(file_ids) != list:
            return Response(
                {"error": "file should be a list"}, status=status.HTTP_400_BAD_REQUEST
            )
        if(len(shared_with)==0):
            return Response(
                {"error": " This field 'shared_with' required"}, status=status.HTTP_400_BAD_REQUEST
            )

        for file_id in file_ids:
            if self.check_file_ownership(request, file_id):
                request.data.pop("file")
                request.data["file"] = file_id
                for id in shared_with:
                    if(SharedFiles.objects.filter(file=file_id,shared_with__id=id)):
                        return Response({"error":f"File already shared with {id}"},status=status.HTTP_406_NOT_ACCEPTABLE)
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
        user = request.user
        self.lookup_field = "file"
        file = kwargs.get("file")

        cache_key = f"file_info_{file}"

        cache_data = cache.get(cache_key)
        if(cache_data):
            return Response(cache_data)
        self.queryset = SharedFiles.objects.filter(shared_with__id=user.id)
        res = self.retrieve(request,*args,**kwargs)
        cache.set(cache_key,res.data,timeout=3600*24*2)
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
        user = request.user
        org_id = user.org
        user_role = user.role_priv
        if user_role == "org_admin":
            return self.partial_update(request, **kwargs)
        elif self.check_file_ownership(request, file_id):
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

    # def dispatch(self, request, *args, **kwargs):
    #     response = super().dispatch(request, *args, **kwargs)
    #     print("Queries :", connection.queries)
    #     print("Queries count :", len(connection.queries))
    #     return response

    def retrieve(self, request, *args, **kwargs):
        # user = request.user
        # file_id = kwargs.get("file")
        
        instance = self.get_object()
        print(instance.security_check)
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
                return Response(
                    {"error": "wrong parameter value"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as error:
                return Response(
                    {"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
                )

    # Endpoint Serves recepient with the presigned url
    # - Adds an access log entry.
    def get_shared_file_url(self, request, *args, **kwargs):
        # Only files shared with the current user
        
        user = request.user
        user_role = user.role_priv
        user_org = user.org
        self.lookup_field = "file"
    

        if not self.check_file_ownership(request, kwargs.get("file")):
            if user_role == "org_admin":
                self.queryset = Objects.objects.select_related("owner").filter(
                    owner__org=user_org
                )
                objs = get_object_or_404(self.queryset, id=kwargs.get("file"))
                signed_url = create_signed(objs.name, 60)
                response = Response({"id": objs.id, "signed_url": signed_url})
            else:
                self.queryset = SharedFiles.objects.filter(
                    shared_with__id=request.user.id
                )
                response = self.retrieve(request, *args, **kwargs)

            
            if response.status_code == 200:
                
                file_id = kwargs.get("file")
                access_log_data = {
                    "user": user.id,
                    "username": user.username,
                    "user_email": user.email,
                    "profile_pic": user.profile_pic,
                    "file": uuid.UUID(file_id),
                    "file_name": Objects.objects.get(id=file_id).name,
                    "event": "file_access",
                    "org": user.org.id,
                }

                access_log_serializer = AccessLogSerializer(data=access_log_data)

                print(access_log_data)
                if access_log_serializer.is_valid():
                    print("HELLO")
                    access_log_serializer.save()
                    key1 = f"log_access_{file_id}"
                    key2 = f"log_all_{file_id}"
                    # Deleting and setting new access cache
                    cache.delete_many([key1,key2])

            
            return response
        else:
            self.queryset = Objects.objects.filter(owner=user)
            objs = get_object_or_404(self.queryset, id=kwargs.get("file"))
            signed_url = create_signed(objs.name, 60)
            return Response({"id": objs.id, "signed_url": signed_url})


class LoggingView(
    ExtraChecksMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = AccessLogSerializer
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]

    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print("Queries :", connection.queries)
        print("Queries count :", len(connection.queries))
        return response


    def event_log_handler(self, request, *args, **kwargs):
        # Only files shared with the current user
        user = request.user
        file_id = kwargs.get("file")
        allowed_events = ["screenshot", "download"]
        try:
            event = request.GET.get("event", "screenshot")
            if event not in allowed_events:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return Response({"error": str(error)})

        return self.create_log(request, user, event, *args, **kwargs)

    def create_log(self, request, user, event, *args, **kwargs):
        try:
            file_id = kwargs.get("file")
            shared = SharedFiles.objects.get(
                shared_with__id=request.user.id, file=file_id
            )

            access_log_data = {
                "user": user.id,
                "username": user.username,
                "user_email": user.email,
                "profile_pic":user.profile_pic,
                "file": uuid.UUID(file_id),
                "file_name": Objects.objects.get(id=file_id).name,
                "event": event,
                "org": user.org.id,
            }
            access_log_serializer = AccessLogSerializer(data=access_log_data)
            if access_log_serializer.is_valid():
                access_log_serializer.save()
            return Response(
                {"message": f"event logged successfully"},
                status=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationError:
            return Response(
                {"error": "wrong parameter value"}, status=status.HTTP_400_BAD_REQUEST
            )
        except SharedFiles.DoesNotExist:
            return Response(
                {"error": "invalid share"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Objects.DoesNotExist:
            return Response(
                {"error": "file does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the screen shot attempts for Current user's files
    def get_logs(self, request, *args, **kwargs):
        user = request.user
        event = kwargs.get("event")
        file = kwargs.get("file")

        # Get URL all parameters
        try:
            n = int(request.GET.get("recs", "0"))
            all_logs = int(request.GET.get("global", "1"))
        except ValueError:
            return Response(
                {"error": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return Response({"error": str(error)})

        # List of events
        all_events = ["access", "download", "screen"]

        # User activity logging system
        if event in all_events:
            event_filter = self.event_selector(event)
            if file:
                return self.handle_event_by_file(request, event_filter, file, n)
            else:
                return self.handle_event_all(request, event_filter, n)

        # The DUES logging  system
        elif event == "dues":
            return self.handle_due_event_all(user, n)

        # If now event is specified logs for all events:
        else:
            if file:
                return self.handle_all_by_file(request, user, file, n)
            else:
                return self.handle_all(request, user, n, all_logs)

    def event_selector(self, event_name):
        event_filter = {"include": {"event": []}, "exclude": {"event": []}}

        if event_name == "access":
            event_filter["include"]["event"].append("file_access")
        elif event_name == "download":
            event_filter["include"]["event"].append("download")
        elif event_name == "screen":
            event_filter["include"]["event"].append("screenshot")

        return event_filter

    def handle_event_by_file(self, request, event_filter, file, n):
        user = request.user
        user_org = user.org

        try:
            # Cache
            cache_key = f"log_{event_filter}_{file}"

            # Check if the data is already in the cache
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

            # If not in the cache, fetch the data from the database
            self.queryset = (
                AccessLog.objects.select_related("org")
                .filter(
                    file=file, org=user_org, event__in=event_filter["include"]["event"]
                )
                .order_by("-timestamp")
            )
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            response = self.list(request)

            # Cache the response with the custom cache key
            cache.set(cache_key, response.data, timeout=3600*24)

            return response

        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response(
                {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

    def handle_event_all(self, request, event_filter, n):
        user = request.user
        try:
            self.queryset = AccessLog.objects.filter(
                org=user.org, event__in=event_filter["include"]["event"]
            ).order_by("-timestamp")
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            return self.list(request)
        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response(
                {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

    def handle_due_event_all(self, user, n):
        self.serializer_class = SharedFileSerializer
        try:
            self.queryset = (
                SharedFiles.objects.select_related("file__owner__org")
                .filter(file__owner__org=user.org, state="due")
                .order_by("-last_modified_at")
            )
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            fields = ["file","file_name", "last_updated", "expiration_time", "shared_with"]
            serializer = self.get_serializer(
                self.queryset, many=True, context={"fields": fields}
            )
            return Response(serializer.data)
        except (SharedFiles.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response(
                {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

    def handle_all_by_file(self, request, user, file, n):
        # user_org = user.org
        try:
            cache_key = f"log_all_{file}"

            # Check if the data is already in the cache
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

            self.queryset = AccessLog.objects.filter(file=file)
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset

            response = self.list(request)
            cache.set(cache_key,response.data,timeout=3600*24)
            
            return response

        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response(
                {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

    def handle_all(self, request, user, n, all_logs):
        try:
            if all_logs == 0:
                self.queryset = AccessLog.objects.filter(user=user.id).order_by(
                    "-timestamp"
                )
            else:
                self.queryset = AccessLog.objects.filter(org=user.org).order_by(
                    "-timestamp"
                )
            self.lookup_field = "file"
            self.queryset = self.queryset[:n] if n >= 1 else self.queryset
            return self.list(request)
        except (AccessLog.DoesNotExist, exceptions.ValidationError, ValueError):
            return Response(
                {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )


# class SetDepartment(APIView):
#     def get(self,request):
#         for file_obj in Objects.objects.select_related("owner").all().exclude(name=".emptyFolderPlaceholder"):
#             temp = file_obj.metadata
#             temp.update({"department":file_obj.owner.dept.name})
#             file_obj.name = "test"
#             file_obj.save()
#             print(file_obj.id)
#             break
#         return Response("DONE!!")

class GeoLocationView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [OrgadminRequired]
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = AllowedLocationSerializer
    queryset = AllowedLocations.objects.all()
    lookup_field = "id"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print("Queries :", connection.queries)
        print("Queries count :", len(connection.queries))
        return response

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

    def update_location(self, request, **kwargs):
        user_org = request.user.org
        self.queryset = AllowedLocations.objects.filter(org=user_org)
        return self.update(request, **kwargs)

    def delete_location(self, request, **kwargs):
        user_org = request.user.org
        self.queryset = AllowedLocations.objects.filter(org=user_org)
        return self.destroy(request, **kwargs)

    def get_permissions(self):
        if self.action == "get_locations":
            self.permission_classes = [OthersPerm]
        return super().get_permissions()

