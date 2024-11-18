from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom manager for handling user creation
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, department=None, manager=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, department=department, manager=manager, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('designation', 'Admin')  # Automatically set to Admin for superusers
        return self.create_user(username, email, password, **extra_fields)
    

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, choices=[
        ('IT', 'IT'),
        ('Sales', 'Sales'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    ], unique=True)

    def __str__(self):
        return self.name


# Custom User model
class CustomUser(AbstractUser):
    DESIGNATION_CHOICES = [
        ('Employee', 'Employee'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),  # Add Admin option for clarity
    ]
    designation = models.CharField(max_length=100, choices=DESIGNATION_CHOICES, default='Employee')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Add phone number field
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    is_active = models.BooleanField(default=True)  
    is_admin = models.BooleanField(default=False) 
    is_employee = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    leave_balance = models.IntegerField(default=0) 

    # Use the CustomUserManager for creating users
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # If the user is a superuser, set the designation to "Admin"
        if self.is_superuser and not self.designation:
            self.designation = 'Admin'
        super().save(*args, **kwargs)
