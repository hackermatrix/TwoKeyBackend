from backend import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from backend.custom_perm_classes import *
from rest_framework.permissions import IsAuthenticated
from fileoperations.serializers import FileSerializer, SharedFileSerializer, SharedFilesRecepient
from supabase import create_client, Client
from decouple import config
from rest_framework.response import Response
from rest_framework import mixins
from backend.supabase_auth import SupabaseAuthBackend
from rest_framework import generics
from .models import *
from rest_framework import status


class FileListing(mixins.ListModelMixin
               ,generics.GenericAPIView):
    
    serializer_class= FileSerializer
    authentication_classes = [SupabaseAuthBackend]
    permission_classes = [OthersPerm]
    queryset = Objects.objects.all()

    # List all files uploaded by all users from all departments. 
    def get(self,request,*args,**kwargs):
        self.queryset = Objects.objects.prefetch_related('owner').filter(owner__org=request.user.org).exclude(name='.emptyFolderPlaceholder')
        return self.list(request,*args,**kwargs)
    


class FileOwnershipMixin:
    # Check if the user creating or deleting a share is the owner of the file
    def check_file_ownership(self, request, file_id):
        try:
            file_object = Objects.objects.get(id=file_id)
            file_owner = file_object.owner
        except Objects.DoesNotExist:
            return Response({'error': "File not found"}, status=status.HTTP_400_BAD_REQUEST)
        current_user = request.user
        if current_user == file_owner:
            return True
        return False
    
#  Below are the endpoints used at the Sender's side.
class ShareViewSetSender(FileOwnershipMixin,
                          mixins.RetrieveModelMixin, 
                          mixins.CreateModelMixin, 
                          mixins.DestroyModelMixin, 
                          mixins.UpdateModelMixin,
                          GenericViewSet):
    authentication_classes = [SupabaseAuthBackend]
    serializer_class = SharedFileSerializer
    permission_classes = [OthersPerm]
    queryset = SharedFiles.objects.all()

    # Create a file share for a list of Emails
    def create(self, request, *args, **kwargs):
        file_id = kwargs.get('file')
        if self.check_file_ownership(request, file_id):
            return super().create(request, *args, **kwargs)
        else:
            return Response({'error': "You cannot share this file"}, status=status.HTTP_403_FORBIDDEN)

    # Delete a file share if the user is the owner of the file
    def destroy(self, request, *args, **kwargs):
        file_id = kwargs.get('file')
        if self.check_file_ownership(request, file_id):
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': "You cannot delete this share"}, status=status.HTTP_403_FORBIDDEN)

    # Share a file (alias for create)
    #Create a file share for list of UUIDs. 
    # - Only Single file sharing availabe as of now 
    # - Assigns a presigned url to the share as in the expiration_time parameter.
    # - Security Features not yet added.
    def share_file(self, request):
        return self.create(request)
    

    # Get information about the shared file, including its name, id, and the list of users it's shared with
    # Returns Information about the Shared file given
    #  - file_name
    #  - file_id
    #  - Shared_with list
    def get_file_info(self, request, *args, **kwargs):
        self.lookup_field = 'file'
        pk = kwargs.get('file')
        res = self.retrieve(request)
        return res

    # Delete All share of a file 
    # User file ownership check added already
    def delete_share(self, request, *args, **kwargs):
        self.lookup_field = 'file'
        pk = kwargs.get('file')
        return self.destroy(request)

    # Remove access for a single user (not implemented yet)
    def edit_access(self, request,**kwargs):
        file_id = kwargs.get('file')
        self.lookup_field = 'file'
        if(self.check_file_ownership(request,file_id)):
            return self.partial_update(request,**kwargs)
        else:
            return Response({"error":"You cannot modify this share"},status=status.HTTP_401_UNAUTHORIZED)

# Below will be used at recepient's end

class ShareViewSetReceiver(mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    
    serializer_class = SharedFilesRecepient
    authentication_classes=[SupabaseAuthBackend]
    permission_classes = [OthersPerm]


    # Endpoint Serves recepient with the presigned url 
    # - Adds an access log entry.
    def get_shared_file_url(self, request, *args, **kwargs):
        # Only files shared with current user
        self.queryset = SharedFiles.objects.filter(shared_with__id=request.user.id)
        self.lookup_field = 'file'
        res = self.retrieve(request,*args,**kwargs)
        return res



        


