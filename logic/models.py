from django.db import models

# Create your models here.
import uuid
from django.db import models

class Organizations(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    name = models.CharField(blank=True, null=True,unique=True)

    class Meta:
        managed = True
        db_table = 'organizations'

class Departments(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    name = models.CharField(blank=True, null=True)
    org = models.ForeignKey(Organizations,on_delete=models.CASCADE,default=None)

    class Meta:
        managed = True
        db_table = 'departments'


class UserInfo(models.Model):
    # Personal Info
    id = models.UUIDField(primary_key=True)
    username = models.CharField(default='',null=True)
    name =models.CharField(default='')
    last_name = models.CharField(default='')
    email = models.EmailField(default=None)
    phone = models.BigIntegerField(default=None,null=True)
    # Work Info
    org = models.ForeignKey(Organizations, on_delete=models.CASCADE,default=None)
    role_priv = models.CharField(max_length=20,default="employee")
    dept = models.ForeignKey(Departments, models.DO_NOTHING,default=None)
    # Address Info
    country = models.CharField(max_length=30,default='')
    state = models.CharField(max_length=30,default='')
    city = models.CharField(max_length=30,default='')
    postal_code = models.IntegerField(default=None,null=True)

    is_approved = models.BooleanField(default=False)
    is_authenticated = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'user_info'


class Role(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    role = models.CharField(max_length=20)

    class Meta:
        db_table = 'user_roles'
