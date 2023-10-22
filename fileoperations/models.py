from django.db import models
from authenticate.models import Users
from logic.models import UserInfo , Organizations, Departments
from django.utils import timezone
from uuid import uuid4

# Non Managed

class Buckets(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(unique=True)
    owner = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    public = models.BooleanField(blank=True, null=True)
    avif_autodetection = models.BooleanField(blank=True, null=True)
    file_size_limit = models.BigIntegerField(blank=True, null=True)
    allowed_mime_types = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'storage"."buckets'



class Objects(models.Model):
    id = models.UUIDField(primary_key=True)
    bucket = models.ForeignKey(Buckets, models.DO_NOTHING, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(UserInfo,on_delete=models.SET_NULL,blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    last_accessed_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    path_tokens = models.TextField(blank=True, null=True)  # This field type is a guess.
    version = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'storage"."objects'
        unique_together = (('bucket', 'name'),)



# managed
# class UserFiles(models.Model):
#     id = models.UUIDField(primary_key=True,default=uuid4)
#     owner = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
#     file_name = models.CharField(max_length=255)
#     file_key = models.CharField(max_length=255)
#     file_size = models.BigIntegerField(default=0)
#     file_type = models.CharField(max_length=50)
#     org = models.ForeignKey(Organizations,on_delete=models.CASCADE)
#     dept = models.ForeignKey(Departments,on_delete=models.SET_NULL,null=True)
#     uploaded_at = models.DateTimeField(default=timezone.now)  

#     class Meta:
#         db_table = 'user_files'

#     def __str__(self):
#         return (f"{self.FileID} - {self.FileName}")