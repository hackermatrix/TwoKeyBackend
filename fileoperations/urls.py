from django.urls import path,include, re_path
from .views import *
from django.urls import path
from .views import FileListing, ShareViewSetSender, ShareViewSetReceiver

urlpatterns = [
    # File Listing and Operations
    re_path(r'files/?(?P<dept>[\w-]*)', FileListing.as_view(), name="fileListing"),
    re_path(r'addDepartment/(?P<file>[\w-]*)', AddDepartmentsToFileView.as_view(), name='add_departments_to_file'),
    
    # Shared File Operations
    re_path(r'shareFile', ShareViewSetSender.as_view({'post': 'share_file'}), name="shareFile"),
    re_path(r'sharedFileInfo/(?P<file>[\w-]*)', ShareViewSetSender.as_view({'get': 'get_file_info'}), name="sharedFileInfo"),
    re_path(r'deleteShare/(?P<file>[\w-]*)', ShareViewSetSender.as_view({'delete': 'delete_share'}), name='deleteShare'),
    re_path(r'editShare/(?P<file>[\w-]*)',ShareViewSetSender.as_view({'put':'edit_access'}),name="Edit shared user"),
    
    # Get a Presigned URL for a Shared File
    re_path(r'getPresigned/(?P<file>[\w-]*)', ShareViewSetReceiver.as_view({'post': 'get_shared_file_url'}), name="getPresignedUrl"),

    # Store ScreenShot Attempt
    re_path(r'logEvent/(?P<file>[\w-]*)',LoggingView.as_view({'get':'event_log_handler'}),name="Create Logs"),
    re_path(r'getLogs/?(?:(?P<event>[\w-]*)/)?(?P<file>[\w-]*)',LoggingView.as_view({'get':'get_logs'}),name="Get logs"),

    # GeoLocation Endpoints
    re_path(r'createLocation',GeoLocationView.as_view({'post':'create_location'}),name="Creating an allowed location"),
    re_path(r'listLocation',GeoLocationView.as_view({"get":"get_locations"}),name="List all the allowed locations"),
    re_path(r'deleteLocation/(?P<id>[\w-]*)',GeoLocationView.as_view({"delete":"delete_location"}),name="Delete locations"),
    re_path(r'updateLocation/(?P<id>[\w-]*)',GeoLocationView.as_view({"put":"update_location"}),name="Update locations"),

    # path('test',SetDepartment.as_view(),name="DELETE This ENDPT")
]
