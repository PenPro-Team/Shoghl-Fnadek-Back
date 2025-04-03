from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   # Add related_name attributes to avoid clashes with auth.User
   groups = models.ManyToManyField(
       'auth.Group',
       verbose_name='groups',
       blank=True,
       help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
       related_name='custom_user_set',
       related_query_name='custom_user'
   )
   user_permissions = models.ManyToManyField(
       'auth.Permission',
       verbose_name='user permissions',
       blank=True,
       help_text='Specific permissions for this user.',
       related_name='custom_user_set',
       related_query_name='custom_user'
   )
   username = models.CharField(max_length=150, unique=True, blank=True)
   first_name = models.CharField(max_length=30, blank=True)
   last_name = models.CharField(max_length=30, blank=True)
   email = models.EmailField(unique=True)
   phone_number = models.CharField(max_length=15, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   image = models.ImageField(blank=True, null=True)
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

   
   def __str__(self):
       return self.first_name + " " + self.last_name
