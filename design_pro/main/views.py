from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, RequestForm, StatusChangeForm, CategoryForm
from .models import Request, Category


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def home_view(request):
    completed_requests = Request.objects.filter(status='Выполнено').order_by('-created_at')[:4]
    accepted_requests_count = Request.objects.filter(status='Принято в работу').count()
    return render(request, 'home.html', {
        'completed_requests': completed_requests,
        'accepted_requests_count': accepted_requests_count
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home')

@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_instanse = form.save(commit=False)
            request_instanse.user = request.user
            request_instanse.save()
            messages.success(request, 'Request created successfully.')
            return redirect('view_requests')
    else:
        form = RequestForm()
    return render(request, 'create_request.html', {'form': form})

@login_required
def view_requests(request):
    requests = Request.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'view_requests.html', {'requests': requests})

@login_required
def delete_request(request, request_id):
    request_instance = get_object_or_404(Request, id=request_id, user=request.user)
    if request_instance.status == 'Новая':
        request_instance.delete()
        messages.success(request, 'Request deleted successfully.')
    else:
        messages.error(request, 'Cannot delete a request that is not in "New" status.')
    return redirect('view_requests')

@login_required
def change_status(request, request_id):
    request_instance = get_object_or_404(Request, id=request_id)
    if request.user.is_superuser:
        if request.method == 'POST':
            form = StatusChangeForm(request.POST, instance=request_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Status changed successfully.')
                return redirect('view_all_requests')
        else:
            form = StatusChangeForm(instance=request_instance)
        return render(request, 'change_status.html', {'form': form, 'request': request_instance})
    else:
        messages.error(request, 'You do not have permission to change the status of this request.')
        return redirect('view_requests')

@login_required
def view_all_requests(request):
    if request.user.is_superuser:
        requests = Request.objects.all().order_by('-created_at')
        return render(request, 'view_all_requests.html', {'requests': requests})
    else:
        messages.error(request, 'You do not have permission to view all requests.')
        return redirect('view_requests')

@login_required
def create_category(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category created successfully.')
                return redirect('view_categories')
        else:
            form = CategoryForm()
        return render(request, 'create_category.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to create a category.')
        return redirect('home')

@login_required
def view_categories(request):
    if request.user.is_superuser:
        categories = Category.objects.all().order_by('name')
        return render(request, 'view_categories.html', {'categories': categories})
    else:
        messages.error(request, 'You do not have permission to view categories.')
        return redirect('home')

@login_required
def edit_category(request, category_id):
    if request.user.is_superuser:
        category = get_object_or_404(Category, id=category_id)
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully.')
                return redirect('view_categories')
        else:
            form = CategoryForm(instance=category)
        return render(request, 'edit_category.html', {'form': form, 'category': category})
    else:
        messages.error(request, 'You do not have permission to edit this category.')
        return redirect('view_categories')

@login_required
def delete_category(request, category_id):
    if request.user.is_superuser:
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('view_categories')
    else:
        messages.error(request, 'You do not have permission to delete this category.')
        return redirect('view_categories')