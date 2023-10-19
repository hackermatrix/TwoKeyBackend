import uuid
from django.db import models

class Organizations(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organizations'

class Departments(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    name = models.CharField(blank=True, null=True)
    org = models.ForeignKey(Organizations,on_delete=models.CASCADE,default=None)

    class Meta:
        managed = True
        db_table = 'departments'

# class OrgAdmins(models.Model):
#     id = models.UUIDField(primary_key=True)
#     org = models.ForeignKey(Organizations, models.DO_NOTHING)
#     is_authenticated = models.BooleanField(default=False)
#     class Meta:
#         db_table = 'org_admins'

class UserInfo(models.Model):
    id = models.UUIDField(primary_key=True)
    org = models.ForeignKey(Organizations, models.DO_NOTHING)
    role_priv = models.CharField(max_length=20,default="employee")
    dept = models.ForeignKey(Departments, models.DO_NOTHING)
    is_authenticated = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user_info'
