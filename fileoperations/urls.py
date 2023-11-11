from django.urls import path,include, re_path
from .views import *
from django.urls import path
from .views import FileListing, ShareViewSetSender, ShareViewSetReceiver

urlpatterns = [
    # File Listing and Operations
    re_path(r'files/?', FileListing.as_view(), name="fileListing"),
    
    # Shared File Operations
    re_path(r'shareFile/?', ShareViewSetSender.as_view({'post': 'share_file'}), name="shareFile"),
    re_path(r'sharedFileInfo/<uuid:file>/?', ShareViewSetSender.as_view({'get': 'get_file_info'}), name="sharedFileInfo"),
    re_path(r'deleteShare/<uuid:file>/?', ShareViewSetSender.as_view({'delete': 'delete_share'}), name='deleteShare'),
    re_path(r'editShare/<uuid:file>/?',ShareViewSetSender.as_view({'put':'edit_access'}),name="Edit shared user"),
    
    # Get a Presigned URL for a Shared File
    re_path(r'getPresigned/<uuid:file>/?', ShareViewSetReceiver.as_view({'post': 'get_shared_file_url'}), name="getPresignedUrl"),

    # Store ScreenShot Attempt
    re_path(r'screenShotAlert/?',ShareViewSetReceiver.as_view({'post':'screen_shot_alert'}),name="ScreenShot Alert"),
    re_path(r'getLogs/(?P<event>[\w-]*)/(?P<file>[\w-]*)/?',ShareViewSetReceiver.as_view({'get':'get_logs'}),name="Get logs"),

    # GeoLocation Endpoints
    re_path(r'createLocation/?',GeoLocationView.as_view({'post':'create_location'}),name="Creating an allowed location"),
    re_path(r'listLocation/?',GeoLocationView.as_view({"get":"get_locations"}),name="List all the allowed locations"),
]
