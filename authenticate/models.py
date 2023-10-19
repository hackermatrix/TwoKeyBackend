from django.db import models



class Users(models.Model):
    instance_id = models.UUIDField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)
    aud = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    encrypted_password = models.CharField(max_length=255, blank=True, null=True)
    email_confirmed_at = models.DateTimeField(blank=True, null=True)
    invited_at = models.DateTimeField(blank=True, null=True)
    confirmation_token = models.CharField(unique=True, max_length=255, blank=True, null=True)
    confirmation_sent_at = models.DateTimeField(blank=True, null=True)
    recovery_token = models.CharField(unique=True, max_length=255, blank=True, null=True)
    recovery_sent_at = models.DateTimeField(blank=True, null=True)
    email_change_token_new = models.CharField(unique=True, max_length=255, blank=True, null=True)
    email_change = models.CharField(max_length=255, blank=True, null=True)
    email_change_sent_at = models.DateTimeField(blank=True, null=True)
    last_sign_in_at = models.DateTimeField(blank=True, null=True)
    raw_app_meta_data = models.JSONField(blank=True, null=True)
    raw_user_meta_data = models.JSONField(blank=True, null=True)
    is_super_admin = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    phone = models.TextField(unique=True, blank=True, null=True)
    phone_confirmed_at = models.DateTimeField(blank=True, null=True)
    phone_change = models.TextField(blank=True, null=True)
    phone_change_token = models.CharField(max_length=255, blank=True, null=True)
    phone_change_sent_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    email_change_token_current = models.CharField(unique=True, max_length=255, blank=True, null=True)
    email_change_confirm_status = models.SmallIntegerField(blank=True, null=True)
    banned_until = models.DateTimeField(blank=True, null=True)
    reauthentication_token = models.CharField(unique=True, max_length=255, blank=True, null=True)
    reauthentication_sent_at = models.DateTimeField(blank=True, null=True)
    is_sso_user = models.BooleanField(db_comment='Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.')
    deleted_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'auth\".\"users'
        
        db_table_comment = 'Auth: Stores user login data within a secure schema.'