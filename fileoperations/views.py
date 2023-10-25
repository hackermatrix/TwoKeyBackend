from backend import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from backend.custom_perm_classes import *
from rest_framework.permissions import IsAuthenticated
from fileoperations.serializers import FileSerializer, SharedFileSerializer
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
        print(self.queryset)
        return self.list(request,*args,**kwargs)
    


class ShareViewSet(mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    authentication_classes=[SupabaseAuthBackend]
    serializer_class = SharedFileSerializer

    permission_classes = [OthersPerm]
    queryset = SharedFiles.objects.all()

    def create(self, request, *args, **kwargs):
        current_user = request.user
        file_id = request.data.get('file')
        try:
            file_object = Objects.objects.get(id=file_id)
            file_owner = file_object.owner
        except Objects.DoesNotExist:
            return Response({'error': "File not found"}, status=status.HTTP_400_BAD_REQUEST)
        if current_user == file_owner:
            return super().create(request, *args, **kwargs)
        else:
            return Response({'error': "You cannot share this file"}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        current_user = request.user
        file_id = request.data.get('file')
        try:
            file_object = Objects.objects.get(id=file_id)
            file_owner = file_object.owner
        except Objects.DoesNotExist:
            return Response({'error': "File not found"}, status=status.HTTP_400_BAD_REQUEST)
        if current_user == file_owner:
            return super().create(request, *args, **kwargs)
        else:
            return Response({'error': "You cannot delete this share"}, status=status.HTTP_403_FORBIDDEN)
    

        return super().destroy(request, *args, **kwargs)
            
    #Create a file share for list of Emails. 
    # - Only Single file sharing availabe as of now 
    def share_file(self,request):
        return self.create(request)
    

    
    # Returns Information about the Shared file given
    #  - file_name
    #  - file_id
    #  - Shared_with list
    def get_file_info(self,request,*args,**kwargs):
        self.lookup_field = 'file'
        pk = kwargs.get('file')
        res = self.retrieve(request)
        return res
    
    # Delete All share of a file 
    def delete_share(self,request,*args,**kwargs):
        self.lookup_field = 'file'
        pk = kwargs.get('file')
        return self.destroy(request)
        


