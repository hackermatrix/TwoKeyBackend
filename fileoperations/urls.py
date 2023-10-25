from django.urls import path,include
from .views import *
urlpatterns = [
    path('files/', FileListing.as_view(),name="Listing Org FIles "),
    # Shared File Operations:
    path('share_file/',ShareViewSet.as_view({'post':'share_file'}),name="Share a file to list of emails"),
    path('shared_file_info/<uuid:file>',ShareViewSet.as_view({'get':'get_file_info'}),name="Get info about a single file"),
    path('delete_share/<uuid:file>',ShareViewSet.as_view({'delete':'delete_share'}),name='Delete share')
]