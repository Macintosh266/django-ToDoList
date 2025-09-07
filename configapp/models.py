from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import re
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self,username,password=None,**extra_fields):
        if not username:
            return  ValueError('User kiritish shart!')
        user=self.model(username=username,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,username,password,**extra_fields):
        extra_fields.setdefault('is_admin',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_admin') is not True:
            return ValueError("Sizda is_admin==True b'olishi kerak")
        if extra_fields.get('is_active') is not True:
            return ValueError()

        return  self.create_user(username,password,**extra_fields)

class User(AbstractBaseUser,PermissionsMixin):
    username=models.CharField(max_length=15,unique=True)
    email = models.CharField(max_length=50, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects=CustomUserManager()

    USERNAME_FIELD='username'
    REQUIRED_FIELDS = []




    def __str__(self):
        return self.username

    @property
    def is_superuser(self):
        return self.is_admin



    
class ToDoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


import random

class PhoneMassage(models.Model):
    phone=models.CharField(max_length=15,unique=True)
    time_password = models.CharField(max_length=5)
    is_bool = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone} - {self.is_bool}"
    
    def clean(self):
        super().clean()
        if self.phone and not re.match(r'^\+?\d{9,15}$', self.phone):
            raise ValidationError({'phone': 'Telefon raqami noto‘g‘ri formatda. Masalan: +998901234567'})

    def set_reset_code(self):
        code = str(random.randint(10000, 99999))
        self.time_password = code
        self.save()
        return code
