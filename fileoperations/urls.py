from django.urls import path,include
from .views import *
urlpatterns = [
    path('files/', FileListing.as_view(),name="Listing Org FIles ")
]