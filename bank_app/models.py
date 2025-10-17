from django.db import models
from django.contrib.auth.hashers import make_password,check_password

# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    
    def __str__(self):
        return self.name

class User(models.Model):
    ROLE_CHOICES = [
        ('super_user', 'Super User'),
        ('branch_manager', 'Branch Manager'),
        ('customer', 'Customer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_manager', 'Pending Manager Approval'),
    ]
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

