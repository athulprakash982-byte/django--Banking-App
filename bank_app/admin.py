from django.contrib import admin

# Register your models here.
from .models import Branch, User, Transaction

admin.site.register(Branch)
admin.site.register(User)
admin.site.register(Transaction)