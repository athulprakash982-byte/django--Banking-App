from django.urls import path
from . import views

urlname = 'bank_app'

urlpatterns = [
    path('', views.index, name='index'), 
    path('login/', views.login_view, name='login'),

    path('super-dashboard/', views.super_dashboard, name='super_dashboard'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),

    path('logout/', views.logout_view, name='logout'),

    path('profile-update/', views.profile_update, name='profile_update'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('approve-customer/<int:customer_id>/', views.approve_customer, name='approve_customer'),
    path('reject-customer/<int:customer_id>/', views.reject_customer, name='reject_customer'),

    path('register/', views.customer_registration, name='register'),

    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),

    path('create-branch/', views.create_branch, name='create_branch'),
    path('delete-branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),

    path('register-manager/', views.manager_registration, name='register_manager'),
    path('approve-manager/<int:manager_id>/', views.approve_manager, name='approve_manager'),
    path('reject-manager/<int:manager_id>/', views.reject_manager, name='reject_manager'),

    path('registration-success/', views.registration_success, name='registration_success'),

    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),

    
]