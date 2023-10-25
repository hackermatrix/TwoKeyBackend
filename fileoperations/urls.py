from django.urls import path,include
from .views import *
urlpatterns = [
    path('files/', FileListing.as_view(),name="Listing Org FIles "),
    # Shared File Operations:
    path('share_file/',ShareViewSetSender.as_view({'post':'share_file'}),name="Share a file to list of emails"),
    path('shared_file_info/<uuid:file>',ShareViewSetSender.as_view({'get':'get_file_info'}),name="Get info about a single file"),
    path('delete_share/<uuid:file>',ShareViewSetSender.as_view({'delete':'delete_share'}),name='Delete share'),
    path('get_presigned/<uuid:file>',ShareViewSetReceiver.as_view({'get':'get_shared_file_url'}),name="get_shared_file_url")
]