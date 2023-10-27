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
    owner = models.ForeignKey(UserInfo,on_delete=models.SET_NULL,blank=True, null=True,db_column='owner')
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
class SharedFiles(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    file = models.OneToOneField(Objects, on_delete=models.CASCADE)
    # file_owner = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(UserInfo, related_name='shared_files')
    expiration_time = models.BigIntegerField(default=0)
    last_modified_at = models.DateTimeField(default=timezone.now)
    signed_url = models.URLField(default="")
    download_allowed = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'shared_files'