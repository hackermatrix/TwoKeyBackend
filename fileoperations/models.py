from django.db import models
from logic.models import UserInfo , Organizations, Departments
from django.utils import timezone
from uuid import uuid4

class UserFiles(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    owner = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_key = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50)
    org = models.ForeignKey(Organizations,on_delete=models.CASCADE)
    dept = models.ForeignKey(Departments,on_delete=models.SET_NULL,null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)  

    class Meta:
        db_table = 'user_files'

    def __str__(self):
        return (f"{self.FileID} - {self.FileName}")