from rest_framework.viewsets import GenericViewSet
from backend.custom_perm_classes import *
from rest_framework.permissions import IsAuthenticated

class FileViewset(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def upload_file(self,request):
        pass