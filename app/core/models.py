"""
Database Model
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, #functionally for authetication
    BaseUserManager,
    PermissionsMixin  #functionallity for permissions,fields
)


class UsersManager(BaseUserManager):
    """Manager for users"""

    def create_user(self,email, password=None, **extra_field):
        """create, save and return new user"""

        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser"""

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User (AbstractBaseUser, PermissionsMixin):
    """Users in the systemUSERNAME_FIELD."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsersManager()
    USERNAME_FIELD = 'email'  #field will be used for authenticaiton