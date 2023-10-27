from django.urls import path,include
from .views import *
from django.urls import path
from .views import FileListing, ShareViewSetSender, ShareViewSetReceiver

urlpatterns = [
    # File Listing and Operations
    path('files/', FileListing.as_view(), name="fileListing"),
    
    # Shared File Operations
    path('shareFile/', ShareViewSetSender.as_view({'post': 'share_file'}), name="shareFile"),
    path('sharedFileInfo/<uuid:file>/', ShareViewSetSender.as_view({'get': 'get_file_info'}), name="sharedFileInfo"),
    path('deleteShare/<uuid:file>/', ShareViewSetSender.as_view({'delete': 'delete_share'}), name='deleteShare'),
    path('editShareUsers/<uuid:file>',ShareViewSetSender.as_view({'put':'edit_access'}),name="Edit shared user"),
    
    # Get a Presigned URL for a Shared File
    path('getPresigned/<uuid:file>/', ShareViewSetReceiver.as_view({'get': 'get_shared_file_url'}), name="getPresignedUrl")
]
