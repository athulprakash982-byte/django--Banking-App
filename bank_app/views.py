from django.shortcuts import render, redirect

# Create your views here.
from .models import User, Branch, Transaction
from decimal import Decimal


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
            
            # ALL passwords are hashed now - only use check_password
            if not user.check_password(password):
                return render(request, 'bank_app/login.html', {'error': 'Invalid credentials'})
            
            # Check approval status
            if user.role == 'customer' and user.status != 'approved':
                return render(request, 'bank_app/login.html', {
                    'error': 'Account pending approval. Please wait for branch manager approval.'
                })
            
            # Login successful
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            
            # Redirect based on role
            if user.role == 'super_user':
                return redirect('super_dashboard')
            elif user.role == 'branch_manager':
                return redirect('manager_dashboard')
            else:
                return redirect('customer_dashboard')
                
        except User.DoesNotExist:
            return render(request, 'bank_app/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'bank_app/login.html')

def super_dashboard(request):
    return render(request, 'bank_app/super_dash.html')





def manager_dashboard(request):
    user_id = request.session.get('user_id')
    manager = User.objects.get(id=user_id)
    
    # Get pending customers for approval
    pending_customers = User.objects.filter(
        branch=manager.branch, 
        role='customer',
        status='pending'
    )
    
    # Get approved customers
    approved_customers = User.objects.filter(
        branch=manager.branch, 
        role='customer',
        status='approved'
    )
    
    return render(request, 'bank_app/manager_dash.html', {
        'manager': manager,
        'pending_customers': pending_customers,
        'approved_customers': approved_customers
    })




def customer_dashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    return render(request, 'bank_app/user_dash.html', {'user': user})




def logout_view(request):
    request.session.flush()
    return redirect('login')




import random

def profile_update(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        contact_number = request.POST.get('contact_number')

        # Check if both fields are provided
        if full_name and contact_number:
            otp = '123456'
            request.session['otp'] = otp
            request.session['new_name'] = full_name
            request.session['new_contact'] = contact_number

            return render(request, 'bank_app/otp_verify.html', {'user': user})
        else:
            # If fields missing, show error
            return render(request, 'bank_app/profile_update.html', {
                'user': user,
                'error': 'Please fill in all fields.'
            })

    return render(request, 'bank_app/profile_update.html', {'user': user})





def verify_otp(request):
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')
        
        print(f"Debug: Entered OTP: {entered_otp}, Saved OTP: {saved_otp}")  # Debug line
        
        if entered_otp == saved_otp:
            # OTP verified - update user info
            user = User.objects.get(id=user_id)
            new_name = request.session.get('new_name')
            new_contact = request.session.get('new_contact')
            
            print(f"Debug: Updating user {user.username} to {new_name}, {new_contact}")  # Debug line
            
            # Update the user
            user.full_name = new_name
            user.contact_number = new_contact
            user.save()
            
            print(f"Debug: User saved successfully! New name: {user.full_name}")  # Debug line
            
            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('new_name', None)
            request.session.pop('new_contact', None)
            
            return redirect('customer_dashboard')
        else:
            user = User.objects.get(id=user_id)
            return render(request, 'bank_app/otp_verify.html', {
                'user': user, 
                'error': 'Invalid OTP. Please try again.'
            })
    
    # If not POST, show OTP form
    user = User.objects.get(id=user_id)
    return render(request, 'bank_app/otp_verify.html', {'user': user})





def approve_customer(request, customer_id):
    if request.method == 'POST':
        manager_id = request.session.get('user_id')
        manager = User.objects.get(id=manager_id)
        customer = User.objects.get(id=customer_id)
        
        # Check if customer belongs to manager's branch
        if customer.branch == manager.branch:
            customer.status = 'approved'
            customer.save()
        
        return redirect('manager_dashboard')




def reject_customer(request, customer_id):
    if request.method == 'POST':
        customer = User.objects.get(id=customer_id)
        customer.status = 'rejected'
        customer.save()
        return redirect('manager_dashboard')
    


def customer_registration(request):
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        full_name = request.POST['full_name']
        contact_number = request.POST['contact_number']
        branch_id = request.POST['branch']
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            return render(request, 'bank_app/registration.html', {
                'branches': branches,
                'error': 'Username already exists. Please choose a different username.'
            })
        
        try:
            branch = Branch.objects.get(id=branch_id)
            user = User(
                username=username,
                role="customer",
                branch=branch,
                full_name=full_name,
                contact_number=contact_number,
                status="pending"
            )

            user.set_password(password)
            user.save()
            
            # REDIRECT instead of render to prevent form resubmission
            return redirect('registration_success')
            
        except Exception as e:
            return render(request, 'bank_app/registration.html', {
                'branches': branches,
                'error': 'An error occurred. Please try again.'
            })
    
    return render(request, 'bank_app/registration.html', {'branches': branches})




def deposit(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        user.balance += amount
        user.save()
        
        Transaction.objects.create(
            user=user,
            transaction_type='deposit',
            amount=amount,
            description=f"Cash deposit"
        )
        return redirect('customer_dashboard')
    
    return render(request, 'bank_app/deposit.html', {'user': user})




def withdraw(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        if user.balance >= amount:
            user.balance -= amount
            user.save()
            
            Transaction.objects.create(
                user=user,
                transaction_type='withdraw',
                amount=amount,
                description=f"Cash withdrawal"
            )
            return redirect('customer_dashboard')
        else:
            return render(request, 'bank_app/withdraw.html', {
                'user': user,
                'error': 'Insufficient balance'
            })
    
    return render(request, 'bank_app/withdraw.html', {'user': user})




def create_branch(request):
    # Check if user is super_user
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    if user.role != 'super_user':
        return redirect('customer_dashboard')  # Or show error
    
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        
        Branch.objects.create(
            name=name,
            address=address
        )
        return redirect('super_dashboard')
    
    return render(request, 'bank_app/create_branch.html')



def super_dashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    branches = Branch.objects.all()

    # Get pending manager approvals
    pending_managers = User.objects.filter(
        role='branch_manager', 
        status='pending_manager'
    )
    
    return render(request, 'bank_app/super_dash.html', {
        'user': user,
        'branches': branches,
        'pending_managers':pending_managers
    })



def delete_branch(request, branch_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    if user.role != 'super_user':
        return redirect('customer_dashboard')
    
    branch = Branch.objects.get(id=branch_id)
    branch.delete()
    return redirect('super_dashboard')




def manager_registration(request):
    # Get branches that have ANY branch managers (approved OR pending)
    occupied_branches = User.objects.filter(
        role='branch_manager'
    ).exclude(branch__isnull=True).values_list('branch_id', flat=True)
    
    available_branches = Branch.objects.exclude(id__in=occupied_branches)

    print(f"Occupied branches: {list(occupied_branches)}")  # Debug
    print(f"Available branches: {list(available_branches)}")  # Debug
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        full_name = request.POST['full_name']
        contact_number = request.POST['contact_number']
        branch_id = request.POST['branch']
        
        branch = Branch.objects.get(id=branch_id)
        User.objects.create(
            username=username,
            password=password,
            role='branch_manager',
            branch=branch,
            full_name=full_name,
            contact_number=contact_number,
            status='pending_manager'  # Special status for manager approval
        )
        
        return render(request, 'bank_app/registration_success.html', {
            'message': 'Branch Manager registration submitted for Super User approval.'
        })
    
    return render(request, 'bank_app/manager_registration.html', {
        'branches': available_branches
    })

def approve_manager(request, manager_id):
    if request.method == 'POST':
        manager = User.objects.get(id=manager_id)
        manager.status = 'approved'
        manager.save()
        return redirect('super_dashboard')

def reject_manager(request, manager_id):
    if request.method == 'POST':
        manager = User.objects.get(id=manager_id)
        manager.status = 'rejected'
        manager.save()
        return redirect('super_dashboard')
    
def registration_success(request):
    return render(request, 'bank_app/registration_success.html')




def delete_customer(request, customer_id):
    if request.method == 'POST':
        manager_id = request.session.get('user_id')
        manager = User.objects.get(id=manager_id)
        customer = User.objects.get(id=customer_id)
        
        # Security check: Ensure customer belongs to manager's branch
        if customer.branch == manager.branch and customer.role == 'customer':
            customer.delete()
        
        return redirect('manager_dashboard')
                                                    




    