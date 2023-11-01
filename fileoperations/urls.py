from django.urls import path,include, re_path
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
    path('editShareUsers/<uuid:file>/',ShareViewSetSender.as_view({'put':'edit_access'}),name="Edit shared user"),
    
    # Get a Presigned URL for a Shared File
    path('getPresigned/<uuid:file>/', ShareViewSetReceiver.as_view({'post': 'get_shared_file_url'}), name="getPresignedUrl"),

    # Store ScreenShot Attempt
    path('screenShotAlert/',ShareViewSetReceiver.as_view({'post':'screen_shot_alert'}),name="ScreenShot Alert"),
    path('getScreenShotLogs/',ShareViewSetReceiver.as_view({'get':'get_screenshot_logs'}),name="Get Screen Shot logs"),

    # GeoLocation Endpoints
    path('createLocation/',GeoLocationView.as_view({'post':'create_location'}),name="Creating an allowed location"),
    path('listLocation/',GeoLocationView.as_view({"get":"get_locations"}),name="List all the allowed locations"),
]
